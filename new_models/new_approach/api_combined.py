"""
AquaGuard Unified ML API  v3.0
================================
Endpoints
---------
GET  /                        Health check
GET  /api/v1/tds              Model 2 – TDS +60min forecast
GET  /api/v1/anomaly          Model 3 – Anomaly detection (query params)
POST /api/v1/iot-ingest       Receive live ESP32 telemetry (Firebase bridge)
GET  /api/v1/iot-latest       Return last live reading (for optional UI polling)
All Model 1 (Flood) routes are mounted via the flood_api router.

Data flow matches the project diagrams:
  ESP32 ──► Firebase RTDB  (web dashboard live tiles, pump control)
        └──► POST /api/v1/iot-ingest  (this file)
                 ├── appends live_iot_log.csv  (rolling history)
                 ├── runs Model 3 anomaly detection  ──► returns result to ESP32
                 └── result is also available at /api/v1/iot-latest for UI

Model 3 feature contract (must match pipeline_anomaly.py):
  Features: pH, TDS, temperature, pH_change, TDS_change, temp_change
  Model fitted on RAW (unscaled) values – scaler.pkl not used at inference.
"""

import sys
import os
import csv
from datetime import datetime
from typing import Optional

import joblib
import numpy as np
import pandas as pd
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# ---------------------------------------------------------------------------
# Path setup – add model_1_flood so we can import its modules
# ---------------------------------------------------------------------------
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "model_1_flood"))

try:
    import api as flood_api
except ImportError:
    flood_api = None

# ---------------------------------------------------------------------------
# App
# ---------------------------------------------------------------------------
app = FastAPI(title="AquaGuard Unified ML API", version="3.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

if flood_api:
    app.include_router(flood_api.app.router)

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
BASE = os.path.dirname(__file__)
M2_PATH = os.path.join(BASE, "model_2")
M3_PATH = os.path.join(BASE, "model_3")
LIVE_LOG = os.path.join(M2_PATH, "data", "live_iot_log.csv")

# ---------------------------------------------------------------------------
# Load Model 2 (TDS – Linear Regression)
# ---------------------------------------------------------------------------
try:
    tds_model = joblib.load(os.path.join(M2_PATH, "outputs", "models", "linear_regression.pkl"))
    tds_data = pd.read_csv(os.path.join(M2_PATH, "data", "pond_iot_2023.csv"))
    tds_data["created_date"] = pd.to_datetime(tds_data["created_date"])
    tds_data = tds_data.set_index("created_date").sort_index()
    tds_hourly = (
        tds_data[["water_pH", "TDS", "water_temp"]]
        .resample("1h").mean()
        .interpolate(method="linear", limit=3)
        .ffill()
        .dropna()
    )
    tds_hourly.rename(columns={"water_pH": "pH", "water_temp": "temperature"}, inplace=True)
    print("Model 2 (TDS) loaded OK.")
except Exception as e:
    tds_model = None
    tds_hourly = None
    print(f"Warning: Model 2 not loaded – {e}")

# ---------------------------------------------------------------------------
# Load Model 3 (Anomaly – Isolation Forest)
# Features expected: pH, TDS, temperature, pH_change, TDS_change, temp_change
# Fitted on RAW values (pipeline_anomaly.py fits on X, not X_scaled).
# ---------------------------------------------------------------------------
try:
    anomaly_model = joblib.load(os.path.join(M3_PATH, "outputs", "models", "isolation_forest.pkl"))
    print("Model 3 (Anomaly) loaded OK.")
except Exception as e:
    anomaly_model = None
    print(f"Warning: Model 3 not loaded – {e}")

# Historical means for delta computation when only one reading arrives live
_hist_means = {}
if tds_hourly is not None:
    _hist_means = {
        "pH":          tds_hourly["pH"].mean(),
        "TDS":         tds_hourly["TDS"].mean(),
        "temperature": tds_hourly["temperature"].mean(),
    }

# ---------------------------------------------------------------------------
# Helper – run anomaly model with correct feature contract
# ---------------------------------------------------------------------------
def _run_anomaly(ph: float, tds: float, temp: float,
                 ph_prev: float = None, tds_prev: float = None, temp_prev: float = None):
    """
    Returns (status_str, score_float) or raises.
    Delta features fall back to historical mean when no previous value given.
    """
    if anomaly_model is None:
        return "Model not loaded", 0.0

    ph_change   = (ph   - ph_prev)   if ph_prev   is not None else (ph   - _hist_means.get("pH", ph))
    tds_change  = (tds  - tds_prev)  if tds_prev  is not None else (tds  - _hist_means.get("TDS", tds))
    temp_change = (temp - temp_prev) if temp_prev is not None else (temp - _hist_means.get("temperature", temp))

    X = pd.DataFrame([{
        "pH":          ph,
        "TDS":         tds,
        "temperature": temp,
        "pH_change":   ph_change,
        "TDS_change":  tds_change,
        "temp_change": temp_change,
    }])

    pred  = anomaly_model.predict(X)[0]
    score = float(anomaly_model.decision_function(X)[0])
    status = "NORMAL" if pred == 1 else "ANOMALY DETECTED"
    return status, score


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------

@app.get("/")
def read_root():
    return {"status": "online", "models": ["flood", "tds", "anomaly"]}


# --- Model 2: TDS Forecast ---
@app.get("/api/v1/tds")
def predict_tds():
    """Predict pond TDS +60 minutes using last available historical row."""
    if tds_model is None or tds_hourly is None:
        return {"error": "Model 2 not loaded"}

    df_feat = tds_hourly.copy()
    df_feat["hour"]        = df_feat.index.hour
    df_feat["day_of_week"] = df_feat.index.dayofweek
    for lag in [1, 2, 3, 6, 12]:
        df_feat[f"TDS_t-{lag}"]         = df_feat["TDS"].shift(lag)
    for lag in [1, 2, 3]:
        df_feat[f"pH_t-{lag}"]          = df_feat["pH"].shift(lag)
        df_feat[f"temperature_t-{lag}"] = df_feat["temperature"].shift(lag)
    df_feat["TDS_rolling_mean"]         = df_feat["TDS"].shift(1).rolling(6).mean()
    df_feat["TDS_rolling_std"]          = df_feat["TDS"].shift(1).rolling(6).std()
    df_feat["pH_rolling_mean"]          = df_feat["pH"].shift(1).rolling(6).mean()
    df_feat["temperature_rolling_mean"] = df_feat["temperature"].shift(1).rolling(6).mean()
    df_feat.dropna(inplace=True)

    last_row = df_feat.iloc[-1:]
    features = [c for c in df_feat.columns if c not in ["TDS", "pH", "temperature"]]
    pred_tds = float(tds_model.predict(last_row[features])[0])
    curr_tds = float(last_row["TDS"].values[0])

    trend = ("INCREASING" if pred_tds > curr_tds + 2
             else "DECREASING" if pred_tds < curr_tds - 2
             else "STABLE")

    return {
        "current_tds":        round(curr_tds, 1),
        "predicted_tds_60min": round(pred_tds, 1),
        "trend":               trend,
    }


# --- Model 3: Anomaly Detection (query params) ---
@app.get("/api/v1/anomaly")
def detect_anomaly(pH: float = None, tds: float = None, temp: float = None):
    """
    Detect anomalies. Pass live sensor values as query params for interactive testing.
    Falls back to last historical row if none provided.
    """
    if anomaly_model is None:
        return {"error": "Model 3 not loaded"}

    if pH is not None and tds is not None and temp is not None:
        status, score = _run_anomaly(pH, tds, temp)
    else:
        # Use last historical row with real deltas
        if tds_hourly is None:
            return {"error": "No historical data available"}
        df_feat = tds_hourly.copy()
        df_feat["pH_change"]   = df_feat["pH"].diff()
        df_feat["TDS_change"]  = df_feat["TDS"].diff()
        df_feat["temp_change"] = df_feat["temperature"].diff()
        df_feat.dropna(inplace=True)
        row = df_feat.iloc[-1]
        status, score = _run_anomaly(
            row["pH"], row["TDS"], row["temperature"],
            row["pH"] - row["pH_change"],
            row["TDS"] - row["TDS_change"],
            row["temperature"] - row["temp_change"],
        )

    return {
        "status":        status,
        "anomaly_score": round(score, 4),
        "message":       "No unusual sensor pattern" if status == "NORMAL"
                         else "Warning: Unusual water condition detected!",
    }


# --- IoT Ingest: receive live ESP32 telemetry ---
class SensorPayload(BaseModel):
    temperature:      Optional[float] = None   # NaN-safe: firmware sends null if ADC invalid
    ph:               Optional[float] = None   # null when not yet calibrated
    tds:              float
    water_distance_cm: float


@app.post("/api/v1/iot-ingest")
def ingest_iot_data(data: SensorPayload):
    """
    Called by AquaGuard_v2.ino postToFastAPI() every UPLOAD_INTERVAL.
    1. Appends row to live_iot_log.csv
    2. Runs Model 3 anomaly detection with delta vs previous row
    3. Returns anomaly result to ESP32 Serial monitor
    """
    ts = datetime.now().isoformat()

    # --- 1. Append to rolling CSV log ---
    file_exists = os.path.isfile(LIVE_LOG)
    with open(LIVE_LOG, mode="a", newline="") as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow(["timestamp", "temperature", "ph", "tds", "water_distance_cm"])
        writer.writerow([ts, data.temperature, data.ph, data.tds, data.water_distance_cm])

    # --- 2. Anomaly detection ---
    anomaly_status = "Skipped (pH not calibrated)"
    anomaly_score  = None

    if data.ph is not None and data.temperature is not None:
        # Load previous row for delta computation
        ph_prev = tds_prev = temp_prev = None
        try:
            df_log = pd.read_csv(LIVE_LOG)
            if len(df_log) >= 2:
                prev = df_log.iloc[-2]
                ph_prev   = prev["ph"]   if pd.notna(prev["ph"])          else None
                tds_prev  = prev["tds"]  if pd.notna(prev["tds"])         else None
                temp_prev = prev["temperature"] if pd.notna(prev["temperature"]) else None
        except Exception:
            pass

        try:
            anomaly_status, anomaly_score = _run_anomaly(
                data.ph, data.tds, data.temperature,
                ph_prev, tds_prev, temp_prev
            )
        except Exception as e:
            anomaly_status = f"Error: {e}"

    return {
        "status":         "success",
        "timestamp":      ts,
        "anomaly_status": anomaly_status,
        "anomaly_score":  round(anomaly_score, 4) if anomaly_score is not None else None,
    }


# --- Latest live reading (optional frontend polling) ---
@app.get("/api/v1/iot-latest")
def get_latest_iot():
    """Return the most recent ESP32 reading from the live log."""
    if not os.path.isfile(LIVE_LOG):
        return {"error": "No live data yet – waiting for ESP32"}
    try:
        df = pd.read_csv(LIVE_LOG)
        if df.empty:
            return {"error": "Log exists but is empty"}
        latest = df.iloc[-1].to_dict()

        # Re-run anomaly on the stored values so the UI always gets a fresh result
        anomaly_status = "Skipped (pH not calibrated)"
        if pd.notna(latest.get("ph")) and pd.notna(latest.get("temperature")):
            ph_prev = tds_prev = temp_prev = None
            if len(df) >= 2:
                prev = df.iloc[-2]
                ph_prev   = prev["ph"]          if pd.notna(prev["ph"])          else None
                tds_prev  = prev["tds"]         if pd.notna(prev["tds"])         else None
                temp_prev = prev["temperature"] if pd.notna(prev["temperature"]) else None
            try:
                anomaly_status, _ = _run_anomaly(
                    latest["ph"], latest["tds"], latest["temperature"],
                    ph_prev, tds_prev, temp_prev
                )
            except Exception:
                pass

        latest["anomaly_status"] = anomaly_status
        return latest
    except Exception as e:
        return {"error": str(e)}


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
