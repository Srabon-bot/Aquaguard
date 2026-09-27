# Archive Analysis & Project Improvement Roadmap

## What Was Done

### 1. `plan.md` updated
Appended **Phase 2: Operational Excellence & Pipeline Hardening (2026-08-30)** with 7 prioritized workstreams, data enhancement opportunities, model architecture improvements, and a rollback strategy.

### 2. `MODEL_BUILD_PLAN.md` updated
Appended **Parts 8–15** with granular checklists before the existing Progress Log:
- **Part 8:** Precision optimization, calibration, tiered alerts
- **Part 9:** Coastal flood / storm surge module
- **Part 10:** Uncertainty quantification
- **Part 11:** Farmer feedback loop
- **Part 12:** Complete CHIRPS backfill + 6 additional data sources
- **Part 13:** Model architecture enhancements (ensemble, quantile, coastal)
- **Part 14:** API & frontend hardening
- **Part 15:** IoT hardware integration

### 3. Safe copy workspace created
| Path | Purpose | Rollback |
|------|---------|----------|
| `backend/app/models_enhanced/` | Enhanced model code (calibration, uncertainty, ensemble, coastal module) | Change import in `main.py` back to `app.models.flood_gbm_model` |
| `backend/models_improved/` | Empty placeholder for new trained artifacts | Delete directory; original `backend/models/` untouched |
| `backend/app/models/` (original) | **Untouched.** Synthetic `risk_model.py` preserved as reference. | N/A |

**To test the enhanced pipeline:** Change one line in `backend/app/main.py`:
```python
# Current (production):
from app.models.flood_gbm_model import FloodGBMModel, build_reasoning

# To test enhanced:
from app.models_enhanced.flood_gbm_model import EnhancedFloodGBMModel, build_enhanced_reasoning
```
Then update the model loading line to `EnhancedFloodGBMModel.load(...)`. To revert, swap the import back.

---

## Dataset Improvements: Free Sources You Can Pull Now

Your current training data is Open-Meteo ERA5 (daily, 1950-present) + Open-Meteo Flood API discharge (1998-present) + GFMS flood labels. This is solid but thin in two dimensions: **temporal depth** (only ~25 years of discharge) and **spatial context** (no terrain, soil, land cover). Here is what you can add for free:

| Dataset | What It Gives You | Effort | Impact |
|---------|------------------|--------|--------|
| **Complete CHIRPS backfill** | Daily satellite rainfall, 1981-present. 26 of 46 years already on disk. | 1-2 days (fix retry logic, resume download) | Extends rainfall history by 20+ years; cross-checks Open-Meteo |
| **GloFAS-ERA5 (Copernicus CDS)** | Daily discharge reanalysis, **1979-present** (40+ years vs. Open-Meteo's ~25). Free registration required. | 2-3 days (signup, `cdsapi` config, download script) | **Biggest single improvement.** Triples discharge history; better for extreme-event training |
| **SRTM DEM (NASA)** | 30m elevation, slope, distance to river. | 1 day (download tiles, extract per-station features) | Critical for flood susceptibility mapping and distinguishing riverine vs. pluvial flooding |
| **SoilGrids (ISRIC)** | Soil type, texture, drainage class, organic carbon at 250m resolution. | 1 day (download, map to stations) | Soil drainage class is a top-cited flood driver in Bangladesh-specific ML papers |
| **Sentinel-1 SAR (Copernicus)** | All-weather, day/night surface water extent maps. | 2-3 days (access hub, download pre/post flood events) | **Gold-standard validation labels.** You can see exactly where water actually went |
| **TerraClimate** | Monthly high-res (4km) climate: precipitation, PET, soil moisture, 1958-present. | 1 day | Long-term climate baseline for trend detection and extreme-event frequency |
| **PERSIANN / GSMaP** | Satellite precipitation alternatives to CHIRPS. | 1 day | Cross-checks rainfall estimates; fills gaps if one source fails |
| **ESA WorldCover** | 10m land cover map (2020-2022). | 1 day | Runoff curve numbers by land use type (urban vs. agricultural vs. forest) |
| **BBS Census + OpenStreetMap** | Population density, road access, drainage network. | 1 day | Impact weighting: a flood warning is more urgent where population is dense and access is poor |

**Recommended pull order by ROI:**
1. GloFAS-ERA5 (triples your discharge data — highest impact)
2. Complete CHIRPS backfill (26 years already done, finish the rest)
3. SRTM DEM + SoilGrids (terrain context, 1 day each)
4. Sentinel-1 SAR (validation gold standard)
5. TerraClimate / WorldCover / BBS (nice-to-have enrichment)

---

## Model Improvements: More Doable, Richer Pipeline

Your current LightGBM setup is already the right primary choice — it is state-of-the-art for tabular flood forecasting, handles missing data natively, and is SHAP-explainable. The improvements below are additive, not replacements:

### Tier 1: Do This Now (1-3 days each)

| Improvement | Why It Helps | How to Implement |
|-------------|-------------|------------------|
| **Probability calibration** | Raw LightGBM probabilities are often overconfident. A calibrated model tells farmers "70% chance" and means it. | Fit `CalibratedClassifierCV` (Platt or isotonic) on validation set; save calibrator alongside model; apply in `predict()` |
| **Ensemble: LightGBM + XGBoost + CatBoost + Logistic Regression** | Ensembles almost always beat single models in tabular tasks. The meta-learner learns which model to trust when. | Train all 4 on same CV folds; use out-of-fold preds to train a Logistic Regression meta-learner; compare vs. single best |
| **Region-specific thresholds** | Brahmaputra (flash floods) needs higher precision than Ganges (slow-rising). One threshold punishes one basin to help another. | Split validation by basin; optimize threshold per basin for 85% recall; store in JSON |
| **Cost-sensitive training** | Directly penalizes false positives during training rather than just at threshold time. | `class_weight='balanced'` or custom `sample_weight` in LightGBM |

### Tier 2: Do This Next (3-7 days each)

| Improvement | Why It Helps | How to Implement |
|-------------|-------------|------------------|
| **Quantile LightGBM** | Farmers need "expected range" not just a point. "60-80% chance" is actionable. "60% chance" is ambiguous. | Retrain with `objective='quantile'`, alpha=0.1/0.5/0.9; save three variants per horizon |
| **Coastal module (Random Forest)** | 30-40% of aquaculture areas are coastal polders where riverine models are irrelevant. A simple model is better than nothing. | Train on distance-to-coast + elevation + surge index; integrate via meta-classifier in API |
| **Tiered alerts (Watch / Warning / Emergency)** | Binary "flood / no flood" forces a single decision. Tiers let farmers calibrate response. | Decouple "issue alert" from "issue emergency" — already partially implemented in `_score_to_level` |

### Tier 3: If Data Supports It (1-2 weeks)

| Improvement | Why It Helps | When to Consider |
|-------------|-------------|------------------|
| **Temporal Fusion Transformer (TFT)** | State-of-the-art for multi-horizon time series with known covariates. Handles seasonality, trends, and uncertainty natively. | When you have >100k training rows and need the last few % of performance |
| **TabNet** | Deep learning for tabular data with built-in attention-based interpretability. | If SHAP becomes too slow for real-time serving |
| **LSTM/GRU sequence model** | Captures long-range temporal dependencies that tree models miss. | If you move to sub-daily (hourly) resolution |

### Recommended Architecture Going Forward

```
┌─────────────────────────────────────────────┐
│                 API Layer                    │
│  /predict/risk  →  Meta-classifier           │
│                    ├─ Riverine: LightGBM     │
│                    │   + XGBoost ensemble    │
│                    │   + Calibration         │
│                    │   + Quantile intervals  │
│                    └─ Coastal: Random Forest │
│                        + surge/tide features │
└─────────────────────────────────────────────┘
           ↓                    ↓
  Calibrated probs      Region thresholds
  Uncertainty bands     Basin-aware tiers
           ↓                    ↓
  Watch / Warning / Emergency (farmer-facing)
```

---

## Rollback Path

Everything is reversible in one file change:

**To test enhanced models:**
```python
# backend/app/main.py, line 12:
from app.models_enhanced.flood_gbm_model import EnhancedFloodGBMModel, build_enhanced_reasoning
# line 63:
model_registry["flood_model"] = EnhancedFloodGBMModel.load(settings.flood_model_version)
```

**To revert to production:**
```python
from app.models.flood_gbm_model import FloodGBMModel, build_reasoning
model_registry["flood_model"] = FloodGBMModel.load(settings.flood_model_version)
```

Original files in `backend/app/models/` and `backend/models/` are completely untouched.
