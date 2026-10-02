@echo off
REM Launcher script for Bahadurabad Forecasting FastAPI Web Backend Server
echo Starting Bahadurabad Water Level Forecasting Web API on http://localhost:8000 ...
echo API Documentation available at http://localhost:8000/docs
uvicorn api:app --host 0.0.0.0 --port 8000 --reload
