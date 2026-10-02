# AquaGuard — How to Run Locally

The system is fully portable. Copy this project to any machine, run two steps, and you have the full system running.

---

## Prerequisites (one-time per machine)

- **Python 3.9+** — check with `python --version`
- A modern web browser (Chrome, Edge, Firefox)

---

## Step 1 — Install Dependencies (once per machine)

```bash
cd new_models/new_approach
pip install -r requirements.txt
```

Installs: FastAPI, Uvicorn, Pandas, NumPy, Scikit-Learn, XGBoost, SHAP, Matplotlib, Seaborn.

---

## Step 2 — Start the ML Backend

Open a terminal and run:

```bash
cd new_models/new_approach
python -m uvicorn api_combined:app --host 0.0.0.0 --port 8000 --reload
```

**Success:** You will see `Uvicorn running on http://0.0.0.0:8000`

Keep this terminal open. View API docs at: `http://127.0.0.1:8000/docs`

---

## Step 3 — Open the Dashboard

Double-click `frontend/index.html` in your browser.

*(Recommended: use VS Code's Live Server extension for best experience.)*

---

## What You Will See

| Section | Powered By | What It Shows |
|---|---|---|
| Live Sensor Tiles | Firebase Realtime DB | pH, TDS, Water Temp, Water Level, Pump controls |
| 🌊 Bahadurabad Forecast | Model 1 (`/api/v1/forecast`) | 14-day river water level forecast, hydrograph, bilingual advice |
| 🔮 Water Quality AI | Model 2 (`/api/v1/tds`) | Predicted pond TDS in 60 minutes, trend indicator |
| 🛡️ Anomaly Detection | Model 3 (`/api/v1/anomaly`) | Isolation Forest status + "Simulate Spike" demo button |

---

## API Endpoints Reference

| Endpoint | Model | Returns |
|---|---|---|
| `GET /api/v1/forecast` | Model 1 | 14-day water levels, risk level, bilingual farmer advice, hydrograph data |
| `GET /api/v1/tds` | Model 2 | Current TDS, predicted TDS (+60 min), trend |
| `GET /api/v1/anomaly` | Model 3 | Anomaly status, score, message |
| `GET /api/v1/anomaly?pH=9.5&tds=450&temp=33` | Model 3 | Force a spike simulation |
| `GET /docs` | All | Auto-generated Swagger API documentation |

---

## Troubleshooting

| Problem | Fix |
|---|---|
| Dashboard shows "Forecast service offline" | The backend terminal is not running. Start it with the Step 2 command above. |
| Python not found | Ensure Python is added to system PATH during installation. |
| Missing module error | Run `pip install -r requirements.txt` inside `new_models/new_approach/`. |
| Live sensors show `--` | The ESP32 firmware has not been flashed yet. See `hardware/AquaGuard_v2/README.md`. |

---

## Developer Handoff

A self-contained portable copy of everything (frontend + all 3 model backends + saved .pkl files) is at:

```
new_models/new_approach/AquaGuard_Web_Bundle/
```

Zip that folder and send it. The recipient follows these exact same steps. No changes to paths needed — all code uses relative paths.
