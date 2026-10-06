import pandas as pd
import numpy as np
from pathlib import Path
from src import config as C

def load_raw_data():
    """Load primary gauge series (Date, WL, Q_R) and ensure complete calendar dates."""
    df = pd.read_csv(C.RAW_WL_Q_PATH)
    df['Date'] = pd.to_datetime(df['Date'])
    df = df.sort_values('Date').reset_index(drop=True)
    
    # Ensure full continuous date range 2008-01-01 to 2022-12-31
    full_dates = pd.date_range(start='2008-01-01', end='2022-12-31', freq='D')
    df_full = pd.DataFrame({'Date': full_dates})
    df = pd.merge(df_full, df, on='Date', how='left')
    
    df['Year'] = df['Date'].dt.year
    df['Month'] = df['Date'].dt.month
    df['DayOfYear'] = df['Date'].dt.dayofyear
    
    return df

def audit_annual_maxima(df):
    """Compare dataset annual maxima against BWDB official record."""
    records = []
    for yr, (bw_val, bw_date_str) in C.BWDB_ANNUAL_MAXIMA.items():
        sub = df[df['Year'] == yr].dropna(subset=['WL'])
        if len(sub) == 0:
            continue
        max_idx = sub['WL'].idxmax()
        max_row = sub.loc[max_idx]
        ds_val = max_row['WL']
        ds_date = max_row['Date']
        bw_date = pd.to_datetime(bw_date_str)
        diff_val = ds_val - bw_val
        diff_days = (ds_date - bw_date).days
        records.append({
            'Year': yr,
            'Dataset_Max_WL': ds_val,
            'Dataset_Max_Date': ds_date,
            'BWDB_Max_WL': bw_val,
            'BWDB_Max_Date': bw_date,
            'WL_Diff_m': diff_val,
            'Date_Diff_days': diff_days
        })
    return pd.DataFrame(records)

def audit_nulls(df):
    """Count nulls by year and month."""
    null_matrix = df.pivot_table(index='Year', columns='Month', values='WL', aggfunc=lambda x: x.isna().sum(), fill_value=0)
    return null_matrix

def identify_flood_events(df, threshold=C.DL):
    """Identify independent flood events (consecutive days >= threshold)."""
    df_clean = df.copy()
    df_clean['above_dl'] = (df_clean['WL'] >= threshold).fillna(False)
    
    # Identify event transitions
    df_clean['event_start'] = df_clean['above_dl'] & (~df_clean['above_dl'].shift(1, fill_value=False))
    df_clean['event_id'] = df_clean['event_start'].cumsum()
    
    events_df = df_clean[df_clean['above_dl']].groupby('event_id').agg(
        start_date=('Date', 'min'),
        end_date=('Date', 'max'),
        duration=('Date', 'count'),
        peak_wl=('WL', 'max'),
        peak_date=('Date', lambda x: df_clean.loc[x.index[df_clean.loc[x.index, 'WL'].argmax()], 'Date'])
    ).reset_index(drop=True)
    
    events_df['event_index'] = np.arange(1, len(events_df) + 1)
    return events_df

def load_rainfall_data():
    """Load Brahmaputra catchment-averaged daily rainfall."""
    rf_path = C.RAW_DIR / "catchment_rainfall.csv"
    if not rf_path.exists():
        raise FileNotFoundError(f"Rainfall data not found at {rf_path}")
    df_rf = pd.read_csv(rf_path)
    df_rf['Date'] = pd.to_datetime(df_rf['date'])
    df_rf = df_rf[['Date', 'precip_catchment_mm', 'temp_catchment_c', 'precip_local_mm']].copy()
    df_rf.rename(columns={
        'precip_catchment_mm': 'Rainfall_Catchment',
        'temp_catchment_c': 'Temp_Catchment',
        'precip_local_mm': 'Rainfall_Local'
    }, inplace=True)
    return df_rf

def compute_doy_climatology(df):
    """Compute day-of-year mean WL (climatology) on dev set (2008-2019)."""
    dev_mask = (df['Year'] >= C.DEV_START_YEAR) & (df['Year'] <= C.DEV_END_YEAR)
    dev_df = df[dev_mask].copy()
    doy_mean = dev_df.groupby('DayOfYear')['WL'].mean().to_dict()
    return doy_mean

def get_table_t1(df, events_df):
    """Generate Table T1: Dataset Summary."""
    total_rows = len(df)
    total_nulls = df['WL'].isna().sum()
    null_pct = (total_nulls / total_rows) * 100
    days_above_dl = (df['WL'] >= C.DL).sum()
    days_above_extreme = (df['WL'] >= C.EXTREME_LEVEL).sum()
    days_above_rhwl = (df['WL'] >= C.RHWL).sum()
    
    t1_data = {
        'Parameter': [
            'Study Period',
            'Total Calendar Days',
            'Missing Daily WL Values',
            'Missing Data Share (%)',
            'Gauge Level Range (m)',
            'Danger Level Threshold (m)',
            'Extreme Level Threshold (m)',
            'Recorded Highest Water Level (RHWL) (m)',
            'Total Days >= Danger Level (19.05 m)',
            'Total Days >= Extreme Level (19.90 m)',
            'Total Days >= RHWL (20.63 m)',
            'Identified Independent Flood Events',
            'Mean Flood Event Duration (days)',
            'Max Flood Event Duration (days)',
            'Development Window (Train/CV)',
            'Final Test Holdout Window'
        ],
        'Value': [
            f"2008-01-01 to 2022-12-31",
            f"{total_rows:,}",
            f"{total_nulls} days",
            f"{null_pct:.2f}%",
            f"{df['WL'].min():.2f} to {df['WL'].max():.2f}",
            f"{C.DL:.2f}",
            f"{C.EXTREME_LEVEL:.2f}",
            f"{C.RHWL:.2f}",
            f"{days_above_dl} days",
            f"{days_above_extreme} days",
            f"{days_above_rhwl} days",
            f"{len(events_df)}",
            f"{events_df['duration'].mean():.1f} days",
            f"{events_df['duration'].max()} days",
            f"2008 – 2019 (12 years)",
            f"2020 – 2022 (3 years)"
        ]
    }
    return pd.DataFrame(t1_data)
