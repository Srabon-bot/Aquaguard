# Enhanced Model Artifacts

This directory holds **enhanced** model artifacts (calibrated, ensemble, coastal) for the AquaGuard flood-risk system.

## Important: Never modify ackend/models/

The original production artifacts live in ackend/models/. They are the **canonical, frozen** models — do not modify, delete, or retrain them in place. Any improvement work happens here in ackend/models_improved/, and the swap is done by changing a single import line in ackend/app/main.py.

## Directory structure

\\\
backend/models_improved/
+-- README.md
+-- <version>/                      # e.g. 2026-08-30a
¦   +-- model_<horizon>.joblib       # main LightGBM classifier per horizon (24h/48h/72h)
¦   +-- model_<horizon>_calibrator.joblib  # IsotonicRegression calibrator (uses .transform())
¦   +-- model_<horizon>_threshold.json      # decision threshold + target_recall
¦   +-- feature_schema.json          # per-horizon feature columns + categorical values
¦   +-- model_metadata.json          # version, trained_at, calibration_method, metrics
+-- coastal/
    +-- <version>/
        +-- model.joblib
        +-- feature_schema.json
\\\

## How to deploy an enhanced model

1. Train the model with \python train/train_model.py --version <features_version>\.
2. Copy the trained artifacts into \ackend/models_improved/<version>/\ (and optionally \ackend/models_improved/coastal/<version>/\).
3. Edit \ackend/app/main.py\ to import \EnhancedFloodGBMModel\ from \pp.models_enhanced.flood_gbm_model\ instead of \FloodGBMModel\ from \pp.models.flood_gbm_model\.
4. Restart the API.

## Calibrator note

The calibrator saved by \	rain_model.py\ is a \sklearn.isotonic.IsotonicRegression\. It exposes \.transform(X)\ (not \.predict_proba()\). The serving wrapper in \pp/models_enhanced/flood_gbm_model.py\ calls \.transform()\ correctly — do not "fix" it back to \predict_proba\.

## Version naming

Use ISO-date-based version strings (e.g. \2026-08-30a\) so that lexicographic sorting also sorts chronologically. The \\ suffix distinguishes multiple model runs trained on the same feature version.
