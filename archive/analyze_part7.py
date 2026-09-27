import pandas as pd
import numpy as np
from scipy import stats
import warnings
warnings.filterwarnings("ignore")

df = pd.read_csv(r"D:/Projects/pred_flood/archive/65 Years of Weather Data Bangladesh (1948 - 2013).csv")
df.columns = df.columns.str.strip()

# 7. Comparison with flood forecasting datasets
print("=" * 80)
print("7. COMPARISON WITH TYPICAL FLOOD FORECASTING DATASETS")
print("=" * 80)
print("""
This dataset is a GROUND-BASED METEOROLOGICAL dataset. Here is how it compares
to typical flood forecasting data sources:

A. WHAT THIS DATASET PROVIDES (Strengths for flood forecasting):
   + Long-term historical rainfall (primary flood driver) - 65 years
   + Temperature data (evapotranspiration, snowmelt modeling)
   + Humidity and wind (weather pattern context)
   + Sunshine hours (evaporation estimation)
   + Geographic coordinates for spatial analysis
   + Monthly temporal resolution suitable for seasonal flood prediction

B. WHAT THIS DATASET LACKS vs. dedicated flood forecasting datasets:
   - No river discharge/flow data (SWAT, HEC-RAS models need this)
   - No water level/stage measurements at river gauging stations
   - No soil moisture or groundwater level data
   - No land use/land cover (LULC) data for runoff estimation
   - No Digital Elevation Model (DEM) for floodplain mapping
   - No reservoir/dam operation data
   - No tidal data (critical for coastal Bangladesh flooding)
   - Monthly resolution too coarse for flash flood prediction
   - Point-based stations only - no spatial coverage between stations
   - No satellite precipitation (TRMM, GPM, CHIRPS) for spatial rainfall

C. COMPLEMENTARITY:
   * This dataset is an EXCELLENT complement to:
     - BWDB (Bangladesh Water Development Board) river gauge data
     - Satellite precipitation products (for spatial interpolation)
     - DEM data (SRTM/ASTER) for flood inundation mapping
     - Land cover data for runoff coefficient estimation
   
   * Can be used for:
     - Antecedent moisture condition estimation
     - Seasonal flood outlook (monthly scale)
     - Climate trend analysis for flood frequency
     - Calibrating rainfall for hydrological models
     - Identifying extreme rainfall events as flood triggers

D. KNOWN DATA QUALITY CONCERNS FOR FLOOD MODELING:
   * Wind Speed shows suspicious constant values at many stations (likely padded)
   * Bright Sunshine also shows padding at some stations
   * Monthly aggregation loses intensity-duration information critical for floods
   * Station network density may be insufficient for spatial rainfall estimation
   * No quality flags or source metadata for individual observations
""")

# 8. Flood-relevant patterns
print("=" * 80)
print("8. FLOOD-RELEVANT PATTERNS")
print("=" * 80)

# Extreme rainfall events
print("\n8a. TOP 20 EXTREME MONTHLY RAINFALL EVENTS")
extreme_rain = df.nlargest(20, "Rainfall")[["Station Names", "YEAR", "Month", "Rainfall", "Relative Humidity"]]
print(extreme_rain.to_string(index=False))

# Monsoon concentration
print("\n8b. MONSOON VS DRY SEASON RAINFALL")
df["Season"] = df["Month"].map(lambda m: "Monsoon" if m in [6,7,8,9] else ("Pre-Monsoon" if m in [4,5] else ("Post-Monsoon" if m in [10,11] else "Dry")))
season_rain = df.groupby("Season")["Rainfall"].agg(["mean", "sum", "max"]).round(1)
print(season_rain.to_string())

# Yearly rainfall trend
print("\n8c. ANNUAL RAINFALL TREND (all stations combined)")
annual_rain = df.groupby("YEAR")["Rainfall"].sum()
print(f"  Wettest year:  {annual_rain.idxmax()} ({annual_rain.max():.0f} mm total)")
print(f"  Driest year:   {annual_rain.idxmin()} ({annual_rain.min():.0f} mm total)")
print(f"  Mean annual:   {annual_rain.mean():.0f} mm")
print(f"  Std deviation: {annual_rain.std():.0f} mm")

slope, intercept, r_value, p_value, std_err = stats.linregress(annual_rain.index, annual_rain.values)
print(f"  Linear trend:  {slope:.2f} mm/year (R2={r_value**2:.3f}, p={p_value:.4f})")

# Wind speed deep dive
print("\n8d. WIND SPEED DEEP DIVE (checking for padded values)")
ws_per_station = df.groupby("Station Names")["Wind Speed"].agg(["nunique", "mean", "std", "min", "max"])
ws_const = ws_per_station[ws_per_station["nunique"] <= 5]
print(f"  Stations with <=5 unique wind speed values (likely padded): {len(ws_const)}")
if len(ws_const) > 0:
    print(ws_const.to_string())

# Bright sunshine deep dive
print("\n8e. BRIGHT SUNSHINE DEEP DIVE")
bs_per_station = df.groupby("Station Names")["Bright Sunshine"].agg(["nunique", "mean", "std"])
bs_const = bs_per_station[bs_per_station["nunique"] <= 5]
print(f"  Stations with <=5 unique sunshine values (likely padded): {len(bs_const)}")
if len(bs_const) > 0:
    print(bs_const.to_string())

# Spatial coverage
print("\n8f. SPATIAL COVERAGE SUMMARY")
print(f"  Latitude range:  {df['LATITUDE'].min():.2f} to {df['LATITUDE'].max():.2f}")
print(f"  Longitude range: {df['LONGITUDE'].min():.2f} to {df['LONGITUDE'].max():.2f}")
print(f"  Altitude range:  {df['ALT'].min()} to {df['ALT'].max()} m")
print(f"  Approximate area: {(df['LATITUDE'].max()-df['LATITUDE'].min()):.1f} x {(df['LONGITUDE'].max()-df['LONGITUDE'].min()):.1f} degrees")
print(f"  Avg station density: ~{df['Station Names'].nunique() / ((df['LATITUDE'].max()-df['LATITUDE'].min())*(df['LONGITUDE'].max()-df['LONGITUDE'].min())):.2f} stations per sq degree")

print("\n" + "=" * 80)
print("ANALYSIS COMPLETE")
print("=" * 80)
