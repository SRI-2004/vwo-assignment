## Importing libraries and files
from crewai import Task

from agents import doctor, verifier, nutritionist, exercise_specialist
from tools import BloodTestReportTool

## Creating a task to help solve user's query
help_patients = Task(
    description="""Analyze the blood test report at {file_path} to answer the user's query: '{query}'.

Your process must be efficient and targeted:
1.  **Formulate a Batch Query**: Based on the user's query, identify all relevant medical terms and combine them into a single search query for the tool. Separate keywords with " OR " (e.g., `"Glucose" OR "LDL Cholesterol"`).
2.  **Execute a Single, Powerful Search**: Use the 'Blood Test Report Searcher' tool **once** with your combined query.
3.  **Synthesize and Explain**: Thoroughly analyze the retrieved text. Extract all relevant results, including value, units, and reference range. Explain the findings clearly and formulate a comprehensive answer to the user's query.
4.  **Conclude**: Provide a final, easy-to-understand summary and advise the user to consult with a healthcare provider.""",
    expected_output="""A detailed and well-structured answer that fully addresses the user's query, supported by specific data from the report. The output must include:
- A list of all relevant lab results with their values, units, and reference ranges, derived from a single, efficient search.
- A clear interpretation of each result.
- A final summary that is easy for a layperson to understand.
- A concluding statement advising consultation with a healthcare provider.""",
    agent=doctor,
)

## Creating a nutrition analysis task
nutrition_analysis = Task(
    description="Your goal is to provide nutrition advice based on the user's query: '{query}' and the report at {file_path}. To do this efficiently, you must formulate a single, comprehensive search query that includes all major nutritional markers (e.g., 'Glucose', 'Cholesterol', 'HDL', 'LDL', 'Triglycerides', 'Iron', 'Vitamin D', 'Vitamin B12'). Execute one search with this batch query using the 'Blood Test Report Searcher' tool. Then, analyze the combined results to provide personalized and actionable nutritional recommendations.",
    expected_output="""A detailed nutrition plan based on a thorough analysis of the report. It should include:
- A summary of all nutrition-related lab results found in the report from a single search.
- An analysis of how these results relate to the user's nutritional status.
- Specific, actionable dietary recommendations and a sample one-day meal plan.
- A disclaimer that this is not medical advice and the user should consult a doctor.""",
    agent=nutritionist,
)

## Creating an exercise planning task
exercise_planning = Task(
    description="Your goal is to create an exercise plan based on the user's query: '{query}' and the report at {file_path}. Formulate a single, comprehensive search query to find all lab results relevant to physical activity (e.g., 'Cholesterol', 'Hemoglobin', 'Cardiac Risk', 'CBC'). Use the 'Blood Test Report Searcher' tool just once with this query. Synthesize the findings from this single search to develop a safe, effective, and personalized exercise plan.",
    expected_output="""A personalized exercise plan based on a comprehensive review of the report. It should include:
- An assessment of the user's fitness level based on the relevant search results from a single search.
- A recommended weekly exercise schedule, including types of exercise, duration, and intensity.
- Safety precautions and modifications based on any potential health concerns identified in the report.
- A disclaimer that the user should consult their doctor before starting an exercise program.""",
    agent=exercise_specialist,
)
    
verification = Task(
    description="""Your mission is to validate the document at {file_path} as a legitimate blood test report in a single, efficient step.

Follow this exact procedure:
1.  **Execute a Single Batch Search**: Use the 'Blood Test Report Searcher' tool **once** with the following combined query: `"Patient Name" OR "Lab Results" OR "Reference Range" OR "Hemoglobin"`.
2.  **Assess the Results**: Review the output from the tool. To be considered valid, the document must contain evidence for at least THREE of the four keywords.

Your final answer must be a definitive statement of the document's validity based on this single search.""",
    expected_output="A definitive statement based on a comprehensive search: 'The document appears to be a valid blood test report based on the presence of multiple key identifiers.' or 'The document does not appear to be a valid blood test report because it is missing key identifiers.'",
    agent=verifier,
    tools=[BloodTestReportTool()],
)