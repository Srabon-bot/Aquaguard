# Comprehensive Machine Learning Report
**Project:** AquaGuard — Bangladesh Flood Early Warning and IoT Pond Management System

---

## Section 1: Model 1 — River Water-Level Forecasting

### 1.1 Overview & Data
* **Purpose:** Predict future river water levels (+1 to +14 days) to warn aquaculture farmers of impending floods.
* **Dataset:** Historical water level gauge data from the Bangladesh Water Development Board (BWDB) for the Bahadurabad Transit (Jamuna River), combined with upstream catchment rainfall data (Open-Meteo/ERA5).

### 1.2 Step-by-Step Methodology
1. **Data Ingestion & Cleaning:** Raw water levels and daily rainfall were merged. Missing days were interpolated.
2. **Feature Engineering:** We generated autoregressive lag features (water level at $t-1, t-3, t-7$) and cumulative rainfall features.
3. **Validation Strategy (LOYO):** We utilized **Leave-One-Year-Out (LOYO) Cross-Validation**. 
4. **Training:** We trained Multiple Linear Regression, Lasso, Ridge, Random Forest, and XGBoost on historical years and tested on the held-out year.
5. **Thresholding:** The continuous ML prediction (e.g., 19.12m) is passed through a rule-based layer that compares it to the official BWDB Danger Level (19.05m) to output a categorical warning (NORMAL/WARNING/DANGER/EXTREME).

### 1.3 Techniques Chosen & Rationale
* **Why Continuous Regression instead of Classification?** Predicting a vague "Flood" vs "No Flood" label is unhelpful. Predicting continuous meters allows the dashboard to say exactly *how far* the water is from the danger level, letting farmers calculate embankment heights.
* **Why LOYO Cross-Validation?** Standard $K$-Fold cross-validation randomly shuffles data. If you shuffle time-series data, the model can "look into the future," causing extreme data leakage. LOYO trains on (for example) 2010-2021 and tests on 2022, proving the model works on unseen future monsoon seasons.

### 1.4 Model Comparison
We compared simple linear models against complex tree models.
* **Result:** For short-term horizons (+1 to +3 days), **Linear Regression** and **Ridge Regression** consistently outperformed Random Forest and XGBoost (lowest RMSE). 
* **Why?** Tree-based models (Random Forest) cannot extrapolate beyond their training data. If a new flood is 10cm higher than any flood in the training set, a tree model will cap its prediction. Linear models extrapolate linear trends perfectly, making them superior for extreme hydrological events.

---

## Section 2: Model 2 — Pond TDS Forecasting

### 2.1 Overview & Data
* **Purpose:** Forecast the Total Dissolved Solids (TDS) of the fish pond +60 minutes into the future to warn of deteriorating water quality.
* **Dataset:** Aquaponic Fish Pond IoT Dataset (1327 continuous hourly records of pH, TDS, and Temperature).

### 2.2 Step-by-Step Methodology
1. **Resampling:** Irregular sensor timestamps were resampled to standard 1-hour intervals using mean aggregation.
2. **Feature Engineering:** 
   * Created history lags: $TDS_{t-1}, TDS_{t-2}$, etc.
   * Created **Rolling Statistics**: 6-hour rolling mean and rolling standard deviation for all sensors to smooth out sensor noise.
3. **Target Shift:** The target variable was created by shifting the TDS column by -1 (predicting the next hour).
4. **Chronological Split:** Data was split strictly chronologically (70% Train, 15% Validation, 15% Test).
5. **SHAP Integration:** TreeExplainer was used to extract feature importances from the models.

### 2.3 Techniques Chosen & Rationale
* **Why Rolling Averages?** Raw IoT sensors fluctuate wildly due to hardware noise or fish swimming near the probe. A 6-hour rolling average provides the ML model with the true underlying environmental trend.
* **Why the Persistence Baseline?** In environmental forecasting, water quality changes slowly. A persistence baseline mathematically states $TDS_{future} = TDS_{current}$. Any ML model must prove it can beat this naive assumption to be considered useful.

### 2.4 Model Comparison
Evaluated on the 15% hold-out test set:
* **Persistence Baseline:** R² = 0.941
* **Linear Regression:** R² = 0.888, RMSE = 15.90 ppm
* **Random Forest:** R² = 0.742, RMSE = 24.14 ppm
* **XGBoost:** R² = 0.711, RMSE = 25.55 ppm
* **Conclusion:** The Persistence Baseline and Linear Regression dominated. Because pond TDS changes incrementally in a 60-minute window, complex non-linear boosting (XGBoost) overcomplicated the task and found false patterns. 

---

## Section 3: Model 3 — Pond Water-Quality Anomaly Detection

### 3.1 Overview & Data
* **Purpose:** Detect unusual combinations of sensor readings (pH, Temp, TDS) that indicate abnormal pond conditions, without relying on manually labeled data.
* **Dataset:** Aquaponic Fish Pond IoT Dataset.

### 3.2 Step-by-Step Methodology
1. **Delta Feature Engineering:** Alongside absolute values (e.g., pH 7.5), we calculated rate-of-change "deltas" (e.g., pH shifted +0.5 in one hour).
2. **Statistical Baseline:** Calculated Z-scores for all features. Any row containing a Z-score $>3$ was flagged as anomalous (detected 55 anomalies).
3. **Isolation Forest Training:** Trained an Isolation Forest with a 5% contamination factor (assuming 5% of the data represents unhealthy conditions).
4. **Scoring:** The model outputs a raw anomaly score for every hour, converting the lowest 5% of scores into a boolean `ANOMALY DETECTED` flag.

### 3.3 Techniques Chosen & Rationale
* **Why Unsupervised Learning?** Real-world aquaculture datasets rarely come with perfect labels of "fish died at this exact hour." Supervised learning was impossible. Unsupervised learning allows the AI to learn what a "healthy" baseline looks like and flag deviations.
* **Why Isolation Forest over Z-Scores?** Z-scores only catch **univariate** anomalies (one sensor going crazy). Isolation Forest catches **multivariate** anomalies. For example, a pH of 8.0 is safe. A temperature of 32°C is safe. But a pH of 8.0 *combined* with 32°C temperature causes deadly toxic ammonia spikes. Isolation forest detects this dangerous combination even if neither value breaks the Z-score limit individually.
* **Why Delta Features?** A slow rise to high TDS is manageable via acclimation. A sudden spike in TDS implies contamination (e.g., fertilizer runoff). Delta features teach the model to fear sudden shocks.

---

## Section 4: Technical Defense Preparation

If your board includes technical Machine Learning professors, they will likely ask these questions. Study the answers carefully.

### 4.1 Anticipated Technical Questions & Answers

**Q1: "Explain LOYO (Leave-One-Year-Out) Cross-Validation and why you didn't use standard K-Fold."**
> *Answer:* Standard K-Fold randomly shuffles data. If we shuffle time-series data, a data point from December could be in the training set, while November is in the test set. The model would "look into the future," causing data leakage. LOYO trains on block years (e.g., 2010-2020) and tests on a strictly unseen future year (e.g., 2021). It is the only rigorous way to validate hydrological models.

**Q2: "In Model 2, why did your baseline and Linear Regression beat XGBoost? Isn't XGBoost a better algorithm?"**
> *Answer:* XGBoost is better for complex, non-linear tabular data. However, over a short 60-minute window, pond TDS exhibits strong linear autocorrelation (it changes very slowly). Tree-based models excel at interpolation but fail at extrapolation. Linear Regression perfectly modeled the slow, linear drift of the water quality, while XGBoost overfit to noise. 

**Q3: "How does the Isolation Forest algorithm actually work in Model 3?"**
> *Answer:* Isolation Forest works by building random decision trees to separate data points. It assumes that anomalies are "few and different." Because anomalies are outliers, it takes very few random splits in the tree to isolate them into their own leaf node. Normal data points are clustered closely together, requiring many splits to isolate. Therefore, data points with a short average path length across the trees are flagged as anomalies.

**Q4: "What is SHAP and why did you use it?"**
> *Answer:* SHAP (SHapley Additive exPlanations) is based on game theory. It calculates exactly how much each feature (like $TDS_{t-1}$ or $pH$) contributed to the final prediction. We used it to break the "black box" of our ML models, proving to stakeholders (farmers) exactly *why* the model is issuing a warning.

**Q5: "In Model 3, does an 'Anomaly' mean the fish are dead?"**
> *Answer:* No. The model explicitly avoids making a medical/biological claim. An anomaly simply means "The current multivariate sensor pattern differs substantially from the patterns considered normal by historical standards." It acts as an early-warning decision-support signal for the farmer to manually inspect the pond.

### 4.2 Key Topics to Study Before Defense
1. **Time-Series Extrapolation vs Interpolation:** Understand why Random Forests cannot predict a value higher than the maximum value in their training set.
2. **Metrics Definition:** Be ready to define MAE (Mean Absolute Error - average error in physical units) vs RMSE (Root Mean Squared Error - heavily penalizes large errors/outliers) vs R² (variance explained).
3. **Multivariate Outliers:** Understand the concept of data points that are normal on the X-axis, normal on the Y-axis, but anomalous in X-Y space. (Crucial for defending Model 3).
