from fastapi import FastAPI, File, UploadFile, Form, HTTPException, Depends
from sqlalchemy.orm import Session
import os
import uuid
import shutil

from database import SessionLocal, AnalysisRequest, AnalysisResult, create_db_and_tables, get_db
from worker import run_analysis_crew
from celery.result import AsyncResult
from celery_config import celery_app

# Create the database and tables on startup
create_db_and_tables()

app = FastAPI(title="Blood Test Report Analyser")

@app.get("/")
async def root():
    """Health check endpoint"""
    return {"message": "Blood Test Report Analyser API is running"}

@app.post("/analyze")
async def analyze_blood_report(
    db: Session = Depends(get_db),
    file: UploadFile = File(...),
    query: str = Form(default="Summarise my Blood Test Report")
):
    """
    Accepts a PDF blood report and a query, saves them,
    and dispatches the analysis task to a background worker.
    """
    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Invalid file type. Please upload a PDF.")

    # Generate unique filename to avoid conflicts and save the file
    upload_dir = "data/uploads"
    os.makedirs(upload_dir, exist_ok=True)
    file_id = str(uuid.uuid4())
    file_path = os.path.join(upload_dir, f"{file_id}_{file.filename}")
    
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # Create a request record in the database
    new_request = AnalysisRequest(
        query=query.strip(),
        file_path=file_path
    )
    db.add(new_request)
    db.commit()
    db.refresh(new_request)

    # Dispatch the background task
    task = run_analysis_crew.delay(new_request.id)

    return {
        "status": "success",
        "message": "Analysis task has been submitted.",
        "task_id": task.id
    }

@app.get("/results/{task_id}")
async def get_analysis_result(task_id: str, db: Session = Depends(get_db)):
    """
    Retrieves the status and result of an analysis task.
    """
    # Check our database first
    request = db.query(AnalysisRequest).filter(AnalysisRequest.id == task_id).first()
    if not request:
        # If not in DB, maybe it's a celery ID? Let's check celery.
        task_result = AsyncResult(task_id, app=celery_app)
        if not task_result:
             raise HTTPException(status_code=404, detail="Task not found.")
        return {"status": task_result.status, "result": task_result.result}

    response = {"task_id": request.id, "status": request.status, "created_at": request.created_at}

    if request.status == "COMPLETED" and request.result:
        response["result"] = request.result.content
    elif request.status == "FAILED":
        # Get celery error info
        task_result = AsyncResult(task_id, app=celery_app)
        response["error"] = str(task_result.result)

    return response

if __name__ == "__main__":
    import uvicorn
    # Note: `reload=True` is not recommended for production with Celery.
    # It can cause issues with how workers are managed.
    uvicorn.run(app, host="0.0.0.0", port=8000)