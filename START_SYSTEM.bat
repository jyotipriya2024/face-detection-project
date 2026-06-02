@echo off
REM Complete AI Vision System Startup Script for Windows
REM Starts both Backend API and Frontend Web Server

title AI Vision System - Startup

echo.
echo ====================================================
echo  AI Vision - Face Recognition System
echo  Complete Startup Script
echo ====================================================
echo.

REM Get the directory where this script is located
set SCRIPT_DIR=%~dp0
cd /d "%SCRIPT_DIR%"

REM Check if we're in the right directory
if not exist "face_detection_system" (
    echo Error: face_detection_system directory not found
    echo Please run this script from the project root directory
    pause
    exit /b 1
)

REM Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python is not installed or not in PATH
    pause
    exit /b 1
)

echo [1/3] Checking dependencies...
python -m pip list | findstr fastapi >nul
if errorlevel 1 (
    echo Installing dependencies...
    pip install -q -r face_detection_system/requirements.txt
)

echo [2/3] Starting Backend API...
echo.
start "Face Recognition Backend" cmd /k "cd /d "%SCRIPT_DIR%face_detection_system\backend" && python api_server.py"

REM Wait for API to start
timeout /t 3 /nobreak

echo [3/3] Starting Frontend Web Server...
echo.
start "Face Recognition Frontend" cmd /k "cd /d "%SCRIPT_DIR%face_detection_system\web" && npm run dev"

REM Wait for frontend to start
timeout /t 3 /nobreak

echo.
echo ====================================================
echo  AI Vision System Started Successfully!
echo ====================================================
echo.
echo Backend API:  http://localhost:8000
echo Frontend Web: http://localhost:3000
echo.
echo The web browser will open shortly...
timeout /t 2 /nobreak

REM Open the frontend in browser
start "" "http://localhost:3000"

echo.
echo Both servers are now running. Close these windows to stop the system.
echo.
pause
