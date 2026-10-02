# AquaGuard
**Bangladesh Flood Early Warning + IoT Pond Management System**
*Final-year capstone project*

---

## What This Is

AquaGuard has two connected parts:

1. **IoT Pond Management System** — an ESP32 device with sensors and pumps that monitors a fish pond and pushes live data to the cloud.
2. **Flood Early Warning AI** — three machine learning models that warn fish farmers of flood risk and water quality problems, displayed on a web dashboard.

---

## Project Map (Current Version)

```
pred_flood/
├── frontend/              ← Web dashboard (HTML / JS / CSS)
├── hardware/              ← ESP32 firmware + sensor rebuild docs
├── new_models/
│   └── new_approach/      ← All 3 ML models + unified API
│       ├── api_combined.py        ← START HERE: runs all 3 models on port 8000
│       ├── requirements.txt
│       ├── model_1_flood/         ← River Water-Level Forecasting (Bahadurabad / Jamuna)
│       ├── model_2/               ← Pond TDS Forecasting (+60 min)
│       ├── model_3/               ← Pond Anomaly Detection (Isolation Forest)
│       └── AquaGuard_Web_Bundle/  ← Portable copy for developer handoff
├── reports/
│   └── project-report/    ← Main project report (PDF + MD)
├── DEFENSE_STRATEGY.md    ← How to present to the defense board
├── HOW_TO_RUN_AQUAGUARD.md ← How to run the full system locally
└── _legacy/               ← Archived outdated files (old 3-model system, old backend, etc.)
```

---

## Running the System

### Step 1 — Start the ML Backend (keep terminal open)
```bash
cd new_models/new_approach
pip install -r requirements.txt       # first time only
python -m uvicorn api_combined:app --host 0.0.0.0 --port 8000 --reload
```

API docs auto-open at: `http://127.0.0.1:8000/docs`

### Step 2 — Open the Dashboard
Double-click `frontend/index.html` in your browser (or use VS Code Live Server).

---

## The Three ML Models

| Model | What It Does | API Endpoint |
|---|---|---|
| **Model 1** | Predicts Bahadurabad (Jamuna) river water level 1–14 days ahead | `GET /api/v1/forecast` |
| **Model 2** | Predicts pond TDS (water quality) 60 minutes ahead | `GET /api/v1/tds` |
| **Model 3** | Detects unusual pond sensor combinations (Isolation Forest) | `GET /api/v1/anomaly` |

Coverage: Jamuna River floodplain — Jamalpur, Gaibandha, Sirajganj, Bogura, Tangail.

---

## Hardware

ESP32 with 4 sensors (pH, TDS, Ultrasonic water level, Thermistor temperature), 2 pumps (via relay), and a servo — all wired, tested, and fully documented. The combined firmware (`hardware/AquaGuard_v2/AquaGuard_v2.ino`) is ready to flash. See `hardware/AquaGuard_v2/README.md` for the 2 values to fill in before flashing.

---

## For Defense Preparation
- `DEFENSE_STRATEGY.md` — How to frame the project to the board
- `new_models/new_approach/AQUAGUARD_ML_FINAL_REPORT.md` — Full ML technical report
- `new_models/new_approach/DETAILED_VISUAL_REPORT.md` — Report with all plots embedded (export to PDF)
- `reports/project-report/PROJECT_REPORT.md` — Full project report
