from celery_config import celery_app
from database import SessionLocal, AnalysisRequest, AnalysisResult
from crewai import Crew, Process
from agents import doctor, verifier, nutritionist, exercise_specialist
from task import verification, help_patients, nutrition_analysis, exercise_planning

def get_crew(query: str, file_path: str):
    """Initializes and returns the medical crew."""
  
    return Crew(
        agents=[verifier, doctor, nutritionist, exercise_specialist],
        tasks=[verification, help_patients, nutrition_analysis, exercise_planning],
        process=Process.sequential,
        verbose=True
    )

@celery_app.task(bind=True)
def run_analysis_crew(self, request_id: str):
    """Celery task to run the full analysis crew."""
    db = SessionLocal()
    try:
        # 1. Get the request details from the DB
        request = db.query(AnalysisRequest).filter(AnalysisRequest.id == request_id).first()
        if not request:
            raise ValueError("Request not found")

        # 2. Update status to PROCESSING
        request.status = "PROCESSING"
        db.commit()

        # 3. Initialize and run the crew
        medical_crew = get_crew(request.query, request.file_path)
        inputs = {'query': request.query, 'file_path': request.file_path}
        result = medical_crew.kickoff(inputs)

        # 4. Save the result to the DB
        new_result = AnalysisResult(request_id=request_id, content=str(result))
        db.add(new_result)
        
        # 5. Update status to COMPLETED
        request.status = "COMPLETED"
        db.commit()
        
        return {"status": "SUCCESS", "result": str(result)}

    except Exception as e:
        # Update status to FAILED
        request.status = "FAILED"
        db.commit()
        # Log the error, Celery will also store the exception
        print(f"Task failed: {e}")
        # Reraise the exception to let Celery know the task failed
        raise
    
    finally:
        db.close() 