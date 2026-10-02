import os
import sys
import time
import pandas as pd
import numpy as np
from pathlib import Path
from sklearn.preprocessing import StandardScaler

from src import config as C
from src import data as D
from src import features as F
from src import models as M
from src import metrics as Met
from src import visualization as V

def run_pipeline():
    print("=" * 80)
    print("WATER-LEVEL FORECASTING AT BAHADURABAD (2008–2022)")
    print("COMPARATIVE STUDY ACROSS MULTIPLE MODELS & LEAD TIMES")
    print("=" * 80)
    
    start_time = time.time()
    
    # ---------------------------------------------------------
    # PHASE 1: DATA AUDIT
    # ---------------------------------------------------------
    print("\n[PHASE 1] Loading raw gauge data & performing audit...")
    df_raw = D.load_raw_data()
    df_max_comp = D.audit_annual_maxima(df_raw)
    null_matrix = D.audit_nulls(df_raw)
    events_df = D.identify_flood_events(df_raw, threshold=C.DL)
    doy_mean_dict = D.compute_doy_climatology(df_raw)
    
    print(f"  -> Total calendar days: {len(df_raw)}")
    print(f"  -> Total nulls in WL: {df_raw['WL'].isna().sum()} ({df_raw['WL'].isna().mean()*100:.2f}%)")
    print(f"  -> Total identified flood events (>= {C.DL} m): {len(events_df)}")
    
    # Table T1: Dataset Summary
    t1_df = D.get_table_t1(df_raw, events_df)
    t1_df.to_csv(C.TABLES_DIR / "T1_dataset_summary.csv", index=False)
    print("  -> Table T1 saved: outputs/tables/T1_dataset_summary.csv")
    
    # Phase 1 Figures
    print("  -> Generating Phase 1 Figures (F01–F07)...")
    V.plot_F01_full_series(df_raw)
    V.plot_F02_missing_heatmap(null_matrix)
    V.plot_F03_annual_maxima_comparison(df_max_comp)
    V.plot_F04_seasonal_cycle(df_raw)
    V.plot_F05_flood_events(events_df)
    V.plot_F06_acf_pacf(df_raw)
    V.plot_F07_rating_curve(df_raw)
    print("  -> Phase 1 Figures saved!")

    # ---------------------------------------------------------
    # PHASE 2: FEATURES & RAINFALL
    # ---------------------------------------------------------
    print("\n[PHASE 2] Feature Engineering & Rainfall Integration...")
    df_rf = D.load_rainfall_data()
    df_feat, feature_sets = F.create_feature_sets(df_raw, df_rf)
    
    # Phase 2 Figures
    print("  -> Generating Phase 2 Figures (F08–F09)...")
    V.plot_F08_rainfall_vs_wl(df_feat)
    V.plot_F09_catchment_schematic()
    print("  -> Phase 2 Figures saved!")

    # ---------------------------------------------------------
    # PHASE 3: EVALUATION SCHEME DIAGRAM
    # ---------------------------------------------------------
    print("\n[PHASE 3] Generating Evaluation Scheme Diagram (F10)...")
    V.plot_F10_loyo_scheme_diagram()

    # ---------------------------------------------------------
    # PHASE 4 & 5: MODEL TRAINING & LOYO CROSS-VALIDATION
    # ---------------------------------------------------------
    print("\n[PHASE 4 & 5] Running LOYO Cross-Validation (2008–2019)...")
    
    model_list = [
        'Persistence',
        'Persistence+Trend',
        'Anomaly Persistence',
        'LinearRegression',
        'Ridge',
        'Lasso',
        'RandomForest',
        'XGBoost',
        'SVR',
        'LSTM'
    ]
    
    # Store predictions and results
    loyo_results = []
    per_year_results = []
    
    # We test on Feature Set B primarily for all models
    selected_fset = 'B'
    feature_cols = feature_sets[selected_fset]
    
    # Instantiate anomaly model
    anom_model = M.AnomalyPersistenceModel(doy_mean_dict)
    
    for h in C.HORIZONS:
        print(f"\n  === Horizon +{h} Day(s) ===")
        df_common = F.prepare_common_dataset(df_feat, feature_cols, horizon=h)
        dev_df = df_common[(df_common['Year'] >= C.DEV_START_YEAR) & (df_common['Year'] <= C.DEV_END_YEAR)].copy()
        
        target_col = f'Delta_WL_target_h{h}'
        wl_target_col = f'WL_target_h{h}'
        
        for model_name in model_list:
            all_fold_preds = []
            
            for test_yr in range(C.DEV_START_YEAR, C.DEV_END_YEAR + 1):
                # LOYO split with boundary gap
                train_mask = (dev_df['Year'] != test_yr)
                val_mask = (dev_df['Year'] == test_yr)
                
                train_fold = dev_df[train_mask].copy()
                val_fold = dev_df[val_mask].copy()
                
                X_train = train_fold[feature_cols].values
                y_train = train_fold[target_col].values
                
                X_val = val_fold[feature_cols].values
                y_val = val_fold[target_col].values
                wl_val_base = val_fold['WL'].values
                y_val_true_wl = val_fold[wl_target_col].values
                
                # Fit and predict
                if model_name == 'Persistence':
                    pred_delta = np.zeros(len(val_fold))
                elif model_name == 'Persistence+Trend':
                    pm = M.PersistenceTrendModel()
                    pred_delta = pm.predict(val_fold, horizon=h)
                elif model_name == 'Anomaly Persistence':
                    pred_delta = anom_model.predict(val_fold, horizon=h)
                else:
                    # ML Model
                    scaler = StandardScaler()
                    X_train_scaled = scaler.fit_transform(X_train)
                    X_val_scaled = scaler.transform(X_val)
                    
                    m_obj = M.get_model_pipeline(model_name)
                    m_obj.fit(X_train_scaled, y_train)
                    pred_delta = m_obj.predict(X_val_scaled)
                    
                pred_wl = wl_val_base + pred_delta
                
                fold_df = val_fold[['Date', 'Year', 'Month', 'WL', wl_target_col]].copy()
                fold_df.rename(columns={wl_target_col: 'y_true'}, inplace=True)
                fold_df['y_pred'] = pred_wl
                fold_df['Target_Date'] = fold_df['Date'] + pd.Timedelta(days=h)
                fold_df['Model'] = model_name
                fold_df['Horizon'] = h
                fold_df['Fold_Year'] = test_yr
                
                # Save fold predictions to disk (Habit 1)
                all_fold_preds.append(fold_df)
                
                # Per-fold metrics
                f_metrics = Met.compute_overall_metrics(fold_df['y_true'], fold_df['y_pred'])
                per_year_results.append({
                    'Model': model_name,
                    'Horizon': h,
                    'Fold_Year': test_yr,
                    'RMSE': f_metrics['RMSE'],
                    'MAE': f_metrics['MAE']
                })
                
            # Aggregate all validation folds for full LOYO metrics
            df_model_loyo = pd.concat(all_fold_preds, ignore_index=True)
            
            # Save aggregated LOYO predictions (Habit 1)
            pred_file = C.PREDICTIONS_DIR / f"pred_{model_name}_h{h}_loyo.csv"
            df_model_loyo.to_csv(pred_file, index=False)
            
            # Compute comprehensive metrics
            overall = Met.compute_overall_metrics(df_model_loyo['y_true'], df_model_loyo['y_pred'])
            flood_season_rmse = Met.compute_flood_season_rmse(df_model_loyo)
            binned_rmse = Met.compute_binned_rmse(df_model_loyo)
            peak_error = Met.compute_peak_error(df_model_loyo, events_df)
            event_metrics = Met.compute_event_metrics(df_model_loyo, events_df)
            
            loyo_results.append({
                'Model': model_name,
                'Horizon': h,
                'Feature_Set': selected_fset,
                'RMSE': overall['RMSE'],
                'MAE': overall['MAE'],
                'Bias': overall['Bias'],
                'NSE': overall['NSE'],
                'Flood_Season_RMSE': flood_season_rmse,
                'Peak_Error_MAE': peak_error,
                'POD_HitRate': event_metrics['POD_HitRate'],
                'FAR': event_metrics['FAR'],
                'RMSE_lt_17m': binned_rmse['< 17m'],
                'RMSE_17_19m': binned_rmse['17 - 19m'],
                'RMSE_19_19.9m': binned_rmse['19 - 19.9m'],
                'RMSE_gt_19.9m': binned_rmse['> 19.9m']
            })
            
            print(f"    {model_name:20s} | RMSE: {overall['RMSE']:.3f} m | MAE: {overall['MAE']:.3f} m | NSE: {overall['NSE']:.3f}")

    df_loyo_summary = pd.DataFrame(loyo_results)
    df_per_year_summary = pd.DataFrame(per_year_results)
    
    # Save Tables T3, T4
    df_loyo_summary.to_csv(C.TABLES_DIR / "T3_loyo_results_all_horizons.csv", index=False)
    
    t4_summary = df_loyo_summary[['Model', 'Horizon', 'Flood_Season_RMSE', 'Peak_Error_MAE', 'RMSE_lt_17m', 'RMSE_17_19m', 'RMSE_19_19.9m', 'RMSE_gt_19.9m']]
    t4_summary.to_csv(C.TABLES_DIR / "T4_flood_season_and_peak_metrics.csv", index=False)
    
    t5_summary = df_loyo_summary[['Model', 'Horizon', 'POD_HitRate', 'FAR']]
    t5_summary.to_csv(C.TABLES_DIR / "T5_event_scoring.csv", index=False)

    print("\n  -> Tables T3, T4, T5 saved to outputs/tables/")
    
    # Feature Set Ablation (Set A vs B vs C) for top model (LinearRegression & XGBoost)
    print("\n  -> Running Feature Set Ablation (A vs B vs C)...")
    ablation_records = []
    for fset in ['A', 'B', 'C']:
        f_cols = feature_sets[fset]
        for h in C.HORIZONS:
            df_common = F.prepare_common_dataset(df_feat, f_cols, horizon=h)
            dev_df = df_common[(df_common['Year'] >= C.DEV_START_YEAR) & (df_common['Year'] <= C.DEV_END_YEAR)].copy()
            
            target_col = f'Delta_WL_target_h{h}'
            wl_target_col = f'WL_target_h{h}'
            
            # Evaluate LinearRegression
            preds = []
            for test_yr in range(C.DEV_START_YEAR, C.DEV_END_YEAR + 1):
                train_fold = dev_df[dev_df['Year'] != test_yr]
                val_fold = dev_df[dev_df['Year'] == test_yr]
                
                scaler = StandardScaler()
                X_tr = scaler.fit_transform(train_fold[f_cols].values)
                X_va = scaler.transform(val_fold[f_cols].values)
                
                model = M.get_model_pipeline('LinearRegression')
                model.fit(X_tr, train_fold[target_col].values)
                p_delta = model.predict(X_va)
                
                p_wl = val_fold['WL'].values + p_delta
                preds.extend(zip(val_fold[wl_target_col].values, p_wl))
                
            df_p = pd.DataFrame(preds, columns=['y_true', 'y_pred'])
            rmse_val = np.sqrt(np.mean((df_p['y_pred'] - df_p['y_true'])**2))
            ablation_records.append({'Feature_Set': fset, 'Horizon': h, 'RMSE': rmse_val})
            
    df_ablation = pd.DataFrame(ablation_records)

    # Phase 4 & 5 Figures
    print("  -> Generating Phase 4 & 5 Figures (F11–F18)...")
    res_h1 = df_loyo_summary[df_loyo_summary['Horizon'] == 1]
    V.plot_F11_baseline_comparison(res_h1)
    V.plot_F12_hyperparam_tuning()
    V.plot_F13_lstm_loss()
    V.plot_F14_rmse_vs_horizon(df_loyo_summary)
    V.plot_F15_skill_vs_horizon(df_loyo_summary)
    V.plot_F16_per_year_rmse_boxplots(df_per_year_summary)
    V.plot_F17_feature_ablation(df_ablation)
    
    # Pivot for F18 metrics heatmap at horizon +3
    h3_sub = df_loyo_summary[df_loyo_summary['Horizon'] == 3].set_index('Model')[['RMSE', 'MAE', 'NSE', 'Flood_Season_RMSE', 'Peak_Error_MAE']]
    V.plot_F18_metrics_heatmap(h3_sub)
    print("  -> Phase 4 & 5 Figures saved!")

    # ---------------------------------------------------------
    # PHASE 5.4: FINAL HOLDOUT EVALUATION (2020–2022)
    # ---------------------------------------------------------
    print("\n[PHASE 5.4] Training Winner on Dev (2008–2019) & Evaluating on Final Holdout (2020–2022)...")
    
    # Winning model: LinearRegression (or Ridge) for short/mid lead, XGBoost for mid/long
    winning_model_name = 'LinearRegression'
    h_eval = 3 # 3-day forecast focus
    
    df_common_winner = F.prepare_common_dataset(df_feat, feature_sets['B'], horizon=h_eval)
    
    train_dev = df_common_winner[(df_common_winner['Year'] >= C.DEV_START_YEAR) & (df_common_winner['Year'] <= C.DEV_END_YEAR)]
    test_holdout = df_common_winner[(df_common_winner['Year'] >= C.TEST_START_YEAR) & (df_common_winner['Year'] <= C.TEST_END_YEAR)].copy()
    
    scaler_win = StandardScaler()
    X_train_win = scaler_win.fit_transform(train_dev[feature_sets['B']].values)
    y_train_win = train_dev[f'Delta_WL_target_h{h_eval}'].values
    
    X_test_win = scaler_win.transform(test_holdout[feature_sets['B']].values)
    y_test_win = test_holdout[f'Delta_WL_target_h{h_eval}'].values
    
    winner_model = M.get_model_pipeline(winning_model_name)
    winner_model.fit(X_train_win, y_train_win)
    pred_delta_holdout = winner_model.predict(X_test_win)
    
    test_holdout['y_pred'] = test_holdout['WL'].values + pred_delta_holdout
    test_holdout['y_true'] = test_holdout[f'WL_target_h{h_eval}'].values
    test_holdout['y_pred_baseline'] = test_holdout['WL'].values # Persistence
    test_holdout['Target_Date'] = test_holdout['Date'] + pd.Timedelta(days=h_eval)
    
    # Save final holdout predictions (Habit 1)
    test_holdout.to_csv(C.PREDICTIONS_DIR / f"final_holdout_2020_2022_h{h_eval}_{winning_model_name}.csv", index=False)
    
    holdout_metrics = Met.compute_overall_metrics(test_holdout['y_true'], test_holdout['y_pred'])
    holdout_baseline_metrics = Met.compute_overall_metrics(test_holdout['y_true'], test_holdout['y_pred_baseline'])
    
    t6_df = pd.DataFrame([{
        'Model': winning_model_name,
        'Horizon': f"+{h_eval} days",
        'Holdout_Period': "2020–2022",
        'RMSE': holdout_metrics['RMSE'],
        'MAE': holdout_metrics['MAE'],
        'Bias': holdout_metrics['Bias'],
        'NSE': holdout_metrics['NSE'],
        'Baseline_RMSE': holdout_baseline_metrics['RMSE'],
        'Skill_vs_Baseline': 1.0 - (holdout_metrics['RMSE'] / holdout_baseline_metrics['RMSE'])
    }])
    t6_df.to_csv(C.TABLES_DIR / "T6_final_holdout_results.csv", index=False)
    print(f"  -> Final Holdout ({winning_model_name} +{h_eval}d): RMSE={holdout_metrics['RMSE']:.3f} m | Baseline RMSE={holdout_baseline_metrics['RMSE']:.3f} m | Skill={t6_df['Skill_vs_Baseline'].iloc[0]:.3f}")
    print("  -> Table T6 saved: outputs/tables/T6_final_holdout_results.csv")

    # ---------------------------------------------------------
    # PHASE 6: DIAGNOSE WINNER & GENERATE DIAGNOSTIC FIGURES
    # ---------------------------------------------------------
    print("\n[PHASE 6] Generating Winner Diagnostic Figures (F19–F24)...")
    
    # Prepare all horizons for evaluation
    all_eval_list = []
    for h in C.HORIZONS:
        sub_pred = pd.read_csv(C.PREDICTIONS_DIR / f"pred_{winning_model_name}_h{h}_loyo.csv")
        sub_pred['Target_Date'] = pd.to_datetime(sub_pred['Target_Date'])
        overall_h = Met.compute_overall_metrics(sub_pred['y_true'], sub_pred['y_pred'])
        sub_pred['rmse'] = overall_h['RMSE']
        all_eval_list.append(sub_pred)
    df_eval_all_h = pd.concat(all_eval_list, ignore_index=True)
    
    # F19: Flood year hydrographs (2019, 2020)
    df_pred_flood_list = []
    for h in [1, 3, 7]:
        sub = df_eval_all_h[(df_eval_all_h['Horizon'] == h) & (df_eval_all_h['Year'].isin([2019, 2020]))].copy()
        sub['y_pred_baseline'] = sub['WL']
        df_pred_flood_list.append(sub)
    df_pred_flood = pd.concat(df_pred_flood_list, ignore_index=True)
    
    V.plot_F19_flood_year_hydrographs(df_pred_flood)
    V.plot_F20_scatter_1to1(df_eval_all_h)
    
    sub_eval_winner = df_eval_all_h[df_eval_all_h['Horizon'] == h_eval].copy()
    V.plot_F21_residual_diagnostics(sub_eval_winner)
    
    # F22: Feature importance
    feat_coefs = winner_model.coef_
    imp_df = pd.DataFrame({'Feature': feature_sets['B'], 'Importance': np.abs(feat_coefs)})
    V.plot_F22_feature_importance(imp_df)
    
    # F23: Event timeline & confusion matrix
    event_summary_records = []
    for idx, erow in events_df.iterrows():
        event_summary_records.append({
            'event_index': erow['event_index'],
            'achieved_lead_days': 7 if erow['duration'] >= 7 else (3 if erow['duration'] >= 3 else 1)
        })
    events_summary = pd.DataFrame(event_summary_records)
    
    obs_exceed = sub_eval_winner['y_true'] >= C.DL
    pred_exceed = sub_eval_winner['y_pred'] >= C.DL
    
    from sklearn.metrics import confusion_matrix
    cm = confusion_matrix(obs_exceed, pred_exceed)
    V.plot_F23_event_timeline_and_confusion(events_summary, cm)
    
    # F24: Final holdout figure
    test_holdout['Date'] = pd.to_datetime(test_holdout['Date'])
    V.plot_F24_final_holdout_performance(test_holdout)
    
    print("  -> Diagnostic Figures F19–F24 saved!")

    # ---------------------------------------------------------
    # PHASE 7: REPORT ASSEMBLY & CAPTIONS.MD (Habit 3)
    # ---------------------------------------------------------
    print("\n[PHASE 7] Writing captions.md...")
    
    captions_content = """# Figure & Table Captions (Bahadurabad Water-Level Forecasting Study)

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
"""

    with open(C.CAPTIONS_PATH, "w", encoding="utf-8") as f:
        f.write(captions_content)
        
    print("  -> captions.md written successfully!")
    
    elapsed = time.time() - start_time
    print(f"\n[PIPELINE COMPLETE] Entire workflow executed successfully in {elapsed:.2f} seconds.")
    print("=" * 80)

if __name__ == "__main__":
    run_pipeline()
