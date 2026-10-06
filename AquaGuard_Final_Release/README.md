# AquaGuard Final Release

This folder contains the complete, sendable package for the AquaGuard Flood Prediction & Water Quality monitoring system. You can zip this entire folder and send it to another PC.

## Folder Structure

* `hardware/`: Contains everything needed to build the physical IoT node.
  * `TODO_Assembly_Testing.md`: Step-by-step guide on how to wire the ESP32 and sensors.
  * `arduino_firmware/`: The ESP32 C++ code that reads sensors and transmits data to the ML backend and Web Dashboard.
* `software/`: Contains the Machine Learning models, API, and Web Dashboard.
  * `backend/`: The FastAPI server containing Model 1 (Flood), Model 2 (TDS), and Model 3 (Anomaly Detection).
  * `frontend/`: The HTML/JS/CSS for the web dashboard.

## How to Run (1-Click)

Simply double-click the `Run_AquaGuard.bat` file in this directory. 

It will automatically:
1. Launch the Python FastAPI Machine Learning backend on Port 8000.
2. Launch a local web server to host the Web Dashboard on Port 8080.
3. Open your default web browser to the dashboard.

*Note: You must have Python installed on the target PC to run the backend and frontend servers.*
