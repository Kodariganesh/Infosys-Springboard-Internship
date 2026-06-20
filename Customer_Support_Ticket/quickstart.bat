@echo off
REM Quick start script for Customer Support Ticket System (Windows)

echo =========================================
echo Customer Support Ticket System - Setup
echo =========================================

REM Check Python version
echo.
echo Checking Python installation...
python --version

REM Create virtual environment
echo.
echo Creating virtual environment...
python -m venv venv

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat

REM Install dependencies
echo.
echo Installing dependencies...
pip install -r requirements.txt

REM Download NLTK data
echo.
echo Downloading NLTK data...
python -c "import nltk; nltk.download('punkt'); nltk.download('stopwords'); nltk.download('wordnet'); nltk.download('omw-1.4')"

echo.
echo =========================================
echo Setup complete!
echo.
echo Next steps:
echo 1. Create .env file from .env.example
echo 2. Place your data in data\ directory
echo 3. Run: python main.py --action all
echo =========================================
pause
