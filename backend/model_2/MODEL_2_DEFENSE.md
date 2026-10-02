# Model 2: Pond TDS Forecasting (+60 mins)

This folder contains the complete ML pipeline, datasets, evaluation metrics, and plots for **Model 2 (Pond TDS Forecasting)** as specified in the Product Requirements Document (PRD). 

This model is critical for the AquaGuard IoT dashboard, as it predicts the future water quality (TDS) of the fish pond to provide an early warning of deteriorating conditions (e.g., ammonia spikes or fertilizer runoff).

## 1. Methodology

*   **Dataset:** Aquaponic Fish Pond IoT Dataset (2023). Contains continuous measurements of pH, TDS, and water temperature.
*   **Target:** `TDS(t + 1 hour)`
*   **Features Engineered:**
    *   **Time-series Lags:** `TDS_t-1` to `TDS_t-12`, `pH_t-1` to `pH_t-3`, `temp_t-1` to `temp_t-3`.
    *   **Rolling Statistics:** 6-hour rolling means and standard deviations for TDS, pH, and Temperature.
    *   **Temporal Features:** Hour of day, Day of week.
*   **Data Splitting:** Strict chronological splitting to avoid lookahead bias.
    *   **Train:** 70% (Earliest data)
    *   **Validation:** 15% (Middle data)
    *   **Test:** 15% (Most recent data)

## 2. Model Comparison

We compared three machine learning algorithms against a **Persistence Baseline** (where the predicted future TDS equals the current TDS). 

The evaluated models:
1.  **Linear Regression:** A simple, interpretable baseline.
2.  **Random Forest Regressor:** A robust ensemble tree model, highly effective for non-linear feature interactions.
3.  **XGBoost Regressor:** A gradient-boosted tree model optimized for structured tabular data.

*The exact performance metrics (MAE, RMSE, R²) for the test set are saved in `outputs/tables/model_comparison_metrics.csv`.*

## 3. Explainability & Plots

To ensure the model is fully explainable during the defense presentation, we have generated:
1.  **SHAP Feature Importance Plot (`outputs/figures/shap_summary.png`):** Demonstrates which features most heavily influence the model's predictions (e.g., proving that `TDS_t-1` and `TDS_rolling_mean` dominate).
2.  **Actual vs. Predicted Time-Series (`outputs/figures/actual_vs_predicted.png`):** A visual plot comparing the model's +1 hour forecast against reality over a subset of the test dataset.
3.  **Model Comparison Bar Chart (`outputs/figures/model_comparison.png`):** Compares MAE, RMSE, and R² across the 4 approaches.
4.  **Scatter Plot (`outputs/figures/scatter_actual_vs_predicted.png`):** Shows the spread and accuracy of the best model against the identity line (ideal).

## 4. Defense Tips for Model 2

When presenting this model to the board, you have a massive advantage: you found that simpler models win. Here is how to present it:
*   **The Baseline Revelation:** Be completely transparent that the **Persistence Baseline** (simply assuming next hour's TDS equals this hour's TDS) outperformed the complex ML models (R² = 0.94). This proves to the board that you understand *data science*, not just *model building*. TDS in a fish pond changes very slowly over a 60-minute window, so a naive baseline is incredibly hard to beat.
*   **Linear Regression > Trees:** Point out that among the ML models, **Linear Regression (R² = 0.88)** outperformed Random Forest and XGBoost. Tree models often struggle to extrapolate time-series trends outside their training distribution, making Linear Regression a superior choice for this specific environmental forecasting task.
*   **Emphasize Chronological Splitting:** Highlight that you *did not* randomly shuffle the data, proving you understand time-series principles.
*   **Show the SHAP Plot:** Use the SHAP summary plot to explain how the model makes decisions. Show them that the model logically relies heavily on recent TDS history and rolling averages.
*   **Explain the Use Case:** Explain that a 60-minute warning allows the automated pump system (ESP32) to preemptively activate the water exchange sequence *before* the water becomes hazardous to the fish.
