"""FastAPI Web Backend for Bahadurabad Water Level Forecasting System.

Provides REST API endpoints for:
- Current station observations
- 1, 3, 7, 14-day AI Model Water Level Forecasts
- Danger Level alerts & Actionable Farmer Advice (English & Bengali)
- Historical 7-day hydrograph data for UI charting
"""

from __future__ import annotations

import datetime
from typing import Optional, List, Dict, Any
from fastapi import FastAPI, Query, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler

from src import config as C
from src import data as D
from src import features as F
from src import models as M
from src import ingestion as Ing

app = FastAPI(
    title="Bahadurabad Water Level Forecasting API",
    description="Real-time water level predictions, flood alerts, and farmer guidance for Bahadurabad Station (SW46.9L).",
    version="1.0.0"
)

# Enable CORS for Frontend Development (React / Next.js / Vue)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global model cache to avoid re-training on every API request
MODEL_CACHE = {}

def get_trained_model(horizon: int):
    """Load or train winning model for a given horizon."""
    if horizon in MODEL_CACHE:
        return MODEL_CACHE[horizon]
        
    df_raw = D.load_raw_data()
    df_rf = D.load_rainfall_data()
    df_feat, feature_sets = F.create_feature_sets(df_raw, df_rf)
    
    f_cols = feature_sets['B']
    df_common = F.prepare_common_dataset(df_feat, f_cols, horizon=horizon)
    dev_df = df_common[(df_common['Year'] >= C.DEV_START_YEAR) & (df_common['Year'] <= C.DEV_END_YEAR)]
    
    scaler = StandardScaler()
    X_train = scaler.fit_transform(dev_df[f_cols].values)
    y_train = dev_df[f'Delta_WL_target_h{horizon}'].values
    
    model = M.get_model_pipeline('LinearRegression')
    model.fit(X_train, y_train)
    
    MODEL_CACHE[horizon] = (model, scaler, f_cols)
    return MODEL_CACHE[horizon]

# Response Models
class ForecastHorizonResponse(BaseModel):
    horizon_days: int
    target_date: str
    predicted_level_m: float
    predicted_change_m: float
    status: str
    status_code: str
    color_hex: str
    advice_en: str
    advice_bn: str

class HydrographPoint(BaseModel):
    date: str
    level_m: float
    is_forecast: bool

class StationForecastResponse(BaseModel):
    station_name: str
    station_code: str
    danger_level_m: float
    extreme_level_m: float
    rhwl_m: float
    as_of_date: str
    current_level_m: float
    daily_change_cm: float
    catchment_rain_mm: float
    overall_risk_level: str
    forecasts: List[ForecastHorizonResponse]
    hydrograph: List[HydrographPoint]

def generate_farmer_advice(predicted_wl: float, horizon_days: int) -> tuple[str, str, str, str, str]:
    """Generate risk status, color, and bilingual aquaculture advice based on predicted water level.

    Advice is tailored for controlled pond fish farmers (tilapia, rohu, catla, pangasius)
    in the Jamuna/Brahmaputra floodplain districts: Jamalpur, Gaibandha, Sirajganj, Bogura,
    Tangail, and northern Mymensingh char areas.
    """
    if predicted_wl >= C.EXTREME_LEVEL:
        status = "EXTREME FLOOD ALERT"
        code   = "EXTREME"
        color  = "#8b0000"
        en = (
            f"+{horizon_days}d Forecast ({predicted_wl:.2f} m): EXTREME FLOOD IMMINENT. "
            f"Emergency-harvest ALL fish now — pond embankments will almost certainly breach "
            f"and fish will escape into floodwater. Remove cage frames, nets, and aerators to "
            f"high ground immediately. Stop all feeding. Do NOT restock ponds until floodwater "
            f"has fully receded and water quality (pH, DO, ammonia) has been re-tested and normalised."
        )
        bn = (
            f"+{horizon_days} দিনের পূর্বাভাস ({predicted_wl:.2f} মি): মারাত্মক বন্যা আসন্ন! "
            f"এখনই জরুরি ভিত্তিতে সব মাছ জাল টেনে তুলুন — পুকুরের পাড় ভেঙে "
            f"মাছ বেরিয়ে যেতে পারে। খাঁচার ফ্রেম, জাল ও বায়ুসঞ্চালক যন্ত্র উঁচু "
            f"স্থানে সরিয়ে নিন। খাবার বন্ধ রাখুন। বন্যার পানি সরে pH, DO ও "
            f"অ্যামোনিয়া পরীক্ষা না করে পুনরায় মাছ মজুদ করবেন না।"
        )
    elif predicted_wl >= C.DL:
        status = "DANGER LEVEL FLOOD"
        code   = "DANGER"
        color  = "#dc3545"
        en = (
            f"+{horizon_days}d Forecast ({predicted_wl:.2f} m): River crossing Danger Level. "
            f"Harvest marketable fish (>=250 g) immediately. Move fingerlings and juveniles to "
            f"a high-ground emergency nursery pond if available. Raise pond embankments by at "
            f"least 30 cm and seal all inlets/outlets with fine-mesh screens. If embankments "
            f"cannot be raised, fit strong barrier nets (20 mm mesh, 60 cm above water surface) "
            f"around the full pond perimeter. Suspend feeding to prevent water quality collapse."
        )
        bn = (
            f"+{horizon_days} দিনের পূর্বাভাস ({predicted_wl:.2f} মি): নদী বিপৎসীমা অতিক্রম করবে। "
            f"বিক্রযোগ্য মাছ (≥2৫0 গ্রাম) এখনই ধরুন। পোনা ও ছোট মাছ সম্ভব হলে "
            f"উঁচু জরুরি নার্সারি পুকুরে সরিয়ে দিন। পুকুরের পাড় কমপক্ষে "
            f"30 সেমি উঁচু করুন ও সব ইনলেট/আউটলেট বারিক জাল দিয়ে বন্ধ করুন। "
            f"পাড় উঁচু করা সম্ভব না হলে পুকুরের চারপাশে বাধা জাল "
            f"(20 মিমি ফাঁস, পানির উপরে 60 সেমি) লাগান। খাবার বন্ধ রাখুন।"
        )
    elif predicted_wl >= C.CONFIG["thresholds"]["warning_level"]:
        status = "WARNING (RISING RIVER)"
        code   = "WARNING"
        color  = "#ffc107"
        en = (
            f"+{horizon_days}d Forecast ({predicted_wl:.2f} m): River rising — pond risk elevated "
            f"within {horizon_days} days. Inspect ALL pond embankments for cracks, seepage, or "
            f"soft spots and repair with clay compaction immediately. Check and reinforce "
            f"anti-escape barrier nets at inlets and outlets. Reduce daily feed ration by "
            f"30-50% to lower ammonia load. Start partial harvest of large fish (>=300 g) to "
            f"reduce stocking density before floodwater arrives."
        )
        bn = (
            f"+{horizon_days} দিনের পূর্বাভাস ({predicted_wl:.2f} মি): নদীর পানি বাড়ছে — {horizon_days} দিনের মধ্যে "
            f"পুকুর ঝুঁকিতে পড়তে পারে। সব পুকুরের পাড়ে ফাটল, রিসাব বা নরম "
            f"দাগ আছে কিনা পরীক্ষা করে মাটি ঠাসা দিয়ে মেরামত করুন। "
            f"ইনলেট/আউটলেটে মাছ-পালানো-রোধী জাল পরীক্ষা ও মজবুত করুন। "
            f"অ্যামোনিয়া কমাতে দৈনিক খাবার 30–50% কমিয়ে দিন। "
            f"বড় মাছ (≥300 গ্রাম) আংশিকভাবে তুলে মজুদ ঘনত্ব কমাতে শুরু করুন।"
        )
    else:
        status = "NORMAL LEVEL"
        code   = "NORMAL"
        color  = "#28a745"
        en = (
            f"+{horizon_days}d Forecast ({predicted_wl:.2f} m): River within safe range. "
            f"Normal pond management can continue. Monitor dissolved oxygen (>5 mg/L) and "
            f"pH (6.5-8.5) daily. Good time for regular feeding, pond liming/fertilisation, "
            f"and routine stocking density assessment."
        )
        bn = (
            f"+{horizon_days} দিনের পূর্বাভাস ({predicted_wl:.2f} মি): নদীর পানি স্বাভাবিক সীমায় আছে। "
            f"স্বাভাবিক পুকুর ব্যবস্থাপনা চালিয়ে যান। "
            f"প্রতিদিন দ্রবীভূত অক্সিজেন (>5 মিগ্রা/লি) ও pH (6.5-8.5) পরীক্ষা করুন। "
            f"নিয়মিত খাবার, পুকুরে চুন/সার প্রয়োগ ও মাছের মজুদ মূল্যায়নের উপযুক্ত সময়।"
        )

    return status, code, color, en, bn


@app.get("/", tags=["Health"])
def root():
    return {
        "status": "online",
        "system": "Bahadurabad Water Level Forecasting API",
        "station": C.STATION,
        "danger_level_m": C.DL,
        "docs_url": "/docs"
    }

@app.get("/api/v1/forecast", response_model=StationForecastResponse, tags=["Forecasting"])
def get_station_forecast(
    date: Optional[str] = Query(None, description="Date YYYY-MM-DD (defaults to latest recorded date)"),
    force_refresh: bool = Query(False, description="Force run live ingestion pipeline")
):
    """
    Main API endpoint for Farmers & Web Dashboard.
    
    Returns:
    - Today's current gauge observation & rainfall
    - AI Model Predictions for +1, +3, +7, and +14 days
    - Color-coded flood risk levels & Actionable advice (English + Bengali)
    - 7-day past + future hydrograph series for web charting
    """
    if date is None:
        date = datetime.date.today().strftime("%Y-%m-%d")
        
    # Ingest / ensure data is up to date
    try:
        df_live = Ing.ingest_daily_data(date)
    except Exception as e:
        # Fallback to local raw file
        df_raw = D.load_raw_data()
        df_rf = D.load_rainfall_data()
        df_live, _ = F.create_feature_sets(df_raw, df_rf)

    df_feat, feature_sets = F.create_feature_sets(df_live)
    f_cols = feature_sets['B']
    
    target_dt = pd.to_datetime(date)
    sub_df = df_feat[df_feat['Date'] <= target_dt].copy()
    
    if len(sub_df) < 30:
        raise HTTPException(status_code=400, detail="Insufficient lookback window for feature generation.")
        
    latest_row = sub_df.iloc[-1]
    curr_date_str = latest_row['Date'].strftime("%Y-%m-%d")
    curr_wl = float(latest_row['WL'])
    
    # 1-day change in cm
    prev_wl = float(sub_df.iloc[-2]['WL']) if len(sub_df) >= 2 else curr_wl
    daily_change_cm = (curr_wl - prev_wl) * 100.0
    catchment_rain = float(latest_row.get('Rainfall_Catchment', 0.0)) if not pd.isna(latest_row.get('Rainfall_Catchment')) else 0.0
    
    # Forecast across horizons
    forecast_list = []
    max_risk_code = "NORMAL"
    
    for h in C.HORIZONS:
        model, scaler, _ = get_trained_model(h)
        
        feat_vector = latest_row[f_cols].values.reshape(1, -1)
        feat_vector_scaled = scaler.transform(feat_vector)
        
        pred_delta = float(model.predict(feat_vector_scaled)[0])
        pred_wl = curr_wl + pred_delta
        target_date_str = (latest_row['Date'] + pd.Timedelta(days=h)).strftime("%Y-%m-%d")
        
        status, code, color, en, bn = generate_farmer_advice(pred_wl, h)
        
        if code == "EXTREME":
            max_risk_code = "EXTREME"
        elif code == "DANGER" and max_risk_code != "EXTREME":
            max_risk_code = "DANGER"
        elif code == "WARNING" and max_risk_code not in ["DANGER", "EXTREME"]:
            max_risk_code = "WARNING"
            
        forecast_list.append(ForecastHorizonResponse(
            horizon_days=h,
            target_date=target_date_str,
            predicted_level_m=round(pred_wl, 2),
            predicted_change_m=round(pred_delta, 2),
            status=status,
            status_code=code,
            color_hex=color,
            advice_en=en,
            advice_bn=bn
        ))
        
    # Build Hydrograph series (Past 7 days + Future 14 days)
    past_7 = sub_df.iloc[-7:]
    hydrograph = []
    for _, row in past_7.iterrows():
        hydrograph.append(HydrographPoint(
            date=row['Date'].strftime("%Y-%m-%d"),
            level_m=round(float(row['WL']), 2),
            is_forecast=False
        ))
        
    for fc in forecast_list:
        hydrograph.append(HydrographPoint(
            date=fc.target_date,
            level_m=fc.predicted_level_m,
            is_forecast=True
        ))
        
    return StationForecastResponse(
        station_name=C.STATION,
        station_code=C.STATION_CODE,
        danger_level_m=C.DL,
        extreme_level_m=C.EXTREME_LEVEL,
        rhwl_m=C.RHWL,
        as_of_date=curr_date_str,
        current_level_m=round(curr_wl, 2),
        daily_change_cm=round(daily_change_cm, 1),
        catchment_rain_mm=round(catchment_rain, 1),
        overall_risk_level=max_risk_code,
        forecasts=forecast_list,
        hydrograph=hydrograph
    )

@app.post("/api/v1/ingest", tags=["Ingestion"])
def trigger_ingest(date: Optional[str] = None):
    """Trigger manual or webhook daily data ingestion."""
    df_out = Ing.ingest_daily_data(date)
    return {
        "status": "success",
        "message": f"Ingestion completed. Total dataset size: {len(df_out)} rows.",
        "latest_date": df_out.iloc[-1]['Date'].strftime("%Y-%m-%d")
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
