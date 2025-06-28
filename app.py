import chainlit as cl
import os
import asyncio
import httpx
import time

API_URL = "http://localhost:8000"

async def upload_file(file: cl.File):
    """Uploads the file to the FastAPI backend."""
    with open(file.path, "rb") as f:
        content = f.read()

    files = [("file", (file.name, content, "application/pdf"))]
    headers = {"accept": "application/json"}
    data = {"query": cl.user_session.get("query")}
    
    async with httpx.AsyncClient(timeout=30) as client:
        try:
            response = await client.post(f"{API_URL}/analyze", files=files, data=data, headers=headers)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            await cl.Message(content=f"Error uploading file: {e.response.text}").send()
            return None
        except httpx.RequestError as e:
            await cl.Message(content=f"Error connecting to backend: {e}").send()
            return None

async def poll_for_result(task_id: str):
    """Polls the backend for the analysis result."""
    headers = {"accept": "application/json"}
    start_time = time.time()
    timeout = 300  # 5 minutes

    async with httpx.AsyncClient() as client:
        while time.time() - start_time < timeout:
            try:
                response = await client.get(f"{API_URL}/results/{task_id}", headers=headers)
                response.raise_for_status()
                data = response.json()
                
                if data["status"] == "COMPLETED":
                    return data["result"]
                elif data["status"] == "FAILED":
                    return f"Analysis failed: {data.get('error', 'Unknown error')}"
                
                # Wait before polling again
                await asyncio.sleep(5)

            except httpx.HTTPStatusError as e:
                return f"Error polling for results: {e.response.text}"
            except httpx.RequestError as e:
                return f"Error connecting to backend: {e}"
        
        return "Analysis timed out. Please try again later."


@cl.on_chat_start
async def start_chat():
    # Ask for the user's query
    res = await cl.AskUserMessage(
        content="Welcome to the Blood Test Report Analyser! What would you like to know about your blood test report?"
    ).send()
    cl.user_session.set("query", res["output"])

    # Ask for the PDF file
    files = None
    while files is None:
        files = await cl.AskFileMessage(
            content="Please upload your blood test report in PDF format to continue.",
            accept=["application/pdf"],
            max_size_mb=20,
            timeout=180,
        ).send()
    
    file = files[0]

    # Let the user know the analysis is starting
    msg = cl.Message(content=f"Processing `{file.name}`... This may take a few minutes.")
    await msg.send()

    # 1. Upload file and start analysis
    upload_response = await upload_file(file)
    if not upload_response or "task_id" not in upload_response:
        await cl.Message(content="Failed to start the analysis task.").send()
        return

    task_id = upload_response["task_id"]
    
    # Update the UI
    msg.content = f"Your report `{file.name}` is being analyzed. Task ID: `{task_id}`. Please wait."
    await msg.update()

    # 2. Poll for the result
    final_result = await poll_for_result(task_id)

    # 3. Display the final result
    await cl.Message(content="--- Final Report ---").send()
    await cl.Message(content=final_result).send()

    # Save the final report to a markdown file
    output_dir = "outputs"
    os.makedirs(output_dir, exist_ok=True)
    report_path = os.path.join(output_dir, f"final_report_{task_id}.md")
    with open(report_path, "w") as f:
        f.write(final_result)

    await cl.Message(content=f"Final report saved to `{report_path}`.").send() 