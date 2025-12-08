@REM Start the application
@echo off
@REM Activate virtual environment
call .venv\Scripts\activate
ECHO Virtual environment activated.
@REM Run the FastAPI application with uvicorn
python app.py
ECHO Application started.
@REM Application running