@echo off
cd /d "%~dp0"

echo Starting Main Application...
start cmd /k python app.py

echo Starting Dashboard...
start cmd /k python dashboard.py

timeout /t 2 >nul

echo Opening browser...
start http://127.0.0.1:5000
start http://127.0.0.1:5001