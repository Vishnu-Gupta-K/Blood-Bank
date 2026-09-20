@echo off
echo Starting Blood Bank Frontend Server...
cd frontend

REM Check if Python is installed
python --version >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    echo Using Python's built-in HTTP server...
    python -m http.server 5500
) else (
    echo Python not found. Please install Python or use a different web server like Live Server in VS Code.
    echo You can open the frontend by directly opening the index.html file in your browser,
    echo but some features might not work correctly without a proper web server.
)

pause