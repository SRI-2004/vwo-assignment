# Project Setup and Execution Guide

## Getting Started

### Install Required Libraries
```sh
pip install -r requirements.txt
```

## Running the Application
This project now uses Chainlit for its user interface.

1. **Set Environment Variables**: Make sure you have your `GOOGLE_API_KEY` set in a `.env` file in the project root.

2. **Run the app**:
   ```sh
   chainlit run app.py -w
   ```
   The `-w` flag enables auto-reloading, so the app will restart when you make changes to the code.

3. **Open in your browser**: Open your web browser and navigate to `http://localhost:8000`.

**Note**: The old FastAPI entry point, `main.py`, is no longer used and can be deleted.

🐛 **Debug Mode Activated!** The project has bugs waiting to be squashed - your mission is to fix them and bring it to life.

## Debugging Instructions

1. **Identify the Bug**: Carefully read the code and understand the expected behavior.
2. **Fix the Bug**: Implement the necessary changes to fix the bug.
3. **Test the Fix**: Run the project and verify that the bug is resolved.
4. **Repeat**: Continue this process until all bugs are fixed.

## Setup

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/your-username/vwo-assignment.git
    cd vwo-assignment
    ```

2.  **Create a virtual environment and activate it:**
    ```bash
    python -m venv venv
    source venv/bin/activate
    ```

3.  **Install the dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Set up your API key:**
    Create a `.env` file in the root of the project and add your Google API key:
    ```
    GOOGLE_API_KEY="your-google-api-key"
    ```

## How to Run

1.  **Start the Chainlit application:**
