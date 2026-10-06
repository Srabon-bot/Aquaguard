@echo off
echo =======================================================
echo          STARTING AQUAGUARD FULL SYSTEM
echo =======================================================
echo.

echo [1/2] Starting Machine Learning FastAPI Backend (Port 8000)...
cd software\backend
start cmd /k "python api_combined.py"

echo [2/2] Starting Web Dashboard (Port 8080)...
cd ..\frontend
start cmd /k "python -m http.server 8080"

echo.
echo =======================================================
echo System is running!
echo.
echo - FastAPI Backend is running at: http://127.0.0.1:8000
echo - Web Dashboard will open shortly...
echo =======================================================
echo.

timeout /t 3 /nobreak > nul
start http://127.0.0.1:8080

echo Press any key to close this launcher (Servers will keep running in separate windows).
pause > nul
