import pandas as pd
import numpy as np
import warnings
warnings.filterwarnings("ignore")

df = pd.read_csv(r"D:/Projects/pred_flood/archive/65 Years of Weather Data Bangladesh (1948 - 2013).csv")
df.columns = df.columns.str.strip()

# 5. Data quality issues
print("=" * 80)
print("5. DATA QUALITY ISSUES")
print("=" * 80)

# Duplicates
print("\n5a. DUPLICATE CHECK")
dupes = df.duplicated()
print(f"  Fully duplicate rows: {dupes.sum()}")
subset_dupes = df.duplicated(subset=["Station Names", "YEAR", "Month"])
print(f"  Duplicate (Station, Year, Month) combos: {subset_dupes.sum()}")
if subset_dupes.sum() > 0:
    dupe_stations = df[subset_dupes]["Station Names"].value_counts()
    print("  Stations with duplicate month entries:")
    for s, c in dupe_stations.items():
        print(f"    {s}: {c} duplicates")

# Outliers
print("\n5b. OUTLIER ANALYSIS (IQR method)")
num_cols = df.select_dtypes(include=[np.number]).columns.tolist()
id_cols = ["Station Number", "X_COR", "Y_COR"]
num_cols_clean = [c for c in num_cols if c not in id_cols and c != "Period" and c != "Unnamed: 0"]

for col in num_cols_clean:
    q1 = df[col].quantile(0.25)
    q3 = df[col].quantile(0.75)
    iqr = q3 - q1
    lower = q1 - 1.5 * iqr
    upper = q3 + 1.5 * iqr
    outliers = ((df[col] < lower) | (df[col] > upper)).sum()
    print(f"\n  {col}:")
    print(f"    IQR bounds: [{lower:.2f}, {upper:.2f}]")
    print(f"    Outliers: {outliers} ({outliers/len(df)*100:.2f}%)")
    if outliers > 0:
        min_out = df[col][df[col] < lower].min() if (df[col] < lower).any() else None
        max_out = df[col][df[col] > upper].max() if (df[col] > upper).any() else None
        if min_out is not None:
            print(f"    Min outlier: {min_out:.2f}")
        if max_out is not None:
            print(f"    Max outlier: {max_out:.2f}")

# Physical range checks
print("\n5c. PHYSICAL RANGE VALIDATION")
range_checks = {
    "Max Temp": (-10, 55),
    "Min Temp": (-15, 45),
    "Rainfall": (0, 2000),
    "Relative Humidity": (0, 100),
    "Wind Speed": (0, 50),
    "Cloud Coverage": (0, 8),
    "Bright Sunshine": (0, 15),
}
for col, (lo, hi) in range_checks.items():
    if col in df.columns:
        oob = ((df[col] < lo) | (df[col] > hi)).sum()
        if oob > 0:
            print(f"  {col}: {oob} values outside [{lo}, {hi}]")
        else:
            print(f"  {col}: All values within [{lo}, {hi}]")

# Constant value detection
print("\n5d. SUSPICIOUS CONSTANT/PAD VALUES")
for col in num_cols_clean:
    vals = df[col].dropna()
    if len(vals) > 0:
        unique_ratio = vals.nunique() / len(vals)
        if unique_ratio < 0.01 and vals.nunique() < 5:
            print(f"  {col}: Only {vals.nunique()} unique values ({vals.unique()}) - possible padding")

# Station-level constant check
print("\n5e. STATION-LEVEL CONSTANT VALUE CHECK (Wind Speed & Bright Sunshine)")
for col in ["Wind Speed", "Bright Sunshine", "Cloud Coverage"]:
    if col in df.columns:
        const_per_station = df.groupby("Station Names")[col].nunique()
        const_stations = const_per_station[const_per_station <= 3]
        if len(const_stations) > 0:
            print(f"\n  {col} - stations with <=3 unique values:")
            for station, nunique in const_stations.items():
                vals = df[df["Station Names"] == station][col].unique()
                print(f"    {station}: {nunique} unique -> {np.round(vals[:5], 4)}")
