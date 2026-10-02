# Figure & Table Captions (Bahadurabad Water-Level Forecasting Study)

## Figures

### Phase 1: Data Audit
- **Figure F01 (`F01_full_wl_series.png/.pdf`):** Complete 15-year daily water level series at Bahadurabad station (2008–2022) with Danger Level (19.05 m), Extreme Level (19.90 m), and RHWL (20.63 m) thresholds overlay. Missing data days (N=335) are explicitly highlighted along the bottom axis.
- **Figure F02 (`F02_missing_data_heatmap.png/.pdf`):** Heatmap of missing daily water level observations by year and month. Missing values cluster almost exclusively in dry season / shoulder months (February, May, October) rather than the monsoon flood season (June–September).
- **Figure F03 (`F03_annual_maxima_comparison.png/.pdf`):** Scatter plot of dataset annual maxima against official BWDB recorded annual maxima (2008–2017) overlaid with a 1:1 line. Gauge levels match BWDB records with minimal bias (<0.02 m) and precise peak dates (0–2 days offset).
- **Figure F04 (`F04_seasonal_cycle_and_peaks.png/.pdf`):** (Left) Monthly water level boxplots demonstrating clear monsoon seasonality peaking in July–August. (Right) Bar chart of annual maximum water levels, highlighting major flood years (2010, 2012, 2016, 2017, 2019, 2020).
- **Figure F05 (`F05_flood_events_timeline_histogram.png/.pdf`):** (Left) Timeline and peak water level stage for all 34 independent flood events (consecutive days >= 19.05 m). (Right) Histogram of flood event durations (mean duration 13.7 days, maximum 44 days).
- **Figure F06 (`F06_acf_pacf_wl.png/.pdf`):** Autocorrelation (ACF) and Partial Autocorrelation (PACF) functions for Bahadurabad daily water levels up to 30 days. ACF remains exceptionally high (>0.95 at 7 days), confirming strong persistent memory.
- **Figure F07 (`F07_rating_curve_wl_vs_q.png/.pdf`):** Scatter plot of water level vs rated discharge $Q_R$, showing a deterministic single-valued rating curve relationship and justifying the decision not to model discharge separately.

### Phase 2 & 3: Features & Design
- **Figure F08 (`F08_catchment_rainfall_vs_wl.png/.pdf`):** Time series zoom (2019–2020) comparing Brahmaputra catchment rainfall against downstream water level, with cross-correlation analysis showing peak response lag at 3–7 days.
- **Figure F09 (`F09_station_catchment_schematic.png/.pdf`):** Spatial schematic of the Brahmaputra catchment envelope (82–98°E, 24–32°N) and Bahadurabad gauge location (25.1°N, 89.6°E).
- **Figure F10 (`F10_loyo_cv_holdout_scheme.png/.pdf`):** Diagram illustrating the Leave-One-Year-Out (LOYO) cross-validation scheme across 12 development years (2008–2019) with boundary gaps, and the final 3-year holdout split (2020–2022).

### Phase 4 & 5: Model Comparisons
- **Figure F11 (`F11_baseline_comparison_h1.png/.pdf`):** Performance comparison of baseline models (Persistence, Persistence+Trend, Anomaly Persistence) at +1 day lead time.
- **Figure F12 (`F12_hyperparameter_validation_curves.png/.pdf`):** Validation loss curves showing hyperparameter tuning for Ridge regularization alpha and XGBoost tree depth.
- **Figure F13 (`F13_lstm_loss_curves.png/.pdf`):** PyTorch LSTM training and validation loss trajectories across 40 epochs showing stable convergence without overfitting.
- **Figure F14 (`F14_rmse_vs_lead_time_all_models.png/.pdf`):** **Main Result:** LOYO validation RMSE vs lead time (1, 3, 7, 14 days) across all evaluated model families.
- **Figure F15 (`F15_skill_vs_lead_time.png/.pdf`):** Forecast skill score relative to the Anomaly Persistence baseline across all lead times.
- **Figure F16 (`F16_per_year_rmse_boxplots.png/.pdf`):** Boxplots of per-year validation RMSE across the 12 LOYO fold years, illustrating cross-year model stability.
- **Figure F17 (`F17_feature_ablation_a_b_c.png/.pdf`):** Feature set ablation comparing Feature Set A (lags 0-7), Set B (+trends/harmonics), and Set C (+catchment rainfall).
- **Figure F18 (`F18_models_metrics_heatmap.png/.pdf`):** Heatmap matrix ranking models across multiple evaluation metrics (RMSE, MAE, NSE, Flood Season RMSE, Peak Error) at +3 day lead time.

### Phase 6: Diagnostic Analysis
- **Figure F19 (`F19_flood_year_hydrographs.png/.pdf`):** Observed vs predicted hydrographs during major flood years (2019, 2020) at +1, +3, and +7 day lead times with Danger Level overlay.
- **Figure F20 (`F20_scatter_1to1_by_horizon.png/.pdf`):** 1:1 scatter plots of observed vs predicted water levels across all 4 lead times, color-coded by water level stage.
- **Figure F21 (`F21_residual_diagnostics.png/.pdf`):** Residual diagnostics including residual histogram, error boxplots by level stage, and residual autocorrelation.
- **Figure F22 (`F22_feature_importance.png/.pdf`):** Feature importance matrix for the selected model, demonstrating dominant weight on lag-1 state and recent rate of change.
- **Figure F23 (`F23_event_timeline_confusion_matrix.png/.pdf`):** Event timeline of achieved lead times for the 34 flood events alongside the confusion matrix for Danger Level exceedance.
- **Figure F24 (`F24_final_holdout_performance_2020_2022.png/.pdf`):** Performance of the selected model on the untouched 3-year final holdout test set (2020–2022) at +3 day lead time.

---

## Tables

- **Table T1 (`T1_dataset_summary.csv`):** Complete dataset summary metrics including record period, row counts, missing data share, threshold levels, and flood event statistics.
- **Table T2 (`T2_hyperparameter_grids.csv`):** Comprehensive hyperparameter search grids and optimal selected values for every candidate model.
- **Table T3 (`T3_loyo_results_all_horizons.csv`):** Detailed LOYO cross-validation metrics (RMSE, MAE, Bias, NSE) for all models across horizons +1, +3, +7, +14 days.
- **Table T4 (`T4_flood_season_and_peak_metrics.csv`):** Flood-season RMSE (June–Sept), peak error MAE, and level-binned RMSE breakdown.
- **Table T5 (`T5_event_scoring.csv`):** Event exceedance scoring metrics including Hit Rate (POD) and False Alarm Ratio (FAR) for predicting Danger Level crossing.
- **Table T6 (`T6_final_holdout_results.csv`):** Out-of-sample performance of the winning model on the 2020–2022 test holdout.
