"""
Generate Figures D, G, H for AquaGuard Model 1 report.

Figure D: Warning Threshold Hydrograph (2020-2021 flood season)
Figure G: Model 1 Data Pipeline Diagram
Figure H: Data Sources Relationship Diagram

Output: new_models/new_approach/model_1_flood/outputs/figures/report_extra/
"""

import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import matplotlib.patches as mpatch
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
from pathlib import Path

OUT_DIR = Path("D:/Projects/pred_flood/new_models/new_approach/model_1_flood/outputs/figures/report_extra")
OUT_DIR.mkdir(parents=True, exist_ok=True)

PRED_CSV = Path("D:/Projects/pred_flood/new_models/new_approach/model_1_flood/outputs/predictions/final_holdout_2020_2022_h3_LinearRegression.csv")
WL_CSV   = Path("D:/Projects/pred_flood/new_models/new_approach/model_1_flood/Data/Q/Own_Rated_Q_2008-2022_Bahadurabad.csv")

# ─────────────────────────────────────────────────────────────────────────────
# FIGURE D — Warning Threshold Hydrograph
# ─────────────────────────────────────────────────────────────────────────────
print("Building Figure D ...")

df = pd.read_csv(PRED_CSV)
df['Date']        = pd.to_datetime(df['Date'])
df['Target_Date'] = pd.to_datetime(df['Target_Date'])

# Focus on monsoon 2020 (May → November) — biggest flood in dataset
mask = (df['Target_Date'] >= '2020-04-01') & (df['Target_Date'] <= '2020-11-30')
dfl  = df[mask].copy()

fig, ax = plt.subplots(figsize=(13, 5.5))
fig.patch.set_facecolor('#f9f9f9')
ax.set_facecolor('#f9f9f9')

# Threshold levels
WARN  = 18.55
DL    = 19.05
EL    = 19.90

# Shade the dangerous zone (warning → extreme)
ax.axhspan(WARN, EL + 0.2, alpha=0.07, color='#d62728', zorder=0)

# Shade the warning-to-danger zone differently
ax.axhspan(WARN, DL, alpha=0.10, color='#ff7f0e', zorder=0)

# Threshold lines
ax.axhline(EL,   color='#7b0000', lw=1.6, ls='--', zorder=2, label='Extreme Danger Level (19.90 m)')
ax.axhline(DL,   color='#d62728', lw=1.8, ls='--', zorder=2, label='Official Danger Level (19.05 m)')
ax.axhline(WARN, color='#ff7f0e', lw=1.8, ls='-.', zorder=2, label='AquaGuard Alert Threshold (18.55 m)')

# Predicted and observed lines
ax.plot(dfl['Target_Date'], dfl['y_pred'],
        color='#1f77b4', lw=2.0, zorder=4, label='Linear Regression Prediction (+3 day)')
ax.plot(dfl['Target_Date'], dfl['y_true'],
        color='#2ca02c', lw=1.5, alpha=0.85, zorder=3, label='Observed Water Level (BWDB)')

# Annotate the peak
peak_idx  = dfl['y_true'].idxmax()
peak_date = dfl.loc[peak_idx, 'Target_Date']
peak_val  = dfl.loc[peak_idx, 'y_true']
ax.annotate(f'Peak: {peak_val:.2f} m\n{peak_date.strftime("%d %b %Y")}',
            xy=(peak_date, peak_val),
            xytext=(peak_date + pd.Timedelta(days=12), peak_val - 0.55),
            fontsize=9,
            arrowprops=dict(arrowstyle='->', color='#333', lw=1.2),
            color='#333',
            bbox=dict(boxstyle='round,pad=0.3', fc='white', ec='#999', alpha=0.85))

# Annotate the AquaGuard alert window
first_warn = dfl[dfl['y_pred'] >= WARN]['Target_Date'].min()
first_dl   = dfl[dfl['y_true'] >= DL]['Target_Date'].min()
if pd.notna(first_warn) and pd.notna(first_dl):
    ax.annotate('',
                xy=(first_dl,   DL - 0.05),
                xytext=(first_warn, DL - 0.05),
                arrowprops=dict(arrowstyle='<->', color='#ff7f0e', lw=1.5))
    ax.text((first_warn + (first_dl - first_warn) / 2), DL - 0.18,
            f'~{(first_dl - first_warn).days} days warning',
            ha='center', fontsize=8.5, color='#c05000',
            bbox=dict(boxstyle='round,pad=0.2', fc='#fff3e0', ec='#ff7f0e', alpha=0.9))

# Threshold labels on right y-axis
ax2 = ax.twinx()
ax2.set_ylim(ax.get_ylim())
ax2.set_yticks([WARN, DL, EL])
ax2.set_yticklabels(['Alert\n18.55 m', 'Danger\n19.05 m', 'Extreme\n19.90 m'],
                    fontsize=8, color='#555')
ax2.tick_params(length=0)

ax.set_xlabel('Date (2020)', fontsize=11)
ax.set_ylabel('Water Level (m, mPWD)', fontsize=11)
ax.set_title('Figure D: AquaGuard Warning Threshold Hydrograph — 2020 Flood Season\n'
             'Bahadurabad Transit Station (SW46.9L), Jamuna River, +3-Day Forecast',
             fontsize=11, fontweight='bold', pad=10)
ax.legend(loc='upper left', fontsize=8.5, framealpha=0.92, edgecolor='#ccc')
ax.tick_params(axis='x', rotation=30)
ax.grid(axis='y', color='#ddd', lw=0.7, zorder=0)
ax.set_ylim(bottom=12.5)

plt.tight_layout()
out_d = OUT_DIR / 'FigD_warning_threshold_hydrograph.png'
plt.savefig(out_d, dpi=150, bbox_inches='tight')
plt.savefig(str(out_d).replace('.png', '.pdf'), bbox_inches='tight')
plt.close()
print(f"  Saved: {out_d}")


# ─────────────────────────────────────────────────────────────────────────────
# FIGURE G — Model 1 Data Pipeline Diagram
# ─────────────────────────────────────────────────────────────────────────────
print("Building Figure G ...")

fig, ax = plt.subplots(figsize=(12, 14))
fig.patch.set_facecolor('#ffffff')
ax.set_xlim(0, 10)
ax.set_ylim(0, 14)
ax.axis('off')

def box(ax, x, y, w, h, text, fc='#1f3864', tc='white', fs=9.5, ec='#0a1f3a', style='round,pad=0.1', bold=False):
    rect = FancyBboxPatch((x - w/2, y - h/2), w, h,
                          boxstyle=style, fc=fc, ec=ec, lw=1.5, zorder=3)
    ax.add_patch(rect)
    ax.text(x, y, text, ha='center', va='center', fontsize=fs, color=tc,
            fontweight='bold' if bold else 'normal',
            wrap=True, multialignment='center', zorder=4)

def arrow(ax, x1, y1, x2, y2, color='#555', label=''):
    ax.annotate('', xy=(x2, y2), xytext=(x1, y1),
                arrowprops=dict(arrowstyle='->', color=color, lw=1.8))
    if label:
        mx, my = (x1+x2)/2, (y1+y2)/2
        ax.text(mx + 0.15, my, label, fontsize=8, color='#555', va='center')

# ── Row 1: Data Sources ───────────────────────────────────────────────────────
ax.text(5, 13.5, 'MODEL 1 — DATA PIPELINE & FEATURE CONSTRUCTION',
        ha='center', va='center', fontsize=13, fontweight='bold', color='#1f3864')

box(ax, 2.5, 12.5, 3.8, 0.9,
    'BWDB Gauge SW46.9L\nBahadurabad Daily Water Level + Discharge\n2008–2022 (5,479 days)',
    fc='#1f3864', tc='white', fs=8.5)
box(ax, 7.5, 12.5, 3.8, 0.9,
    'ERA5 Reanalysis via Open-Meteo API\n6 Catchment Grid Points\n82°E–98°E, 24°N–32°N',
    fc='#1f3864', tc='white', fs=8.5)

# ── Row 2: Data Cleaning ─────────────────────────────────────────────────────
arrow(ax, 2.5, 12.05, 2.5, 11.35)
arrow(ax, 7.5, 12.05, 7.5, 11.35)

box(ax, 2.5, 11.0, 3.8, 0.6,
    'Data Cleaning: PCHIP Interpolation\n335 missing days (6.11%) filled',
    fc='#2a5298', tc='white', fs=8)
box(ax, 7.5, 11.0, 3.8, 0.6,
    'Catchment-Averaged Precipitation (mm/day)\n& Mean Temperature (°C/day)',
    fc='#2a5298', tc='white', fs=8)

# ── Row 3: Feature Engineering ───────────────────────────────────────────────
arrow(ax, 2.5, 10.7, 2.5, 10.15)
arrow(ax, 7.5, 10.7, 7.5, 10.15)

box(ax, 1.2, 9.8, 1.9, 0.6, 'WL Lag Features\nWL_t-0 … WL_t-7', fc='#285e8e', tc='white', fs=8)
box(ax, 3.3, 9.8, 1.9, 0.6, 'Rate of Change\nΔWL 1d, 3d, 7d', fc='#285e8e', tc='white', fs=8)
box(ax, 5.5, 9.8, 1.9, 0.6, 'Rolling Means\n3d, 7d mean & std', fc='#285e8e', tc='white', fs=8)
box(ax, 7.5, 9.8, 1.9, 0.6, 'Rainfall Lags\n1d, 3d, 7d cumulative', fc='#285e8e', tc='white', fs=8)
box(ax, 9.3, 9.8, 1.2, 0.6, 'Seasonality\nsin/cos DoY', fc='#285e8e', tc='white', fs=8)

# convergence arrows to feature matrix
for xp in [1.2, 3.3, 5.5, 7.5, 9.3]:
    arrow(ax, xp, 9.5, 5.0, 8.75)

box(ax, 5.0, 8.5, 5.5, 0.7,
    'Feature Matrix  (one row per forecast date)',
    fc='#145A32', tc='white', fs=9.5, bold=True)

# ── Row 4: Train/Validate ─────────────────────────────────────────────────────
arrow(ax, 5.0, 8.15, 5.0, 7.55)
box(ax, 5.0, 7.2, 5.5, 0.6,
    'Leave-One-Year-Out (LOYO) Cross-Validation\n12 folds: 2008–2019 | Test holdout: 2020–2022',
    fc='#6C3483', tc='white', fs=8.5)

# ── Row 5: Models ─────────────────────────────────────────────────────────────
arrow(ax, 5.0, 6.9, 5.0, 6.35)
box(ax, 1.8, 6.0, 2.0, 0.6, 'Linear Regression\n★ Deployed', fc='#1f77b4', tc='white', fs=8.5)
box(ax, 4.2, 6.0, 1.5, 0.6, 'Ridge\nLasso', fc='#aec7e8', tc='#1a1a1a', fs=8.5)
box(ax, 6.0, 6.0, 1.5, 0.6, 'Random\nForest', fc='#ff7f0e', tc='white', fs=8.5)
box(ax, 7.7, 6.0, 1.5, 0.6, 'XGBoost', fc='#2ca02c', tc='white', fs=8.5)
box(ax, 9.2, 6.0, 1.3, 0.6, 'SVR\nLSTM', fc='#9467bd', tc='white', fs=8.5)
for xp in [1.8, 4.2, 6.0, 7.7, 9.2]:
    arrow(ax, 5.0, 6.35, xp, 6.3)

# ── Row 6: Horizons ─────────────────────────────────────────────────────────
for xp in [1.8, 4.2, 6.0, 7.7, 9.2]:
    arrow(ax, xp, 5.7, 5.0, 5.15)

box(ax, 5.0, 4.8, 5.5, 0.6,
    'Multi-Horizon Predictions: +1 day  |  +3 days  |  +7 days  |  +14 days',
    fc='#1f3864', tc='white', fs=9, bold=True)

# ── Row 7: Evaluation ─────────────────────────────────────────────────────────
arrow(ax, 5.0, 4.5, 5.0, 3.9)
box(ax, 5.0, 3.6, 5.5, 0.55,
    'Evaluation: RMSE  |  NSE  |  MAE  |  POD  |  FAR\n'
    'Best Model: Linear Regression — NSE 0.998 (+1d), NSE 0.985 (holdout)',
    fc='#922B21', tc='white', fs=8.5)

# ── Row 8: Output ─────────────────────────────────────────────────────────────
arrow(ax, 5.0, 3.3, 5.0, 2.7)
box(ax, 2.5, 2.4, 3.5, 0.55,
    'Predicted Water Level (m)\nvs Danger Level 19.05 m',
    fc='#0b5394', tc='white', fs=8.5)
box(ax, 7.5, 2.4, 3.5, 0.55,
    'AquaGuard Dashboard\nAlert Triggered at 18.55 m',
    fc='#c0392b', tc='white', fs=8.5)
arrow(ax, 5.0, 2.7, 2.5, 2.65)
arrow(ax, 5.0, 2.7, 7.5, 2.65)

plt.tight_layout()
out_g = OUT_DIR / 'FigG_model1_pipeline_diagram.png'
plt.savefig(out_g, dpi=150, bbox_inches='tight', facecolor='white')
plt.savefig(str(out_g).replace('.png', '.pdf'), bbox_inches='tight', facecolor='white')
plt.close()
print(f"  Saved: {out_g}")


# ─────────────────────────────────────────────────────────────────────────────
# FIGURE H — Data Sources Relationship Diagram
# ─────────────────────────────────────────────────────────────────────────────
print("Building Figure H ...")

fig, ax = plt.subplots(figsize=(12, 8))
fig.patch.set_facecolor('#ffffff')
ax.set_xlim(0, 12)
ax.set_ylim(0, 9)
ax.axis('off')

ax.text(6, 8.6, 'MODEL 1 — DATA SOURCES & USAGE ROLES',
        ha='center', va='center', fontsize=13, fontweight='bold', color='#1f3864')

# Legend row
for x, fc, label in [(1.5, '#1f3864', 'Primary — Used in Training'),
                      (5.0, '#1e6b1e', 'Live — Used in Inference'),
                      (8.5, '#7d5a00', 'Cross-Check — Validation Only'),
                      (11.0, '#555', 'Reference — Not in Model')]:
    rect = FancyBboxPatch((x-0.35, 8.1), 0.5, 0.25,
                          boxstyle='round,pad=0.05', fc=fc, ec='none')
    ax.add_patch(rect)
    ax.text(x + 0.35, 8.22, label, va='center', fontsize=7.5, color='#333')

# ── Source boxes ─────────────────────────────────────────────────────────────
# BWDB
box(ax, 2.0, 7.0, 3.2, 0.9,
    'BWDB Gauge SW46.9L\nBahadurabad Daily WL + Discharge\n(2008–2022, 5,479 days)',
    fc='#1f3864', tc='white', fs=8.5)
ax.text(2.0, 6.5, 'PRIMARY\nCredit: BWDB Hydrology Division, Dhaka',
        ha='center', fontsize=7.5, color='#1f3864', style='italic')

# ERA5
box(ax, 6.0, 7.0, 3.2, 0.9,
    'ERA5 via Open-Meteo API\n6 Catchment Grid Points\nHistorical + Real-Time',
    fc='#1e6b1e', tc='white', fs=8.5)
ax.text(6.0, 6.5, 'LIVE INFERENCE\nCredit: Hersbach et al. 2020 / Zippenfenig 2023',
        ha='center', fontsize=7.5, color='#1e6b1e', style='italic')

# FFWC
box(ax, 10.0, 7.0, 3.2, 0.9,
    'FFWC Live Portal\nCurrent-Day Gauge Reading\n(Automated daily fetch)',
    fc='#1e6b1e', tc='white', fs=8.5)
ax.text(10.0, 6.5, 'LIVE INFERENCE\nCredit: FFWC / BWDB, Dhaka',
        ha='center', fontsize=7.5, color='#1e6b1e', style='italic')

# JASON Altimetry
box(ax, 2.0, 5.2, 3.2, 0.9,
    'JASON-2 / JASON-3\nSatellite Radar Altimetry\nVirtual Station at Bahadurabad',
    fc='#7d5a00', tc='white', fs=8.5)
ax.text(2.0, 4.7, 'CROSS-CHECK ONLY\nCredit: ESA / CNES / LEGOS HydroWeb',
        ha='center', fontsize=7.5, color='#7d5a00', style='italic')

# DEM
box(ax, 6.0, 5.2, 3.2, 0.9,
    'Flood Plain DEM\nSentinel-1 / Sentinel-2 SAR\n2016–2022 Annual GeoTIFFs',
    fc='#555', tc='white', fs=8.5)
ax.text(6.0, 4.7, 'REFERENCE (Visualization Only)\nCredit: ESA Copernicus Programme',
        ha='center', fontsize=7.5, color='#555', style='italic')

# FFWC Flood Reports
box(ax, 10.0, 5.2, 3.2, 0.9,
    'FFWC Annual Flood Reports\n2008–2022\nEvent Labels (Flood/No-Flood)',
    fc='#7d5a00', tc='white', fs=8.5)
ax.text(10.0, 4.7, 'EVENT SCORING ONLY\nCredit: FFWC, BWDB Dhaka',
        ha='center', fontsize=7.5, color='#7d5a00', style='italic')

# ── Central Model 1 box ───────────────────────────────────────────────────────
box(ax, 6.0, 3.4, 4.5, 0.85,
    'MODEL 1\nLinear Regression — Multi-Horizon River Forecaster\nBahadurabad, Jamuna River',
    fc='#1f3864', tc='white', fs=10, bold=True)

# ── Arrows from sources to model ─────────────────────────────────────────────
arrow_kw = dict(arrowstyle='->', lw=1.5)

# BWDB → Model
ax.annotate('', xy=(4.0, 3.65), xytext=(2.0, 6.55),
            arrowprops=dict(**arrow_kw, color='#1f3864'))
ax.text(2.5, 5.0, 'WL + Q_R\ntraining data', fontsize=7.5, color='#1f3864',
        ha='center', style='italic')

# ERA5 → Model
ax.annotate('', xy=(5.5, 3.83), xytext=(6.0, 6.55),
            arrowprops=dict(**arrow_kw, color='#1e6b1e'))
ax.text(5.5, 5.0, 'Catchment\nrainfall features', fontsize=7.5, color='#1e6b1e',
        ha='center', style='italic')

# FFWC Live → Model
ax.annotate('', xy=(7.2, 3.65), xytext=(10.0, 6.55),
            arrowprops=dict(**arrow_kw, color='#1e6b1e'))
ax.text(9.3, 5.05, 'Live WL\ninference', fontsize=7.5, color='#1e6b1e',
        ha='center', style='italic')

# JASON → Model (cross-check, dashed)
ax.annotate('', xy=(4.5, 3.4), xytext=(2.0, 4.75),
            arrowprops=dict(arrowstyle='->', color='#7d5a00', lw=1.2, linestyle='dashed'))
ax.text(2.8, 3.9, 'Flood-peak\ncross-check', fontsize=7.5, color='#7d5a00',
        ha='center', style='italic')

# FFWC Reports → Model (event scoring, dashed)
ax.annotate('', xy=(7.5, 3.4), xytext=(10.0, 4.75),
            arrowprops=dict(arrowstyle='->', color='#7d5a00', lw=1.2, linestyle='dashed'))
ax.text(9.3, 3.9, 'POD/FAR\nevent scoring', fontsize=7.5, color='#7d5a00',
        ha='center', style='italic')

# ── Output box ────────────────────────────────────────────────────────────────
arrow(ax, 6.0, 2.97, 6.0, 2.4)
box(ax, 6.0, 2.1, 5.5, 0.55,
    'Predicted Water Level (m) → Danger Level Comparison → Dashboard Alert Banner',
    fc='#c0392b', tc='white', fs=9, bold=True)

# ── Catchment map inset label ─────────────────────────────────────────────────
ax.text(6.0, 1.5,
        'Catchment bounding box monitored via ERA5:  82°E – 98°E, 24°N – 32°N  '
        '(~600,000 km² — 92% outside Bangladesh)',
        ha='center', fontsize=8.5, color='#333',
        bbox=dict(boxstyle='round,pad=0.4', fc='#e8f4fd', ec='#1e6b1e', lw=1.2))

plt.tight_layout()
out_h = OUT_DIR / 'FigH_data_sources_diagram.png'
plt.savefig(out_h, dpi=150, bbox_inches='tight', facecolor='white')
plt.savefig(str(out_h).replace('.png', '.pdf'), bbox_inches='tight', facecolor='white')
plt.close()
print(f"  Saved: {out_h}")

print("\nAll done. Files saved to:")
for f in sorted(OUT_DIR.iterdir()):
    print(f"  {f.name}")
