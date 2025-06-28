import chainlit as cl
import asyncio
from crewai import Crew, Process

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


@cl.on_chat_start
async def start_chat():
    # Ask for the user's query
    res = await cl.AskUserMessage(
        content="Welcome to the Blood Test Report Analyser! What would you like to know about your blood test report?"
    ).send()

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
    cl.user_session.set("query", res["output"])
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
    inputs = {"query": query, "file_path": file_path}

    # We need to run the kickoff in a separate thread to not block the event loop.
    # The verbose output from crewAI will be printed to the console.
    await cl.make_async(medical_crew.kickoff)(inputs)

    # Extract and display the output from each completed task
    await cl.Message(content="--- Final Report ---").send()
    for task in medical_crew.tasks:
        if task.output is not None:
            # The Final Answer is in task.output.raw
            await cl.Message(author=task.agent.role, content=task.output.raw).send()

    # Chainlit handles the temporary file, so no need to manually clean up. 