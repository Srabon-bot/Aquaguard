import numpy as np
import pandas as pd
from src import config as C

def compute_overall_metrics(y_true, y_pred):
    """Compute RMSE, MAE, Bias, and NSE."""
    y_true = np.asarray(y_true)
    y_pred = np.asarray(y_pred)
    
    rmse = np.sqrt(np.mean((y_pred - y_true) ** 2))
    mae = np.mean(np.abs(y_pred - y_true))
    bias = np.mean(y_pred - y_true)
    
    denom = np.sum((y_true - np.mean(y_true)) ** 2)
    nse = 1.0 - (np.sum((y_pred - y_true) ** 2) / denom) if denom != 0 else np.nan
    
    return {
        'RMSE': rmse,
        'MAE': mae,
        'Bias': bias,
        'NSE': nse
    }

def compute_flood_season_rmse(df_eval):
    """Compute RMSE during flood season (June-September)."""
    monsoon = df_eval[df_eval['Month'].isin([6, 7, 8, 9])]
    if len(monsoon) == 0:
        return np.nan
    rmse = np.sqrt(np.mean((monsoon['y_pred'] - monsoon['y_true']) ** 2))
    return rmse

def compute_binned_rmse(df_eval):
    """Compute RMSE across water level bins."""
    bins = {
        '< 17m': df_eval[df_eval['y_true'] < 17.0],
        '17 - 19m': df_eval[(df_eval['y_true'] >= 17.0) & (df_eval['y_true'] < 19.0)],
        '19 - 19.9m': df_eval[(df_eval['y_true'] >= 19.0) & (df_eval['y_true'] < 19.9)],
        '> 19.9m': df_eval[df_eval['y_true'] >= 19.9]
    }
    binned_rmse = {}
    for name, sub in bins.items():
        if len(sub) > 0:
            binned_rmse[name] = np.sqrt(np.mean((sub['y_pred'] - sub['y_true']) ** 2))
        else:
            binned_rmse[name] = np.nan
    return binned_rmse

def compute_peak_error(df_eval, events_df):
    """Compute Mean Absolute Error at flood event peaks."""
    peak_dates = set(events_df['peak_date'])
    sub = df_eval[df_eval['Target_Date'].isin(peak_dates)]
    if len(sub) == 0:
        return np.nan
    mae_peak = np.mean(np.abs(sub['y_pred'] - sub['y_true']))
    return mae_peak

def compute_skill_score(rmse_model, rmse_baseline):
    """Skill score relative to baseline."""
    if np.isnan(rmse_baseline) or rmse_baseline == 0:
        return np.nan
    return 1.0 - (rmse_model / rmse_baseline)

def compute_event_metrics(df_eval, events_df, threshold=C.DL):
    """
    Event scoring for danger level exceedance (19.05 m).
    
    Evaluates whether the forecast made at t predicts crossing DL at t+h 
    when observed level at t was still below DL.
    """
    # Exceedance indicators
    observed_exceed = df_eval['y_true'] >= threshold
    predicted_exceed = df_eval['y_pred'] >= threshold
    
    hits = np.sum(observed_exceed & predicted_exceed)
    misses = np.sum(observed_exceed & (~predicted_exceed))
    false_alarms = np.sum((~observed_exceed) & predicted_exceed)
    correct_negatives = np.sum((~observed_exceed) & (~predicted_exceed))
    
    pod = hits / (hits + misses) if (hits + misses) > 0 else 0.0
    far = false_alarms / (hits + false_alarms) if (hits + false_alarms) > 0 else 0.0
    csi = hits / (hits + misses + false_alarms) if (hits + misses + false_alarms) > 0 else 0.0
    
    return {
        'Hits': hits,
        'Misses': misses,
        'False_Alarms': false_alarms,
        'POD_HitRate': pod,
        'FAR': far,
        'CSI': csi
    }
