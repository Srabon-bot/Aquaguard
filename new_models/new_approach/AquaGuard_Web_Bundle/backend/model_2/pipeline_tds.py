import pandas as pd
import numpy as np
import os
import joblib
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor
from xgboost import XGBRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
import shap

# --- Paths ---
BASE_DIR = r"D:\Projects\pred_flood\new_models\new_approach\model_2"
DATA_PATH = os.path.join(BASE_DIR, "data", "pond_iot_2023.csv")
OUT_FIG = os.path.join(BASE_DIR, "outputs", "figures")
OUT_TBL = os.path.join(BASE_DIR, "outputs", "tables")
OUT_MOD = os.path.join(BASE_DIR, "outputs", "models")

for p in [OUT_FIG, OUT_TBL, OUT_MOD]:
    os.makedirs(p, exist_ok=True)

# --- 1. Data Loading & Preprocessing ---
print("Loading data...")
df = pd.read_csv(DATA_PATH)
df['created_date'] = pd.to_datetime(df['created_date'])
df = df.set_index('created_date').sort_index()

# Resample to 1-hour intervals to stabilize irregular readings
df_hourly = df[['water_pH', 'TDS', 'water_temp']].resample('1H').mean()

# Fill missing values: interpolate short gaps, forward fill the rest
df_hourly = df_hourly.interpolate(method='linear', limit=3).ffill().dropna()

# Rename for convenience
df_hourly.rename(columns={'water_pH': 'pH', 'water_temp': 'temperature'}, inplace=True)

print(f"Data resampled to {len(df_hourly)} hourly records.")

# --- 2. Feature Engineering ---
print("Engineering features...")
df_feat = df_hourly.copy()

# Time features
df_feat['hour'] = df_feat.index.hour
df_feat['day_of_week'] = df_feat.index.dayofweek

# Lag features
lags_tds = [1, 2, 3, 6, 12]
lags_ph = [1, 2, 3]
lags_temp = [1, 2, 3]

for lag in lags_tds:
    df_feat[f'TDS_t-{lag}'] = df_feat['TDS'].shift(lag)
    
for lag in lags_ph:
    df_feat[f'pH_t-{lag}'] = df_feat['pH'].shift(lag)
    
for lag in lags_temp:
    df_feat[f'temperature_t-{lag}'] = df_feat['temperature'].shift(lag)

# Rolling features (6-hour window)
df_feat['TDS_rolling_mean'] = df_feat['TDS'].shift(1).rolling(window=6).mean()
df_feat['TDS_rolling_std'] = df_feat['TDS'].shift(1).rolling(window=6).std()
df_feat['pH_rolling_mean'] = df_feat['pH'].shift(1).rolling(window=6).mean()
df_feat['temperature_rolling_mean'] = df_feat['temperature'].shift(1).rolling(window=6).mean()

# Target Variable: TDS + 1 hour (shifted by -1)
df_feat['target_TDS_plus_1h'] = df_feat['TDS'].shift(-1)

# Drop NaNs created by lagging/rolling
df_feat = df_feat.dropna()
print(f"Features created. Final dataset shape: {df_feat.shape}")

# --- 3. Chronological Splitting ---
n = len(df_feat)
train_idx = int(n * 0.70)
val_idx = int(n * 0.85)

train_df = df_feat.iloc[:train_idx]
val_df = df_feat.iloc[train_idx:val_idx]
test_df = df_feat.iloc[val_idx:]

features = [c for c in df_feat.columns if c not in ['target_TDS_plus_1h', 'TDS', 'pH', 'temperature']]
target = 'target_TDS_plus_1h'

X_train, y_train = train_df[features], train_df[target]
X_val, y_val = val_df[features], val_df[target]
X_test, y_test = test_df[features], test_df[target]

print(f"Train: {X_train.shape[0]}, Val: {X_val.shape[0]}, Test: {X_test.shape[0]}")

# --- 4. Modeling & Evaluation ---
def eval_metrics(y_true, y_pred):
    return {
        'MAE': mean_absolute_error(y_true, y_pred),
        'RMSE': np.sqrt(mean_squared_error(y_true, y_pred)),
        'R2': r2_score(y_true, y_pred)
    }

results = []
models = {
    'Linear Regression': LinearRegression(),
    'Random Forest': RandomForestRegressor(n_estimators=100, random_state=42, n_jobs=-1),
    'XGBoost': XGBRegressor(n_estimators=100, learning_rate=0.1, random_state=42, n_jobs=-1)
}

# Baseline: Persistence (predicted = current TDS, which is TDS_t-1 in features actually, wait, TDS is current. We didn't keep current TDS in features. Let's use TDS_t-1 as baseline for prediction? No, current TDS is train_df['TDS'], let's use that)
y_pred_baseline = test_df['TDS']
base_metrics = eval_metrics(y_test, y_pred_baseline)
results.append({'Model': 'Persistence Baseline', **base_metrics})

trained_models = {}

for name, model in models.items():
    print(f"Training {name}...")
    model.fit(X_train, y_train)
    y_pred = model.predict(X_test)
    metrics = eval_metrics(y_test, y_pred)
    results.append({'Model': name, **metrics})
    trained_models[name] = model
    # Save model
    joblib.dump(model, os.path.join(OUT_MOD, f"{name.replace(' ', '_').lower()}.pkl"))

# Save Metrics Table
res_df = pd.DataFrame(results)
res_df.to_csv(os.path.join(OUT_TBL, "model_comparison_metrics.csv"), index=False)
print("\nMetrics Table:\n", res_df)

# --- 5. Visualization ---
print("Generating plots...")

# Plot 1: Model Comparison Bar Chart
plt.figure(figsize=(10, 6))
sns.barplot(data=res_df.melt(id_vars='Model', var_name='Metric', value_name='Score'), 
            x='Metric', y='Score', hue='Model')
plt.title("Model Comparison on Test Set")
plt.tight_layout()
plt.savefig(os.path.join(OUT_FIG, "model_comparison.png"), dpi=300)
plt.close()

# Plot 2: Actual vs Predicted (Time Series) - XGBoost (assuming it's best)
best_model_name = 'XGBoost'
best_model = trained_models[best_model_name]
y_pred_best = best_model.predict(X_test)

plt.figure(figsize=(14, 6))
# Plot a subset (e.g., first 300 hours) for clarity
subset = 300
plt.plot(test_df.index[:subset], y_test[:subset], label='Actual TDS', color='blue', alpha=0.7)
plt.plot(test_df.index[:subset], y_pred_best[:subset], label=f'Predicted TDS ({best_model_name})', color='orange', linestyle='--', alpha=0.8)
plt.title(f"TDS Forecasting (+1 hour) on Test Set - {best_model_name}")
plt.xlabel("Date")
plt.ylabel("TDS (ppm)")
plt.legend()
plt.tight_layout()
plt.savefig(os.path.join(OUT_FIG, "actual_vs_predicted.png"), dpi=300)
plt.close()

# Plot 3: Scatter Plot (Actual vs Predicted)
plt.figure(figsize=(8, 8))
plt.scatter(y_test, y_pred_best, alpha=0.5, color='teal')
plt.plot([y_test.min(), y_test.max()], [y_test.min(), y_test.max()], 'r--')
plt.title(f"Actual vs Predicted TDS ({best_model_name})")
plt.xlabel("Actual TDS")
plt.ylabel("Predicted TDS")
plt.tight_layout()
plt.savefig(os.path.join(OUT_FIG, "scatter_actual_vs_predicted.png"), dpi=300)
plt.close()

# --- 6. SHAP Explainability ---
print("Generating SHAP values...")
# Use Random Forest for SHAP to avoid XGBoost 3.x version incompatibility bugs
rf_model = trained_models['Random Forest']
explainer = shap.TreeExplainer(rf_model)
shap_values = explainer.shap_values(X_test)

plt.figure(figsize=(10, 8))
shap.summary_plot(shap_values, X_test, show=False)
plt.title(f"SHAP Feature Importance (Random Forest)")
plt.tight_layout()
plt.savefig(os.path.join(OUT_FIG, "shap_summary.png"), dpi=300)
plt.close()

print("Pipeline completed successfully! All outputs saved.")
