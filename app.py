import chainlit as cl
import os
import asyncio
from crewai import Crew, Process
from crewai.utilities.events import crewai_event_bus, LLMStreamChunkEvent
from agents import doctor, verifier, nutritionist, exercise_specialist
from task import verification, help_patients, nutrition_analysis, exercise_planning

# Define the crew outside of the session
medical_crew = Crew(
    agents=[verifier, doctor, nutritionist, exercise_specialist],
    tasks=[verification, help_patients, nutrition_analysis, exercise_planning],
    process=Process.sequential,
    verbose=True,
    max_iter=4,
)

# Create an async queue to hold the tokens
token_queue = asyncio.Queue()

# Define the async handler for streaming events
async def on_llm_stream(event: LLMStreamChunkEvent):
    """Asynchronously handles streaming events from the LLM."""
    await token_queue.put(event.chunk)

@cl.on_chat_start
async def start_chat():
    # Register the async handler
    crewai_event_bus.register_handler(LLMStreamChunkEvent, on_llm_stream)

    # Ask for the user's query
    res = await cl.AskUserMessage(content="Welcome to the Blood Test Report Analyser! What would you like to know about your blood test report?").send()
    
    # Ask for the PDF file
    files = None
    while files is None:
        files = await cl.AskFileMessage(
            content="Please upload your blood test report in PDF format to continue.",
            accept=["application/pdf"],
            max_size_mb=20,
            timeout=180,
        ).send()

    # Store the query and file in the session
    cl.user_session.set("query", res['output'])
    cl.user_session.set("pdf_file", files[0])
    
    # Let the user know the analysis is starting
    await cl.Message(
        content=f"Processing `{files[0].name}` for your query: '{res['output']}'. Please wait..."
    ).send()

    # Run the crew
    await run_crew_in_background()


async def run_crew_in_background():
    query = cl.user_session.get("query")
    pdf_file = cl.user_session.get("pdf_file")
    file_path = pdf_file.path
    inputs = {'query': query, 'file_path': file_path}

    # Create a placeholder for the streamed response
    msg = cl.Message(content="")
    await msg.send()

    # Create a separate task for the crew kickoff to run in the background
    crew_task = asyncio.create_task(cl.make_async(medical_crew.kickoff)(inputs))

    # Consume tokens from the queue and stream them to the UI
    while not crew_task.done() or not token_queue.empty():
        while not token_queue.empty():
            token = await token_queue.get()
            await msg.stream_token(token)
            token_queue.task_done()
        await asyncio.sleep(0.1) # Small sleep to prevent a busy-wait loop

    # Get the final result from the crew task
    result = crew_task.result()
    
    # Update the final message with the complete response
    await msg.update()

    # Send the final result as a separate message for clarity
    await cl.Message(
        author="Final Report",
        content=result
    ).send()

    # Chainlit handles the temporary file, so no need to manually clean up. 