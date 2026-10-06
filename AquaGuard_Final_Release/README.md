# AquaGuard Final Release

This is the complete, self-contained, sendable package for the AquaGuard system.
Zip this entire folder and run it on any PC.

---

## Folder Structure

```
AquaGuard_Final_Release/
├── Run_AquaGuard.bat              ← 1-click launcher (start here)
├── README.md
│
├── hardware/
│   ├── TODO_Assembly_Testing.md   ← Step-by-step wiring guide (read first)
│   └── arduino_firmware/
│       └── AquaGuard_v2/
│           └── AquaGuard_v2.ino  ← Flash this to your ESP32
│
└── software/
    ├── backend/                   ← FastAPI ML server (all 3 models)
    │   ├── api_combined.py        ← Entry point: python api_combined.py
    │   ├── model_1_flood/         ← River water-level forecasting
    │   ├── model_2/               ← Pond TDS forecasting (+60 min)
    │   └── model_3/               ← Water-quality anomaly detection
    │
    └── frontend/                  ← Web dashboard (HTML/JS/CSS)
        ├── index.html             ← Main dashboard
        ├── analytics.html         ← Analytics page
        └── ph-calibration.html    ← pH sensor calibration UI
```

---

## How to Run

### Step 1 – Hardware (ESP32)
1. Wire the sensors per `hardware/TODO_Assembly_Testing.md`
2. Open `hardware/arduino_firmware/AquaGuard_v2/AquaGuard_v2.ino` in Arduino IDE
3. Fill in the **3 required fields** at the top of the file:
   - `WIFI_SSID` / `WIFI_PASSWORD`
   - `FIREBASE_AUTH`  (your Firebase database secret)
   - `FASTAPI_HOST`   (local IP of the PC running the backend, e.g. `192.168.1.50`)
4. Flash to ESP32

### Step 2 – Software (double-click)
Double-click **`Run_AquaGuard.bat`**. It will:
- Start the FastAPI ML backend on **port 8000**
- Start the web dashboard server on **port 8080**
- Open your browser to the dashboard automatically

### Requirements (target PC must have Python installed)
```
pip install fastapi uvicorn pandas numpy scikit-learn xgboost joblib shap
```

---

## Data Flow (how everything connects)

```
ESP32 (AquaGuard_v2.ino)
  │
  ├──► Firebase Realtime Database
  │        └──► Web Dashboard (live sensor tiles, pump controls)
  │
  └──► POST http://<PC-IP>:8000/api/v1/iot-ingest
           ├── Logs to model_2/data/live_iot_log.csv
           ├── Runs Model 3 Anomaly Detection (Isolation Forest)
           └── Returns anomaly result to ESP32 Serial monitor

Web Dashboard ──► GET http://127.0.0.1:8000/api/v1/... (Flood + TDS forecasts)
```

---

## Sensors Wired (exact pins)

| Sensor | ESP32 Pin |
|---|---|
| pH Sensor (analog) | GPIO 34 |
| TDS Sensor (analog) | GPIO 35 |
| NTC Thermistor + 4.7kΩ | GPIO 32 |
| HC-SR04 TRIG | GPIO 5 |
| HC-SR04 ECHO (voltage divider) | GPIO 18 |
| Drain Pump Relay (active LOW) | GPIO 25 |
| Refill Pump Relay (active LOW) | GPIO 26 |
| Feeder Servo | GPIO 13 |

---

## ML Models Summary

| Model | Purpose | Algorithm | Endpoint |
|---|---|---|---|
| Model 1 | River flood water-level forecast (Bahadurabad) | Linear Regression | `GET /api/v1/forecast` |
| Model 2 | Pond TDS forecast +60 min | Linear Regression | `GET /api/v1/tds` |
| Model 3 | Pond water-quality anomaly detection | Isolation Forest | `GET /api/v1/anomaly` or auto-triggered by IoT ingest |
