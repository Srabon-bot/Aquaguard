import sys
import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd
import numpy as np
import joblib

# Add model_1 path so we can import its modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "model_1_flood"))

# Import Model 1 API endpoints
try:
    import api as flood_api
except ImportError:
    flood_api = None

app = FastAPI(title="AquaGuard Unified ML API", version="2.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include Model 1 (Flood) router/endpoints if available
if flood_api:
    # Add the route directly so the frontend doesn't break
    app.include_router(flood_api.app.router)


# Paths for Models 2 & 3
M2_PATH = os.path.join(os.path.dirname(__file__), "model_2")
M3_PATH = os.path.join(os.path.dirname(__file__), "model_3")

# Load Model 2 (TDS Linear Regression)
try:
    tds_model = joblib.load(os.path.join(M2_PATH, "outputs", "models", "linear_regression.pkl"))
    # Load dataset to simulate live features for demo
    tds_data = pd.read_csv(os.path.join(M2_PATH, "data", "pond_iot_2023.csv"))
    tds_data['created_date'] = pd.to_datetime(tds_data['created_date'])
    tds_data = tds_data.set_index('created_date').sort_index()
    tds_hourly = tds_data[['water_pH', 'TDS', 'water_temp']].resample('1h').mean().interpolate(method='linear', limit=3).ffill().dropna()
    tds_hourly.rename(columns={'water_pH': 'pH', 'water_temp': 'temperature'}, inplace=True)
except Exception as e:
    tds_model = None
    print("Warning: Model 2 not fully loaded", e)

# Load Model 3 (Anomaly Isolation Forest)
try:
    anomaly_model = joblib.load(os.path.join(M3_PATH, "outputs", "models", "isolation_forest.pkl"))
except Exception as e:
    anomaly_model = None
    print("Warning: Model 3 not fully loaded", e)

@app.get("/")
def read_root():
    return {"status": "online", "models": ["flood", "tds", "anomaly"]}

# --- Model 2 Endpoint ---
@app.get("/api/v1/tds")
def predict_tds():
    """Predict TDS +60 mins using the last available row in the dataset (Simulating live data)."""
    if not tds_model:
        return {"error": "Model not loaded"}
    
    # Rebuild features for the last row
    df_feat = tds_hourly.copy()
    df_feat['hour'] = df_feat.index.hour
    df_feat['day_of_week'] = df_feat.index.dayofweek
    for lag in [1, 2, 3, 6, 12]: df_feat[f'TDS_t-{lag}'] = df_feat['TDS'].shift(lag)
    for lag in [1, 2, 3]: df_feat[f'pH_t-{lag}'] = df_feat['pH'].shift(lag)
    for lag in [1, 2, 3]: df_feat[f'temperature_t-{lag}'] = df_feat['temperature'].shift(lag)
    df_feat['TDS_rolling_mean'] = df_feat['TDS'].shift(1).rolling(window=6).mean()
    df_feat['TDS_rolling_std'] = df_feat['TDS'].shift(1).rolling(window=6).std()
    df_feat['pH_rolling_mean'] = df_feat['pH'].shift(1).rolling(window=6).mean()
    df_feat['temperature_rolling_mean'] = df_feat['temperature'].shift(1).rolling(window=6).mean()
    
    df_feat = df_feat.dropna()
    last_row = df_feat.iloc[-1:]
    
    features = [c for c in df_feat.columns if c not in ['TDS', 'pH', 'temperature']]
    X = last_row[features]
    
    pred_tds = tds_model.predict(X)[0]
    curr_tds = last_row['TDS'].values[0]
    
    trend = "INCREASING" if pred_tds > curr_tds + 2 else ("DECREASING" if pred_tds < curr_tds - 2 else "STABLE")
    
    return {
        "current_tds": round(float(curr_tds), 1),
        "predicted_tds_60min": round(float(pred_tds), 1),
        "trend": trend
    }

# --- Model 3 Endpoint ---
@app.get("/api/v1/anomaly")
def detect_anomaly(pH: float = None, tds: float = None, temp: float = None):
    """
    Detect anomalies. Accepts current sensor readings via GET params to allow interactive UI testing.
    If none provided, uses the last row of the dataset.
    """
    if not anomaly_model:
        return {"error": "Model not loaded"}
    
    # Build a simulated delta (comparing input against previous average)
    if pH and tds and temp:
        # Simulate a sudden change from the historical mean
        mean_pH = tds_hourly['pH'].mean()
        mean_tds = tds_hourly['TDS'].mean()
        mean_temp = tds_hourly['temperature'].mean()
        
        X = pd.DataFrame([{
            'pH': pH,
            'TDS': tds,
            'temperature': temp,
            'pH_change': pH - mean_pH,
            'TDS_change': tds - mean_tds,
            'temp_change': temp - mean_temp
        }])
    else:
        # Use last row of dataset to generate features
        df_feat = tds_hourly.copy()
        df_feat['pH_change'] = df_feat['pH'].diff()
        df_feat['TDS_change'] = df_feat['TDS'].diff()
        df_feat['temp_change'] = df_feat['temperature'].diff()
        df_feat = df_feat.dropna()
        X = df_feat[['pH', 'TDS', 'temperature', 'pH_change', 'TDS_change', 'temp_change']].iloc[-1:]
    
    prediction = anomaly_model.predict(X)[0]
    score = anomaly_model.decision_function(X)[0]
    
    status = "NORMAL" if prediction == 1 else "ANOMALY DETECTED"
    
    return {
        "status": status,
        "anomaly_score": round(float(score), 3),
        "message": "No unusual sensor pattern" if status == "NORMAL" else "Warning: Unusual water condition detected!"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
