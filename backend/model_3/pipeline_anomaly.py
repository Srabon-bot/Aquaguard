import pandas as pd
import numpy as np
import os
import joblib
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler

# --- Paths ---
DATA_PATH = r"D:\Projects\pred_flood\new_models\new_approach\model_2\data\pond_iot_2023.csv"
BASE_DIR = r"D:\Projects\pred_flood\new_models\new_approach\model_3"
OUT_FIG = os.path.join(BASE_DIR, "outputs", "figures")
OUT_MOD = os.path.join(BASE_DIR, "outputs", "models")

for p in [OUT_FIG, OUT_MOD]:
    os.makedirs(p, exist_ok=True)

# --- 1. Data Loading & Preprocessing ---
print("Loading data...")
df = pd.read_csv(DATA_PATH)
df['created_date'] = pd.to_datetime(df['created_date'])
df = df.set_index('created_date').sort_index()

# Resample to 1-hour intervals to stabilize irregular readings
df_hourly = df[['water_pH', 'TDS', 'water_temp']].resample('1h').mean()
df_hourly = df_hourly.interpolate(method='linear', limit=3).ffill().dropna()
df_hourly.rename(columns={'water_pH': 'pH', 'water_temp': 'temperature'}, inplace=True)

# --- 2. Feature Engineering (As per PRD) ---
print("Engineering features...")
df_feat = df_hourly.copy()

# Derived features (deltas)
df_feat['pH_change'] = df_feat['pH'].diff()
df_feat['TDS_change'] = df_feat['TDS'].diff()
df_feat['temp_change'] = df_feat['temperature'].diff()

df_feat = df_feat.dropna()
features = ['pH', 'TDS', 'temperature', 'pH_change', 'TDS_change', 'temp_change']
X = df_feat[features]

print(f"Features created. Final dataset shape: {X.shape}")

# Scale features for distance-based comparisons (Baseline)
scaler = StandardScaler()
X_scaled = pd.DataFrame(scaler.fit_transform(X), columns=X.columns, index=X.index)

# --- 3. Modeling: Statistical Baseline ---
print("Running Statistical Threshold Baseline...")
# A simple baseline: if any sensor deviates by more than 3 standard deviations, it's an anomaly.
df_feat['baseline_anomaly'] = (np.abs(X_scaled) > 3).any(axis=1)
baseline_count = df_feat['baseline_anomaly'].sum()
print(f"Baseline detected {baseline_count} anomalies (Z-score > 3).")

# --- 4. Modeling: Isolation Forest ---
print("Training Isolation Forest...")
# Set contamination to 0.05 (assuming 5% of historical data represents unusual conditions)
iso_forest = IsolationForest(n_estimators=100, contamination=0.05, random_state=42, n_jobs=-1)
iso_forest.fit(X)

# Predict: 1 for normal, -1 for anomaly
predictions = iso_forest.predict(X)
# Decision function: lower scores are more anomalous
scores = iso_forest.decision_function(X)

# Convert to boolean flag for easier plotting (True = Anomaly)
df_feat['if_anomaly'] = predictions == -1
df_feat['anomaly_score'] = scores

if_count = df_feat['if_anomaly'].sum()
print(f"Isolation Forest detected {if_count} anomalies.")

# Save the scaler and model for future API usage
joblib.dump(scaler, os.path.join(OUT_MOD, "scaler.pkl"))
joblib.dump(iso_forest, os.path.join(OUT_MOD, "isolation_forest.pkl"))

# --- 5. Visualization ---
print("Generating plots...")

# Plot 1: TDS Time Series with Anomalies Highlighted
plt.figure(figsize=(14, 6))
plt.plot(df_feat.index, df_feat['TDS'], label='Normal TDS', color='blue', alpha=0.6)
anomalies = df_feat[df_feat['if_anomaly']]
plt.scatter(anomalies.index, anomalies['TDS'], color='red', label='Anomaly Detected', s=40, zorder=5)
plt.title("Isolation Forest Anomaly Detection on TDS")
plt.xlabel("Date")
plt.ylabel("TDS (ppm)")
plt.legend()
plt.tight_layout()
plt.savefig(os.path.join(OUT_FIG, "anomaly_timeline_tds.png"), dpi=300)
plt.close()

# Plot 2: pH vs TDS Scatter Plot Colored by Anomaly
plt.figure(figsize=(8, 6))
sns.scatterplot(x='pH', y='TDS', hue='if_anomaly', palette={False: 'teal', True: 'red'}, data=df_feat, alpha=0.7)
plt.title("Multivariate Anomaly View: pH vs TDS")
plt.xlabel("pH")
plt.ylabel("TDS (ppm)")
plt.legend(title='Is Anomaly?')
plt.tight_layout()
plt.savefig(os.path.join(OUT_FIG, "scatter_ph_vs_tds.png"), dpi=300)
plt.close()

# Plot 3: Anomaly Score Distribution
plt.figure(figsize=(8, 5))
sns.histplot(df_feat['anomaly_score'], bins=50, kde=True, color='purple')
plt.axvline(x=df_feat[df_feat['if_anomaly']]['anomaly_score'].max(), color='red', linestyle='--', label='Anomaly Threshold')
plt.title("Distribution of Isolation Forest Anomaly Scores")
plt.xlabel("Anomaly Score (Lower is more anomalous)")
plt.ylabel("Frequency")
plt.legend()
plt.tight_layout()
plt.savefig(os.path.join(OUT_FIG, "anomaly_score_distribution.png"), dpi=300)
plt.close()

print("Pipeline completed successfully! All outputs saved.")
