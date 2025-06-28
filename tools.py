## Importing libraries and files
import os
from dotenv import load_dotenv
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings
from crewai.tools import BaseTool
from crewai_tools import SerperDevTool
from pydantic import BaseModel, Field
from typing import Type

load_dotenv()

from crewai_tools import tools


## Creating search tool
search_tool = SerperDevTool()

class BloodTestReportToolSchema(BaseModel):
    pdf_path: str = Field(description="The file path of the PDF blood test report.")
    search_query: str = Field(description="The specific query or question to search for within the report.")

class BloodTestReportTool(BaseTool):
    name: str = "Blood Test Report Searcher"
    description: str = "Searches for specific information within a PDF blood test report and returns only the most relevant snippets."
    args_schema: Type[BaseModel] = BloodTestReportToolSchema

    def _run(self, pdf_path: str, search_query: str) -> str:
        # Sanitize the file path to remove any surrounding quotes or spaces
        sanitized_path = pdf_path.strip("'\" ")
        
        # 1. Load document
        loader = PyPDFLoader(file_path=sanitized_path)
        docs = loader.load()

        # 2. Split text with a larger chunk size
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=2048, chunk_overlap=200)
        splits = text_splitter.split_documents(docs)

        # 3. Create vector store
        embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
        vectorstore = Chroma.from_documents(documents=splits, embedding=embeddings)

        # 4. Retrieve relevant chunks
        retriever = vectorstore.as_retriever(search_kwargs={"k": 5})
        retrieved_docs = retriever.get_relevant_documents(search_query)

        # 5. Format and return
        return "\n\n".join([doc.page_content for doc in retrieved_docs])

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

