## Importing libraries and files
import os
from dotenv import load_dotenv
from langchain_community.document_loaders import PyPDFLoader
from crewai.tools import BaseTool
from crewai_tools import SerperDevTool

load_dotenv()

from crewai_tools import tools


## Creating search tool
search_tool = SerperDevTool()

## Creating custom pdf reader tool
class BloodTestReportTool(BaseTool):
    name: str = "Blood Test Report Reader"
    description: str = "Reads the full content of a PDF blood test report from a given file path."

    def _run(self, path: str) -> str:
        """Tool to read data from a pdf file from a path."""
        docs = PyPDFLoader(file_path=path).load()
        full_report = ""
        for data in docs:
            content = data.page_content
            while "\n\n" in content:
                content = content.replace("\n\n", "\n")
            full_report += content + "\n"
        return full_report

## Creating Nutrition Analysis Tool
class NutritionTool(BaseTool):
    name: str = "Nutrition Analyzer"
    description: str = "Analyzes blood report data to provide nutrition advice. (Currently a placeholder)"
    
    def _run(self, blood_report_data: str) -> str:
        # Process and analyze the blood report data
        processed_data = blood_report_data
        
        # Clean up the data format
        i = 0
        while i < len(processed_data):
            if processed_data[i:i+2] == "  ":  # Remove double spaces
                processed_data = processed_data[:i] + processed_data[i+1:]
            else:
                i += 1
                
        # TODO: Implement nutrition analysis logic here
        return "Nutrition analysis functionality to be implemented"

## Creating Exercise Planning Tool
class ExerciseTool(BaseTool):
    name: str = "Exercise Planner"
    description: str = "Creates an exercise plan based on blood report data. (Currently a placeholder)"

    def _run(self, blood_report_data: str) -> str:        
        # TODO: Implement exercise planning logic here
        return "Exercise planning functionality to be implemented"

