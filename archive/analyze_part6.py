import pandas as pd
import numpy as np
import warnings
warnings.filterwarnings("ignore")

df = pd.read_csv(r"D:/Projects/pred_flood/archive/65 Years of Weather Data Bangladesh (1948 - 2013).csv")
df.columns = df.columns.str.strip()

# 6. Summary statistics
print("=" * 80)
print("6. SUMMARY STATISTICS FOR NUMERICAL COLUMNS")
print("=" * 80)
summary_cols = ["Max Temp", "Min Temp", "Rainfall", "Relative Humidity", "Wind Speed", "Cloud Coverage", "Bright Sunshine"]

header = f"{'Statistic':<12s}"
for col in summary_cols:
    header += f"{col:>14s}"
print(header)
print("-" * (12 + 14 * len(summary_cols)))

stats_list = ["count", "mean", "std", "min", "25%", "50%", "75%", "max"]
desc = df[summary_cols].describe()
for stat in stats_list:
    row = f"{stat:<12s}"
    for col in summary_cols:
        val = desc.loc[stat, col]
        row += f"{val:>14.2f}"
    print(row)

# Monthly rainfall pattern
print()
print("6b. MONTHLY RAINFALL PATTERN (all stations, all years)")
print("-" * 60)
monthly_rain = df.groupby("Month")["Rainfall"].agg(["mean", "median", "max", "sum", "count"])
header = f"{'Month':<8s} {'Mean':>10s} {'Median':>10s} {'Max':>10s} {'Total':>14s} {'Count':>8s}"
print(header)
print("-" * 60)
for month, row in monthly_rain.iterrows():
    print(f"{int(month):<8d} {row['mean']:>10.1f} {row['median']:>10.1f} {row['max']:>10.1f} {row['sum']:>14.0f} {int(row['count']):>8d}")

# Station-level summary
print()
print("6c. STATION-LEVEL CLIMATE SUMMARY")
print("-" * 100)
station_summary = df.groupby("Station Names").agg({
    "Max Temp": "mean",
    "Min Temp": "mean",
    "Rainfall": ["mean", "sum"],
    "Relative Humidity": "mean",
    "Wind Speed": "mean",
    "Bright Sunshine": "mean",
    "Cloud Coverage": "mean",
    "LATITUDE": "first",
    "LONGITUDE": "first",
    "ALT": "first"
}).round(2)

# Flatten multi-level columns
station_summary.columns = ["_".join(col).strip("_") for col in station_summary.columns]
station_summary = station_summary.rename(columns={
    "Max Temp_mean": "Avg MaxT",
    "Min Temp_mean": "Avg MinT",
    "Rainfall_mean": "Avg Rain",
    "Rainfall_sum": "Total Rain",
    "Relative Humidity_mean": "Avg RH",
    "Wind Speed_mean": "Avg Wind",
    "Bright Sunshine_mean": "Avg Sun",
    "Cloud Coverage_mean": "Avg Cloud",
    "LATITUDE_first": "Lat",
    "LONGITUDE_first": "Lon",
    "ALT_first": "Alt"
})
print(station_summary.to_string())

# Negative rainfall check
print()
print("6d. NEGATIVE RAINFULL CHECK")
neg_rain = df[df["Rainfall"] < 0]
print(f"  Records with negative rainfall: {len(neg_rain)}")
if len(neg_rain) > 0:
    print(neg_rain[["Station Names", "YEAR", "Month", "Rainfall"]].to_string())

# Rainfall > 2000
print()
print("6e. EXTREME RAINFALL (>1000mm/month)")
extreme = df[df["Rainfall"] > 1000].sort_values("Rainfall", ascending=False)
print(f"  Records: {len(extreme)}")
if len(extreme) > 0:
    print(extreme[["Station Names", "YEAR", "Month", "Rainfall"]].to_string())
