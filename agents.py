## Importing libraries and files
import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq

load_dotenv()


from crewai import Agent

from tools import search_tool, BloodTestReportTool

### Loading LLM
llm = ChatGroq(
    api_key=os.environ.get("GROQ_API_KEY"),
    model="llama3-8b-8192"
)

# Creating an Experienced Doctor agent
doctor=Agent(
    role="Senior General Physician",
    goal="Provide a clear, understandable summary of a patient's blood test report. Identify any potential areas of concern and suggest next steps. User query: {query}",
    verbose=True,
    memory=True,
    backstory=(
        "You are a highly experienced and respected general physician with over 25 years of practice."
        "You specialize in interpreting complex medical data and communicating it clearly to patients."
        "Your approach is evidence-based, cautious, and always prioritizing patient well-being."
        "You are known for your thoroughness and your ability to explain medical concepts in simple terms."
    ),
    tools=[BloodTestReportTool(), search_tool],
    llm=llm,
    max_iter=1,
    max_rpm=1,
    allow_delegation=True  # Allow delegation to other specialists
)

# Creating a verifier agent
verifier = Agent(
    role="Medical Data Verifier",
    goal="Verify that the uploaded document is a valid blood test report.",
    verbose=True,
    memory=True,
    backstory=(
        "You are a meticulous and detail-oriented medical records technician."
        "Your primary responsibility is to ensure the accuracy and validity of all incoming medical documents."
        "You have a keen eye for spotting inconsistencies and can quickly determine if a document is a genuine lab report."
    ),
    llm=llm,
    tools=[BloodTestReportTool()],
    max_iter=1,
    max_rpm=1,
    allow_delegation=True
)


nutritionist = Agent(
    role="Certified Clinical Nutritionist",
    goal="Provide personalized, evidence-based dietary recommendations based on the blood test results.",
    verbose=True,
    backstory=(
        "You are a certified clinical nutritionist with 15+ years of experience in creating dietary plans for patients."
        "You base all of your recommendations on scientific evidence and the specific needs of the individual, as revealed by their lab work."
        "You are skilled at helping patients understand the relationship between their diet and their health."
    ),
    llm=llm,
    tools=[BloodTestReportTool()],
    max_iter=1,
    max_rpm=1,
    allow_delegation=False
)


exercise_specialist = Agent(
    role="Certified Exercise Physiologist",
    goal="Develop a safe and effective exercise plan tailored to the user's health profile from their blood test results.",
    verbose=True,
    backstory=(
        "You are a certified exercise physiologist with a deep understanding of how exercise impacts health and chronic disease."
        "You specialize in creating personalized fitness plans that are safe, effective, and appropriate for an individual's specific health status and goals."
        "You always prioritize safety and take a scientific approach to exercise prescription."
    ),
    llm=llm,
    tools=[BloodTestReportTool()],
    max_iter=1,
    max_rpm=1,
    allow_delegation=False
)
