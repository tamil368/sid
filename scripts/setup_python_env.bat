@echo off
:: Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo Python is not installed. Please install Python and try again.
    exit /b
)

:: Create virtual environment in "env" folder
echo Creating virtual environment...
python -m venv env

:: Check if requirements.txt exists
if not exist requirements.txt (
    echo requirements.txt file not found. Skipping package installation.
) else (
    echo Installing packages from requirements.txt...
    env\Scripts\pip install -r requirements.txt
)

:: Activate the virtual environment
echo Activating virtual environment...
if "%ComSpec%"=="" (
    env\Scripts\Activate
) else (
    call env\Scripts\Activate
)

echo Virtual environment is activated.
