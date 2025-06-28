import os
from tools import BloodTestReportTool
import camelot
import pandas as pd

def extract_tables_with_camelot(pdf_path, output_path):
    """
    Extracts tables from a PDF using Camelot and saves them to a text file.
    """
    print(f"\n--- Starting Camelot Table Extraction from: {pdf_path} ---")
    
    try:
        # Switching to "stream" which is better for PDFs without clear grid lines.
        tables = camelot.read_pdf(pdf_path, flavor='stream', pages='all')
        
        if tables:
            with open(output_path, "w", encoding="utf-8") as f:
                f.write(f"--- Extracted {tables.n} tables using Camelot (Stream) ---\n\n")
                for i, table in enumerate(tables):
                    f.write(f"--- Table {i+1} (Page: {table.page}) ---\n")
                    # Clean up the DataFrame before printing
                    df = table.df.copy()
                    df.columns = df.iloc[0]  # Set the first row as the header
                    df = df[1:]  # Remove the original header row
                    df.dropna(axis=1, how='all', inplace=True) # Drop empty columns
                    df.dropna(axis=0, how='all', inplace=True) # Drop empty rows
                    df.reset_index(drop=True, inplace=True)

                    f.write(df.to_string(index=False, header=True))
                    f.write("\n\n")
            print(f"Camelot extraction complete. {tables.n} tables saved to: {output_path}")
        else:
            print("Camelot (Stream) could not find any tables in the PDF.")
            
    except Exception as e:
        print(f"An error occurred during Camelot extraction: {e}")

def test_extraction(pdf_path, output_path):
    """
    Tests the PDF extraction tool and saves the output to a text file.
    """
    if not os.path.exists(pdf_path):
        print(f"Error: The file '{pdf_path}' was not found.")
        print("Please place a sample PDF file at that location to run the test.")
        return

    print(f"Testing extraction from: {pdf_path}")

    # Instantiate the tool
    pdf_tool = BloodTestReportTool()

    # The search query is required, but for this test, we are interested
    # in the raw extraction, which happens before the search.
    # We'll use a broad query to get a general sense of the extraction.
    search_query = "report summary"

    # Run the tool's extraction and search method
    # The tool returns the content of relevant document chunks.
    extracted_content = pdf_tool._run(pdf_path=pdf_path, search_query=search_query)

    # Save the extracted content to a .txt file
    with open(output_path, "w", encoding="utf-8") as f:
        f.write("--- Extracted Content using PyMuPDFLoader ---\n\n")
        f.write(extracted_content)

    print(f"Extraction complete. Output saved to: {output_path}")
    if not extracted_content:
        print("Warning: The extracted content is empty. The PDF might be image-based or have no text.")
    else:
        print("\n--- Start of Extracted Content Preview ---\n")
        print(extracted_content[:1500])
        print("\n--- End of Extracted Content Preview ---")


if __name__ == "__main__":
    # --- Instructions ---
    # 1. Place a PDF file you want to test inside the 'vwo-assignment/data/' directory.
    # 2. Change the value of PDF_FILE_NAME to match the name of your file.
    # 3. Run this script from your terminal: python vwo-assignment/test_pdf_extractor.py
    
    PDF_FILE_NAME = "sample.pdf"  # <-- CHANGE THIS to your test PDF file name
    
    # --- Do not change the code below ---
    PDF_FILE_PATH = "/home/srinivasan/Downloads/VWO-Assignment/vwo-assignment/data/sample.pdf"
    OUTPUT_FILE_PATH = "/home/srinivasan/Downloads/VWO-Assignment/vwo-assignment/outputs/extraction_output.txt"
    CAMELOT_OUTPUT_PATH = "/home/srinivasan/Downloads/VWO-Assignment/vwo-assignment/outputs/camelot_tables.txt"
    
    # Run the existing text and pdfplumber extraction
    test_extraction(PDF_FILE_PATH, OUTPUT_FILE_PATH)
    
    # Run the new Camelot table extraction
    extract_tables_with_camelot(PDF_FILE_PATH, CAMELOT_OUTPUT_PATH) 