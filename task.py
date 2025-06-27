## Importing libraries and files
from crewai import Task

from agents import doctor, verifier, nutritionist, exercise_specialist
from tools import BloodTestReportTool

## Creating a task to help solve user's query
help_patients = Task(
    description="Analyze the user's blood test report at {file_path} based on their query: {query}. Use the web search tool to find additional context or information about the patient's conditions or lab results if needed. Provide a clear, concise summary of the key findings, identify any values outside the normal range, and explain their potential significance in simple terms. Avoid speculation and stick to the data in the report unless external research clarifies a point.",
    expected_output="""A structured summary of the blood test report. It should include:
- An overall summary of the findings, potentially enriched with context from web searches.
- A list of any abnormalities detected, with a brief, easy-to-understand explanation of what each marker represents.
- A concluding statement suggesting the user discuss the results with their healthcare provider.""",
    agent=doctor,
    tools=[BloodTestReportTool()],
    async_execution=False,
)

## Creating a nutrition analysis task
nutrition_analysis = Task(
    description="Analyze the blood test report at {file_path} to provide personalized nutrition recommendations. The user's query is: {query}. Focus on how diet can help address any identified abnormalities or support overall health. Base all advice on established nutritional science.",
    expected_output="""A detailed nutrition plan. It should include:
- An analysis of how the blood test results relate to the user's current nutritional status.
- Specific, actionable dietary recommendations (e.g., foods to eat, foods to avoid).
- A sample one-day meal plan.
- A disclaimer that this advice is not a substitute for consultation with a doctor or registered dietitian.""",
    agent=nutritionist,
    tools=[BloodTestReportTool()],
    async_execution=False,
)

## Creating an exercise planning task
exercise_planning = Task(
    description="Develop a safe and effective exercise plan based on the user's blood test report at {file_path} and their query: {query}. The plan should be tailored to the user's likely health status and fitness level, considering any potential risks highlighted in the report.",
    expected_output="""A personalized exercise plan. It should include:
- An assessment of the user's fitness level based on the report.
- A recommended weekly exercise schedule, including types of exercise (cardio, strength, flexibility), duration, and intensity.
- Safety precautions and modifications based on potential health concerns.
- A strong recommendation to consult a healthcare provider before starting any new exercise program.""",
    agent=exercise_specialist,
    tools=[BloodTestReportTool()],
    async_execution=False,
)

    
verification = Task(
    description="Carefully examine the document at {file_path} to determine if it is a legitimate blood test report. Check for common markers, reference ranges, and standard formatting. Conclude with a clear yes or no.",
    expected_output="A definitive statement: 'The document appears to be a valid blood test report.' or 'The document does not appear to be a valid blood test report.'",
    agent=verifier,
    tools=[BloodTestReportTool()],
    async_execution=False
)