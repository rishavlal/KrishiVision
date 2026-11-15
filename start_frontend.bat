@echo off
title कृषिVision Frontend Launcher
echo =====================================================================
echo   Opening कृषिVision Frontend Dashboard...
echo =====================================================================
echo.
start http://127.0.0.1:8000/
timeout /t 1 /nobreak >nul
echo Done! Landing Page opened. Farmer Portal is at http://127.0.0.1:8000/app
