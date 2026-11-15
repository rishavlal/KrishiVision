@echo off
title कृषिVision - Full Stack Launcher
echo =====================================================================
echo   कृषिVision — Intelligent Crop Recommendation and Plant Disease Detection
echo =====================================================================
echo.
cd /d "%~dp0"
if exist "%~dp0venv\Scripts\python.exe" (
    set "PY_EXE=%~dp0venv\Scripts\python.exe"
) else if exist "%~dp0backend\venv\Scripts\python.exe" (
    set "PY_EXE=%~dp0backend\venv\Scripts\python.exe"
) else (
    set "PY_EXE=python"
)

echo [1/2] Launching FastAPI Backend Server on http://127.0.0.1:8000 using %PY_EXE% ...
start "कृषिVision Backend" cmd /k "cd /d "%~dp0backend" && "%PY_EXE%" -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload"

echo [2/2] Waiting 2 seconds for server to initialize...
timeout /t 2 /nobreak >nul

echo.
echo Opening कृषिVision Landing Page in default browser...
start http://127.0.0.1:8000/

echo.
echo =====================================================================
echo  कृषिVision is now RUNNING!
echo  - Landing Page:             http://127.0.0.1:8000/
echo  - Farmer Portal / App:      http://127.0.0.1:8000/app
echo  - Interactive Swagger Docs: http://127.0.0.1:8000/docs
echo  - Backend API Health:       http://127.0.0.1:8000/api/health
echo =====================================================================
echo.
pause
