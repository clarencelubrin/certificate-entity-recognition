@REM Detect if it has python 3.11 installed
@echo off
python --version 2>nul | findstr /R /C:"Python 3\.11" >nul
IF %ERRORLEVEL% NEQ 0 (
    ECHO Python 3.11 is not installed. Please install Python 3.11 and ensure it is added to your PATH.
    EXIT /B 1
)
ECHO Python 3.11 detected.
@REM Create and activate virtual environment
python -m venv .venv
call .venv\Scripts\activate
ECHO Virtual environment activated.
@REM Upgrade pip
python -m pip install --upgrade pip
ECHO Pip upgraded.
@REM Install required packages
pip install -r requirements.txt
pip install -U "huggingface_hub[cli]"
ECHO Downloading model file...
huggingface-cli download [REPO_NAME] --include "Phi-3.5-mini-instruct-Q4_K_M.gguf" --local-dir ./models
ECHO Required packages installed.
@REM Installation complete
@REM Call run.bat to start the application
call run.bat