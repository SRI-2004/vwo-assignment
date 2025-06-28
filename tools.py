from dotenv import load_dotenv
load_dotenv()

## Importing libraries and files
import os
import re
import camelot
import pandas as pd
from langchain_community.document_loaders import PyMuPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings
from crewai.tools import BaseTool
from crewai_tools import SerperDevTool
from pydantic import BaseModel, Field
from typing import Type
from langchain_core.documents import Document

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
        # Sanitize the file path
        sanitized_path = pdf_path.strip("'\" ")
        
        # 1. Extract tables using Camelot's stream method
        try:
            tables = camelot.read_pdf(sanitized_path, flavor='stream', pages='all')
        except Exception as e:
            return f"Error extracting tables with Camelot: {e}"

        if not tables:
            return "No tables found in the PDF."

        # 2. Process and consolidate all tables into a single string
        all_tables_text = []
        for i, table in enumerate(tables):
            # Check each cell in the DataFrame for the "End of report" marker.
            # This is more robust than checking the string representation.
            end_of_report_found = False
            for _, row in table.df.iterrows():
                for cell in row:
                    if "End of report" in str(cell):
                        end_of_report_found = True
                        break
                if end_of_report_found:
                    break
            
            # Skip the table if the marker was found
            if end_of_report_found:
                continue

            # Clean up the DataFrame for better text representation
            df = table.df.copy()
            # The first row might not always be the header, so we'll treat it as data
            # and let the LLM infer the structure from the clean text.
            df.dropna(axis=1, how='all', inplace=True) # Drop empty columns
            df.dropna(axis=0, how='all', inplace=True) # Drop empty rows
            df.reset_index(drop=True, inplace=True)

            # Prepend a header for the LLM to understand context
            page_header = f"--- Table from Page {table.page} ---\n"
            clean_table_text = df.to_string(index=False, header=True)
            
            all_tables_text.append(page_header + clean_table_text)

        # 3. Combine all cleaned table text into a single string for the LLM
        full_text = "\n\n".join(all_tables_text).strip()

        if not full_text:
             return "Could not extract any valid table content from the PDF."
        
        
        # 4. Split the text and create a searchable vector store
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=150)
        docs = text_splitter.create_documents([full_text])

        # 5. Set up the vector store with embeddings
        embeddings = HuggingFaceEmbeddings(model_kwargs={"device": "cpu"})
        vectorstore = Chroma.from_documents(docs, embeddings)
        
        # 6. Search for the most relevant documents based on the query
        retriever = vectorstore.as_retriever(search_kwargs={"k": 4})
        relevant_docs = retriever.get_relevant_documents(search_query)
        
        # 7. Concatenate the content of the relevant documents, ensuring uniqueness
        unique_contents = []
        seen_contents = set()
        for doc in relevant_docs:
            if doc.page_content not in seen_contents:
                unique_contents.append(doc.page_content)
                seen_contents.add(doc.page_content)
        
        relevant_text = "\n\n".join(unique_contents)

        return relevant_text

