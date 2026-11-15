@echo off
title कृषिVision - One-Time Setup
echo =====================================================================
echo   कृषिVision — One-Time Environment Setup
echo =====================================================================
echo.
echo [1/3] Checking Python installation...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python is not installed or not in your PATH!
    echo Please install Python 3.10 or higher from https://www.python.org/
    echo Make sure to check "Add Python to PATH" during installation.
    echo.
    pause
    exit /b 1
)
python --version

echo.
echo [2/3] Creating local virtual environment (venv)...
if not exist "venv\Scripts\python.exe" (
    python -m venv venv
) else (
    echo Virtual environment already exists.
)

echo.
echo [3/3] Installing dependencies from backend\requirements.txt...
call venv\Scripts\activate.bat
python -m pip install --upgrade pip
pip install -r backend\requirements.txt

echo.
echo =====================================================================
echo  SETUP COMPLETE!
echo  You can now run the application anytime by double-clicking:
echo    -> start_all.bat
echo =====================================================================
echo.
pause
