import os
from pathlib import Path
import yaml

# Base directory
BASE_DIR = Path(__file__).resolve().parent.parent

# Load config.yaml
CONFIG_PATH = BASE_DIR / "config.yaml"
with open(CONFIG_PATH, "r") as f:
    CONFIG = yaml.safe_load(f)

# Data paths
RAW_WL_Q_PATH = BASE_DIR / CONFIG["data"]["raw_wl_q_path"]
PROCESSED_DIR = BASE_DIR / CONFIG["data"]["processed_dir"]
RAW_DIR = BASE_DIR / CONFIG["data"]["raw_dir"]
PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
RAW_DIR.mkdir(parents=True, exist_ok=True)

# Output paths
FIGURES_DIR = BASE_DIR / CONFIG["output"]["figures_dir"]
TABLES_DIR = BASE_DIR / CONFIG["output"]["tables_dir"]
PREDICTIONS_DIR = BASE_DIR / CONFIG["output"]["predictions_dir"]
CAPTIONS_PATH = BASE_DIR / CONFIG["output"]["captions_path"]

FIGURES_DIR.mkdir(parents=True, exist_ok=True)
TABLES_DIR.mkdir(parents=True, exist_ok=True)
PREDICTIONS_DIR.mkdir(parents=True, exist_ok=True)

# Project Parameters
STATION = CONFIG["project"]["station"]
STATION_CODE = CONFIG["project"]["station_code"]
DL = CONFIG["thresholds"]["danger_level"]       # 19.05 m
EXTREME_LEVEL = CONFIG["thresholds"]["extreme_level"] # 19.90 m
RHWL = CONFIG["thresholds"]["rhwl"]             # 20.63 m

DEV_START_YEAR = CONFIG["splits"]["dev_start_year"] # 2008
DEV_END_YEAR = CONFIG["splits"]["dev_end_year"]     # 2019
TEST_START_YEAR = CONFIG["splits"]["test_start_year"] # 2020
TEST_END_YEAR = CONFIG["splits"]["test_end_year"]     # 2022
GAP_DAYS = CONFIG["splits"]["gap_days"]               # 7

HORIZONS = CONFIG["horizons"] # [1, 3, 7, 14]
LAGS = CONFIG["lags"]         # [0, 1, 2, 3, 4, 5, 6, 7]
SEED = CONFIG["random_seed"]  # 42

# Consistent Styling Palette for Models across all figures
MODEL_COLORS = {
    'Persistence': '#7f7f7f',           # Gray
    'Persistence+Trend': '#bcbd22',     # Olive
    'Anomaly Persistence': '#17becf',   # Cyan
    'LinearRegression': '#1f77b4',      # Blue
    'Ridge': '#aec7e8',                 # Light Blue
    'Lasso': '#9edae5',                 # Soft Blue
    'RandomForest': '#ff7f0e',          # Orange
    'XGBoost': '#2ca02c',               # Green
    'SVR': '#9467bd',                   # Purple
    'LSTM': '#d62728',                  # Red
    'Ensemble': '#e377c2'               # Pink
}

BWDB_ANNUAL_MAXIMA = {
    2008: (19.75, "2008-09-08"),
    2009: (19.37, "2009-08-22"),
    2010: (19.78, "2010-09-14"),
    2011: (19.64, "2011-07-23"),
    2012: (20.54, "2012-07-01"),
    2013: (19.91, "2013-09-11"),
    2014: (20.20, "2014-08-29"),
    2015: (20.17, "2015-09-06"),
    2016: (20.71, "2016-07-28"),
    2017: (20.84, "2017-08-16"),
}
