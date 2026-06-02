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

REM Get the directory where this script is located (project root)
set SCRIPT_DIR=%~dp0
cd /d "%SCRIPT_DIR%"

REM Check if we're in the right directory
if not exist "backend" (
    echo Error: backend directory not found
    echo Please run this script from the project root directory
    pause
    exit /b 1
)
if not exist "web" (
    echo Error: web directory not found
    echo Please run this script from the project root directory
    pause
    exit /b 1
)

REM Prefer the project virtual environment if present
set PYTHON=python
if exist "%SCRIPT_DIR%.venv\Scripts\python.exe" set PYTHON=%SCRIPT_DIR%.venv\Scripts\python.exe

REM Check Python
"%PYTHON%" --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python is not installed or not in PATH
    pause
    exit /b 1
)

echo [1/3] Checking dependencies...
"%PYTHON%" -m pip show fastapi >nul 2>&1
if errorlevel 1 (
    echo Installing dependencies...
    "%PYTHON%" -m pip install -q fastapi uvicorn -r requirements.txt
)

echo [2/3] Starting Backend API...
echo.
start "Face Recognition Backend" cmd /k "cd /d "%SCRIPT_DIR%backend" && "%PYTHON%" api_server.py"

REM Wait for API to start
timeout /t 3 /nobreak

echo [3/3] Starting Frontend Web Server...
echo.
start "Face Recognition Frontend" cmd /k "cd /d "%SCRIPT_DIR%web" && npm run dev"

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
