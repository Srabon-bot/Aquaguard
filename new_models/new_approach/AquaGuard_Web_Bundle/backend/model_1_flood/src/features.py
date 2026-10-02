import pandas as pd
import numpy as np
from src import config as C

def create_feature_sets(df, df_rf=None):
    """
    Construct feature sets A, B, C, D and targets for horizons h in [1, 3, 7, 14].
    
    Target defined as: Delta_WL_h = WL(t+h) - WL(t).
    To evaluate: Predicted_WL(t+h) = WL(t) + Predicted_Delta_WL_h.
    """
    df = df.copy()
    
    # Merge rainfall if provided
    if df_rf is not None:
        df = pd.merge(df, df_rf, on='Date', how='left')
    
    # Base target values
    for h in C.HORIZONS:
        df[f'WL_target_h{h}'] = df['WL'].shift(-h)
        df[f'Delta_WL_target_h{h}'] = df[f'WL_target_h{h}'] - df['WL']
    
    # --- Feature Set A: Lags 0-7 ---
    feature_cols_A = []
    for lag in C.LAGS:
        col = f'WL_lag_{lag}'
        df[col] = df['WL'].shift(lag)
        feature_cols_A.append(col)
        
    # --- Feature Set B: Set A + changes, rolling stats, annual harmonics ---
    feature_cols_B = list(feature_cols_A)
    
    # Day-over-day changes
    df['Delta_1d'] = df['WL'] - df['WL_lag_1']
    df['Delta_3d'] = df['WL'] - df['WL_lag_3']
    df['Delta_7d'] = df['WL'] - df['WL_lag_7']
    feature_cols_B.extend(['Delta_1d', 'Delta_3d', 'Delta_7d'])
    
    # Rolling stats over 3 and 7 days (computed using past values up to t)
    df['WL_roll3_mean'] = df['WL'].rolling(3).mean()
    df['WL_roll3_std'] = df['WL'].rolling(3).std()
    df['WL_roll7_mean'] = df['WL'].rolling(7).mean()
    df['WL_roll7_std'] = df['WL'].rolling(7).std()
    df['WL_roll7_min'] = df['WL'].rolling(7).min()
    df['WL_roll7_max'] = df['WL'].rolling(7).max()
    feature_cols_B.extend(['WL_roll3_mean', 'WL_roll3_std', 'WL_roll7_mean', 'WL_roll7_std', 'WL_roll7_min', 'WL_roll7_max'])
    
    # Annual harmonics (sine / cosine of day of year)
    doy = df['Date'].dt.dayofyear
    df['sin_doy'] = np.sin(2 * np.pi * doy / 365.25)
    df['cos_doy'] = np.cos(2 * np.pi * doy / 365.25)
    feature_cols_B.extend(['sin_doy', 'cos_doy'])
    
    # --- Feature Set C: Set B + CHIRPS/ERA5 catchment rainfall ---
    feature_cols_C = list(feature_cols_B)
    if 'Rainfall_Catchment' in df.columns:
        # Rolling sums over 1, 3, 7, 14, 30 days
        df['rf_sum_1d'] = df['Rainfall_Catchment']
        df['rf_sum_3d'] = df['Rainfall_Catchment'].rolling(3).sum()
        df['rf_sum_7d'] = df['Rainfall_Catchment'].rolling(7).sum()
        df['rf_sum_14d'] = df['Rainfall_Catchment'].rolling(14).sum()
        df['rf_sum_30d'] = df['Rainfall_Catchment'].rolling(30).sum()
        
        # Rainfall lags
        df['rf_lag_1'] = df['Rainfall_Catchment'].shift(1)
        df['rf_lag_2'] = df['Rainfall_Catchment'].shift(2)
        df['rf_lag_3'] = df['Rainfall_Catchment'].shift(3)
        
        feature_cols_C.extend(['rf_sum_1d', 'rf_sum_3d', 'rf_sum_7d', 'rf_sum_14d', 'rf_sum_30d',
                              'rf_lag_1', 'rf_lag_2', 'rf_lag_3'])
        
    # --- Feature Set D: Set C + Local rainfall / Temp ---
    feature_cols_D = list(feature_cols_C)
    if 'Rainfall_Local' in df.columns and 'Temp_Catchment' in df.columns:
        df['rf_local_1d'] = df['Rainfall_Local']
        df['rf_local_7d'] = df['Rainfall_Local'].rolling(7).sum()
        df['temp_catchment'] = df['Temp_Catchment']
        feature_cols_D.extend(['rf_local_1d', 'rf_local_7d', 'temp_catchment'])
        
    feature_sets = {
        'A': feature_cols_A,
        'B': feature_cols_B,
        'C': feature_cols_C,
        'D': feature_cols_D
    }
    
    return df, feature_sets

def prepare_common_dataset(df, feature_cols, horizon):
    """
    Extract clean dataset for a specific feature set and horizon.
    Drops rows where features or targets are NaN to maintain a strict common row set.
    """
    target_col = f'Delta_WL_target_h{horizon}'
    wl_target_col = f'WL_target_h{horizon}'
    
    required_cols = ['Date', 'Year', 'Month', 'DayOfYear', 'WL', target_col, wl_target_col] + feature_cols
    
    clean_df = df[required_cols].dropna().copy().reset_index(drop=True)
    return clean_df
