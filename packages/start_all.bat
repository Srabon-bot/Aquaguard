@echo off
REM Double-click convenience wrapper for Windows -- see SETUP_MANUAL.md for first-time setup.
REM Assumes the shared virtual environment already exists at packages\.venv (Step 3 of the manual).

cd /d "%~dp0"

if not exist ".venv\Scripts\python.exe" (
    echo Could not find packages\.venv\Scripts\python.exe
    echo Run the first-time setup in SETUP_MANUAL.md before using this shortcut.
    pause
    exit /b 1
)

".venv\Scripts\python.exe" run_all.py
pause
