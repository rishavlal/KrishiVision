@echo off
title कृषिVision Backend Server
echo =====================================================================
echo   Starting कृषिVision FastAPI Backend Server...
echo   API Root:      http://127.0.0.1:8000
echo   Swagger Docs:  http://127.0.0.1:8000/docs
echo   Farmer Portal: http://127.0.0.1:8000/app
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

echo Using Python runtime: %PY_EXE%
cd /d "%~dp0backend"
"%PY_EXE%" -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
pause
