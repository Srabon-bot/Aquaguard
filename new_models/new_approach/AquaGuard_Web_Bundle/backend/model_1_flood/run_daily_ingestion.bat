@echo off
REM Daily Ingestion & Automated Model Inference Scheduler Script
echo Running Daily Live Ingestion Pipeline for Bahadurabad Station...
python -m src.ingestion
echo Daily Ingestion Completed Successfully!
