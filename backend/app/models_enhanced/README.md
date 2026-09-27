# Enhanced Model Workspace (models_enhanced)

This directory is the **experimental/enhanced model workspace** for AquaGuard flood-risk predictions. It contains a parallel implementation that can be swapped in/out without touching the original code.

## Structure

- `__init__.py` — exact copy of original
- `schemas.py` — exact copy of original
- `flood_gbm_model.py` — enhanced version with calibration, uncertainty, ensemble, and coastal support
- `risk_model.py` — exact copy of original (kept as rollback reference)
- `README.md` — this file

## Original Code Location

The original, production-ready model code lives in:
- `backend/app/models/`

**Never edit files directly in `backend/app/models/`.** All experiments and improvements should happen here in `backend/app/models_enhanced/`.

## How to Test

To test the enhanced model, change the import in `backend/app/main.py`:

```python
# From:
from app.models.flood_gbm_model import FloodGBMModel, build_reasoning

# To:
from app.models_enhanced.flood_gbm_model import EnhancedFloodGBMModel, build_enhanced_reasoning
```

You may also need to update the class instantiation in `main.py`:
```python
# From:
model = FloodGBMModel.load(version)

# To:
model = EnhancedFloodGBMModel.load(version)
```

## How to Revert

To revert back to the original model, simply change the import in `backend/app/main.py` back to:
```python
from app.models.flood_gbm_model import FloodGBMModel, build_reasoning
```

## New Features in Enhanced Model

1. **Probability Calibration** — Platt scaling / isotonic regression applied per horizon to improve probability reliability
2. **Quantile Regression** — Q10/Q90 uncertainty intervals for each prediction horizon
3. **Multi-Model Ensemble** — Support for LightGBM + XGBoost + CatBoost + LogisticRegression with configurable weights
4. **Model Metadata & Versioning** — `model_metadata.json` tracks training date, features, AUC-PR, and calibration method
5. **Coastal Flood Module** — Separate `CoastalFloodModel` for coastal-specific risk factors (distance to coast, elevation, tidal phase, surge index)

## Artifacts Location

Trained enhanced model artifacts should be stored in:
- `backend/models_improved/` (created as a placeholder)

This keeps improved artifacts completely separate from the original `backend/models/` directory.
