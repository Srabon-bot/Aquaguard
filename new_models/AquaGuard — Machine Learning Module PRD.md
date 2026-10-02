## AquaGuard — Machine Learning Module

## Product Requirements Document (PRD)

Project: AquaGuard — Bangladesh Flood Early Warning and IoT Pond Management System

Document Type: Machine Learning Module PRD

Primary Users: Aquaculture farmers / pond operators

Implementation Level: Undergraduate / beginner-friendly ML project

Target: A practical, explainable ML system integrated with the existing AquaGuard IoT dashboard

## 1. Project Overview

AquaGuard is an IoT-based pond-management and flood-awareness system for aquaculture environments in Bangladesh.

The existing system contains:

- ESP32-based pond monitoring

- pH sensing

- TDS/water-quality sensing

- temperature sensing

- water-level sensing

- Firebase data storage

- pump and valve control

- web dashboard

- flood-related functionality

The ML module will be redesigned around three practical models:

## Model 1 — River Water-Level Forecasting

Predict river water level for a future time period, primarily 24 hours ahead.

## Model 2 — Pond TDS Forecasting

Predict the future TDS level of the pond using historical TDS, pH, temperature and time-series features.

## Model 3 — Pond Water-Quality Anomaly Detection

Detect unusual combinations of pond sensor readings that may indicate abnormal water conditions.

The three models serve different purposes and should not be combined into one opaque prediction.


## 2. System Objectives

The ML subsystem should:

- 1. Provide a practical flood-related prediction.

- 2. Predict future pond water-quality conditions.

- 3. Detect unusual pond conditions.

- 4. Use publicly available datasets for initial model development.

- 5. Allow later adaptation using AquaGuard's own sensor data.

- 6. Use beginner-friendly ML algorithms.

- 7. Avoid unnecessary deep-learning complexity.

- 8. Use time-aware validation for time-series models.

- 9. Provide explainable outputs.

- 10. Integrate with the existing AquaGuard dashboard and Firebase architecture.

## 3. Overall ML Architecture


## 4. MODEL 1 — River Water-Level Forecasting

## 4.1 Purpose

Predict the future water level of a selected Bangladesh river station.

## Primary prediction target

## River water level +24 hours

Optional later extensions:

- +48 hours

- +72 hours

The model should initially focus on one forecast horizon to keep the implementation reliable.

## 4.2 Why this model was selected

River water level is a continuous and measurable quantity, making it a cleaner ML target than directly predicting a vague "flood/no flood" label.

The Flood Forecasting & Warning Centre (FFWC) provides observed water-level information and station danger levels through its official system.

Recent Bangladesh research also directly supports ML-based river-water-level forecasting. A 2025 study compared nine ML models using 34 years of data from three Old Brahmaputra stations and reported strong results from Random Forest Regression.

Another 2025 study compared Random Forest, XGBoost, LightGBM, Linear Regression, Polynomial Regression and MLP for Bangladesh's Old Brahmaputra River and found Random Forest particularly effective for monthly extreme water levels.

## 4.3 Proposed model

## Primary model

Random Forest Regressor


## Comparison models

For experimentation:

- Linear Regression

- Random Forest Regressor

- XGBoost Regressor

The final deployed model will be selected based on validation/test performance rather than predetermined preference.

## 4.4 Input features

Possible features:

## Historical river level

```
water_level_t-1
water_level_t-2
water_level_t-3
water_level_t-6
water_level_t-12
water_level_t-24
```

## Water-level trend

```
level_change_6h
level_change_12h
level_change_24h
```

## Rainfall

```
rainfall_24h
rainfall_3day
rainfall_7day
```

## Time features

```
month
day_of_year
```


```
sin_day
cos_day
```

If reliable rainfall data cannot be matched to the chosen station, the first version can use water-level history and seasonal features only.

## 4.5 Target

```
target = river_water_level(t + 24 hours)
```

## 4.6 Flood-warning layer

The ML model predicts the water level.

A separate rule-based layer compares the prediction with the station's documented danger level.

Example:

```
Predicted water level = 19.72 m
Danger level = 19.50 m
→ Predicted exceedance
→ Flood warning
```

This separation is important.

## ML = prediction

## Hydrological threshold = warning interpretation

The system should not claim that the ML model itself discovered the official danger threshold.

## 4.7 Candidate datasets

## Dataset A — FFWC/BWDB observations

Official source:

[FFWC Observed Water Level System](https://ffwc.gov.bd/app/observed-water-level?utm_source=chatgpt.com)


The FFWC system provides station information, observed water levels, danger levels and historical water-

level charts.

## Priority: High

Use: Preferred source for a Bangladesh-specific implementation.

## Dataset B — Bangladesh river water-level research

A 2025 study used 1990–2024 water-level data from Old Brahmaputra stations and evaluated multiple ML approaches. The underlying research data are not publicly downloadable from the paper, so it should be

treated as a research/reference source, not assumed to be a directly downloadable training dataset.

[Research paper — Comparative evaluation of ML models for Bangladesh river water levels](https://www.sciencedirect.com/science/article/pii/S2590061725000468?utm_source=chatgpt.com)

## Dataset C — Haor flash-flood events

A newer Bangladesh-specific dataset contains 77 SAR-verified flood/non-flood events from 2014–2024 for

the Sunamganj/Sylhet haor region.

Features include:

- Sentinel-1 VV/VH

- Sentinel-2 NDWI

- antecedent rainfall

- soil moisture

- temperature

- wind speed

- upstream river information

The dataset is available under CC BY 4.0.

[Haor Flash-Flood Dataset — Mendeley Data](https://data.mendeley.com/datasets/d72ny7rftc/1?utm_source=chatgpt.com)

Priority: Secondary / optional

Reason: Only 77 events, so it is much less suitable for a beginner's primary model than a long river-level time series.


## 4.8 Evaluation

Use:

- MAE

- RMSE

- R²

- NSE if implemented

Do not randomly shuffle the entire time series.

Recommended split:

```
Earlier historical period → Training
Later historical period → Validation
Most recent period → Test
```

The model should never receive future observations during training.

## 4.9 Dashboard output

Example:

RIVER FLOOD FORECAST

Station:

Bahadurabad

Current Level:

18.20 m

Predicted +24h:

19.12 m

Danger Level:

19.50 m

Forecast:

Approaching danger level

A graph should show:


```
Historical water level
+
Predicted future level
+
Danger-level reference line
```

## 5. MODEL 2 — Pond TDS Forecasting

## 5.1 Purpose

Predict the future TDS of the AquaGuard pond.

## Primary target

## TDS +60 minutes

If the final sensor sampling interval makes 60 minutes inconvenient, the target can be changed to the next valid measurement horizon.

## Optional:

- +30 minutes

- +60 minutes

## 5.2 Why TDS forecasting

TDS is already one of the parameters measured by the AquaGuard hardware.

The project report confirms that the TDS sensor has been tested and produces a monotonic response from dry air to tap water to salted water.

Therefore, TDS forecasting provides a direct connection between:

```
ML
+
ESP32
+
Firebase
+
Real sensor data
```


## 5.3 Proposed model

## Primary

## XGBoost Regressor

## Comparison

- Linear Regression

- Random Forest Regressor

- XGBoost Regressor

The final model should be chosen using chronological validation.

## 5.4 Features

## TDS history

```
TDS_t-1
TDS_t-2
TDS_t-3
TDS_t-6
TDS_t-12
```

## pH history

```
pH_t-1
pH_t-2
pH_t-3
```

## Temperature history

```
temperature_t-1
temperature_t-2
temperature_t-3
```


## Rolling statistics

```
TDS_rolling_mean
TDS_rolling_std
pH_rolling_mean
temperature_rolling_mean
```

## Time

hour

day_of_week

## 5.5 Target

```
target = TDS(t + 60 minutes)
```

## 5.6 Primary dataset

## Aquaponic Fish Pond IoT Dataset

The dataset contains:

- pH

- TDS

- water temperature

- timestamps

It contains approximately 118,286 rows and measurements collected over three months in 2023. The data were collected using pH-4502C, DFROBOT TDS and DS18B20 temperature sensors.

[Mendeley — Aquaponic Fish Pond IoT Dataset](https://data.mendeley.com/datasets/yd36bx6f8f?utm_source=chatgpt.com)

[Research paper describing the dataset](https://pmc.ncbi.nlm.nih.gov/articles/PMC10293995/?utm_source=chatgpt.com)

## Priority: Very High

This is especially suitable because the sensor types are close to AquaGuard's actual sensors.


## 5.7 Bangladesh aquaculture research dataset

A separate dataset was collected from five fish ponds in Jamalpur, Bangladesh.

It contains:

- pH

- temperature

- turbidity

- fish category

with 40,280 rows. The study evaluated ten ML algorithms and reported Random Forest as the strongest model in its particular experiment.

[Jamalpur Pond Dataset — Mendeley/Research Article](https://pmc.ncbi.nlm.nih.gov/articles/PMC10700555/?utm_source=chatgpt.com)

## Priority: Secondary

It is valuable for Bangladesh-specific context, but it does not contain TDS, so it should not be the primary dataset for the TDS-forecasting model.

## 5.8 Bangladesh shrimp-farm research

A 2024 Bangladesh study developed an IoT monitoring and ML system for freshwater shrimp farms in Satkhira.

The system monitored:

- pH

- temperature

- TDS

- EC

- salinity

and used historical measurements to predict next-day water-quality values. The testing dataset covered approximately 90 days and contained 3,240 observations.

[Bangladesh Smart Aquaculture Analytics Research](https://doi.org/10.1016/j.heliyon.2024.e37330?utm_source=chatgpt.com)

Priority: High as a research reference.

This is particularly useful for justifying the idea of forecasting water-quality parameters in a Bangladesh aquaculture context.


## 5.9 Evaluation

Use:

- MAE

- RMSE

- R²

## Optional:

- MAPE, only if the target values do not approach zero.

The evaluation must use chronological splitting.

## 5.10 Explainability

## Use SHAP.

## Example output:

```
Feature importance
TDS(t-1)
TDS rolling mean
TDS(t-2)
pH(t-1)
Temperature(t-1)
```

This makes the model easier to explain during the project defense.

## 5.11 Dashboard output

```
AI WATER QUALITY FORECAST
Current TDS:
285 ppm
Predicted TDS +60 min:
342 ppm
Trend:
```


Increasing

Model:

XGBoost

Confidence:

[calibrated/validated output if implemented]

The system should avoid presenting a medical/scientific certainty claim. The prediction is a decision-support signal.

## 6. MODEL 3 — Pond Water-Quality Anomaly Detection

## 6.1 Purpose

Detect unusual combinations of sensor readings without requiring a manually labelled "bad water" dataset.

The model answers:

"Does the current combination of pond measurements look unusual compared with normal historical conditions?"

## 6.2 Proposed algorithm

## Isolation Forest

This is suitable for a beginner project because it is:

- available in scikit-learn

- relatively simple

- unsupervised

- does not require manually labelled anomalies

- easy to integrate into a real-time monitoring system


## 6.3 Input features

pH

TDS

Temperature

Water level

Optional derived features:

TDS change

pH change

Temperature change

Water-level change

## 6.4 Output

The model produces an anomaly score.

Dashboard converts it into:

NORMAL

or

ANOMALY DETECTED

The exact wording should emphasize that an anomaly is not automatically proof of unsafe water.

## 6.5 Dataset strategy

Unlike supervised classification, this model does not need a perfect labelled "bad pond" dataset.

Recommended approach:

## Stage 1

Train the model on the normal/clean portion of a public water-quality dataset.


## Stage 2

Test it using:

- naturally unusual observations

- held-out observations

- carefully constructed synthetic perturbations for software testing

## Stage 3

After AquaGuard collects sufficient real sensor data, retrain/adapt the anomaly detector using the project's own Firebase history.

## 6.6 Candidate dataset

The aquaponic IoT dataset is particularly useful because it contains continuous:

- pH

- TDS

- temperature

measurements.

[Aquaponic Fish Pond IoT Dataset](https://data.mendeley.com/datasets/yd36bx6f8f?utm_source=chatgpt.com)

The Jamalpur Bangladesh pond dataset can provide additional Bangladesh-specific water-quality context, although it uses turbidity rather than TDS.

[Jamalpur Bangladesh Pond Dataset](https://pmc.ncbi.nlm.nih.gov/articles/PMC10700555/?utm_source=chatgpt.com)

## 6.7 Important limitation

The anomaly detector should not claim:

ANOMALY = DISEASE

or:

ANOMALY = FISH DEATH

It only means:


The current sensor pattern differs substantially from the patterns considered normal by the model.

The dashboard can then recommend checking the pond conditions.

## 7. Optional Future Computer-Vision Module

This is not required for the core three-model implementation, but it is a possible future extension.

## Fish Disease Classification

A new Bangladesh-specific dataset called MatsyaDx-BD contains 2,137 images from freshwater aquaculture farms in Rajshahi Division.

It contains four classes:

- Healthy Fish

- Bacterial Gill Disease

- Bacterial Red Disease

- Epizootic Ulcerative Syndrome (EUS)

The dataset is released under CC BY 4.0.

[MatsyaDx-BD — Mendeley Data](https://data.mendeley.com/datasets/sxkynv9t7n/2?utm_source=chatgpt.com)

Possible model:

```
Fish image
↓
EfficientNetB0
↓
Disease classification
↓
Healthy / Disease class
```

This should be treated as a future extension, not a required part of the first working version.

## 8. Model Comparison and Experiment Plan

Each model should have a baseline.


## Flood model

```
Baseline:
Persistence
(current level = future level)
vs
Linear Regression
vs
Random Forest
vs
XGBoost
```

## TDS model

```
Baseline:
Persistence
(current TDS = future TDS)
vs
Linear Regression
vs
Random Forest
vs
XGBoost
```

## Anomaly model

```
Isolation Forest
vs
Simple statistical threshold baseline
```

The project should report actual measured results rather than selecting a model based only on reputation.


## 9. Validation Requirements

## Time-series models

Both the river-level and TDS models must use chronological validation.

Example:

TRAIN

70%

Past ───────────────────────────────────────────────→ Future

No random shuffling across the complete time series.

VALIDATION

TEST

15%

15%

## 10. Required Metrics

## Regression

## MAE

Mean Absolute Error.

Easy to explain:

On average, how far was the prediction from the actual value?

## RMSE

Penalizes larger errors more strongly.

R²

Measures how much variation in the target is explained by the model.

## NSE

Optional for river forecasting because it is common in hydrological modelling.


## 11. Model Explainability

The project should include SHAP explanations for the two supervised tree models.

For example:

```
River model
Previous water level
24h rainfall
7-day rainfall
Season
```

and:

This provides an interpretable explanation for the model's prediction.

## 12. Backend Architecture

Each model should be wrapped in a FastAPI endpoint.


```
FastAPI
│
├── /predict/flood
│
├── /predict/tds
│
└── /predict/anomaly
```

Example:

```
POST /predict/flood
```

Input:

```
{
"station": "Station_A",
"water_level": 18.2,
"rainfall_24h": 42.5,
"water_level_lag_1": 18.0
}
```

## Output:

```
{
"predicted_water_level_24h": 19.12,
"danger_level": 19.50,
"warning": "Approaching danger level"
}
```

## 13. Firebase Integration

Existing AquaGuard architecture already uses Firebase Realtime Database for sensor and pond information.

The new ML system should use:

```
ESP32
↓
Firebase
↓
```


```
FastAPI
↓
ML model
↓
Firebase / Dashboard
```

## Possible structure:

```
/ml_predictions
/flood
/tds
/anomaly
```

## 14. Dashboard Requirements

The dashboard should contain three ML cards.

## Flood Forecast

```
│ RIVER FLOOD FORECAST │
│ │
│ Station: Bahadurabad │
│ Current: 18.20 m │
│ +24h: 19.12 m │
│ Danger: 19.50 m │
│ │
│ Status: APPROACHING DANGER │
```

## Water Quality Forecast

```
│ AI WATER QUALITY FORECAST │
│ │
│ TDS now: 285 ppm │
│ TDS +60 min: 342 ppm │
│ │
│ Trend: INCREASING │
```


## Anomaly Detection

```
│ POND CONDITION │
│ │
│ Status: NORMAL │
│ Anomaly score: -0.12 │
│ │
│ No unusual sensor pattern │
```

## 15. Relationship Between the Three Models

The models should remain separate because they answer different questions.

## Model 1

Will the river level rise?

↓

External flood risk

## Model 2

Will pond TDS rise?

↓

Future water-quality condition

## Model 3

Is the current pond condition unusual?

↓

Immediate anomaly detection

Together:


```
External environment
↓
Flood Model
↓
Flood risk to pond
│
│ AQUAGUARD │
│ POND │
│
├── TDS Forecast
│
└── Anomaly Detection
```

## 16. Development Phases

## Phase 1 — Dataset preparation

- Download datasets.

- Inspect columns.

- Clean timestamps.

- Handle missing values.

- Remove impossible sensor readings.

- Create lag features.

- Create rolling features.

- Create target variables.

## Phase 2 — Baseline models

## Implement:

- Persistence baseline

- Linear Regression

## Phase 3 — Main ML models

## Implement:

- Random Forest

- XGBoost


## Phase 4 — Evaluation

## Generate:

- MAE

- RMSE

- R²

- NSE where appropriate

- prediction-vs-actual graphs

- residual plots

## Phase 5 — Explainability

## Add:

- SHAP feature importance

- SHAP summary plots

## Phase 6 — Anomaly detection

## Implement:

- Isolation Forest

- anomaly scoring

- dashboard status

## Phase 7 — API

Create FastAPI services.

## Phase 8 — Firebase

Connect predictions to Firebase.

## Phase 9 — Dashboard

## Add:

- flood forecast

- TDS forecast

- anomaly status

- historical prediction charts


## Phase 10 — Real-device testing

Replace/augment public data with actual AquaGuard sensor data.

## 17. Dataset Priority

| Model | Primary Dataset | Secondary Dataset | Priority |
| --- | --- | --- | --- |
| River Forecast | FFWC/BWDB observations | Haor flood dataset | High |
| TDS Forecast | Aquaponic IoT pH/TDS/temp | Bangladesh shrimp-farm study | Very |
|   | dataset |   | High |
| Anomaly | Aquaponic IoT dataset | Jamalpur Bangladesh pond | High |
| Detection |   | dataset |   |

## 18. Dataset Links

## Flood

[FFWC Observed Water Levels](https://ffwc.gov.bd/app/observed-water-level?utm_source=chatgpt.com)

[Haor Flash-Flood Event Dataset — Mendeley Data](https://data.mendeley.com/datasets/d72ny7rftc/1?utm_source=chatgpt.com)

[Bangladesh River Water-Level ML Research — ScienceDirect](https://www.sciencedirect.com/science/article/pii/S2590061725000468?utm_source=chatgpt.com)

## Water Quality

[Aquaponic Fish Pond IoT Dataset — Mendeley Data](https://data.mendeley.com/datasets/yd36bx6f8f?utm_source=chatgpt.com)

[Aquaponic Dataset Research Paper — PMC](https://pmc.ncbi.nlm.nih.gov/articles/PMC10293995/?utm_source=chatgpt.com)

[Jamalpur Bangladesh Pond Dataset — PMC](https://pmc.ncbi.nlm.nih.gov/articles/PMC10700555/?utm_source=chatgpt.com)

[Bangladesh Shrimp-Farm ML Research](https://doi.org/10.1016/j.heliyon.2024.e37330?utm_source=chatgpt.com)

## Optional Computer Vision

[MatsyaDx-BD Fish Disease Dataset](https://data.mendeley.com/datasets/sxkynv9t7n/2?utm_source=chatgpt.com)


## 19. Success Criteria

The ML module will be considered successfully implemented when:

## Flood model

- [ ] Public/official river dataset successfully obtained.

- [ ] Time-series preprocessing completed.

- [ ] Persistence baseline implemented.

- [ ] At least two ML models compared.

- [ ] Test MAE/RMSE/R² reported.

- [ ] +24h water-level prediction working.

- [ ] Danger-level comparison implemented.

- [ ] Prediction visible in dashboard.

## TDS model

- [ ] Public pH/TDS/temperature dataset downloaded.

- [ ] Lag features created.

- [ ] Persistence baseline implemented.

- [ ] At least two ML models compared.

- [ ] MAE/RMSE/R² reported.

- [ ] Future TDS prediction working.

- [ ] SHAP explanation generated.

- [ ] API endpoint working.

- [ ] Dashboard integration completed.

## Anomaly model

- [ ] Normal training data prepared.

- [ ] Isolation Forest trained.

- [ ] Anomaly score generated.

- [ ] Normal/anomaly status displayed.

- [ ] False-alert behavior tested.

- [ ] Dashboard integration completed.

## 20. Academic Deliverables

The final project should contain:

- 1. Dataset description

- 2. Data preprocessing methodology

- 3. Feature-engineering methodology

- 4. Baseline methodology

- 5. Model architecture


- 6. Training procedure

- 7. Validation methodology

- 8. Evaluation metrics

- 9. Model comparison

- 10. SHAP explainability

- 11. Error analysis

- 12. API implementation

- 13. Firebase integration

- 14. Dashboard implementation

- 15. Real sensor demonstration

- 16. Limitations

- 17. Future work

## 21. Important Limitations to Report

The project should explicitly state:

## Flood model

- River observations and danger levels vary by station.

- Forecast accuracy depends on historical data quality.

- A water-level forecast is not equivalent to a complete physical flood simulation.

- Coastal/tidal effects may reduce performance at some stations.

- The model should not be presented as an official government warning system.

## TDS model

- Public training data may come from a different pond/environment.

- Sensor characteristics and calibration may differ.

- TDS alone does not describe complete water quality.

- The prediction is a decision-support signal rather than a guarantee.

## Anomaly model

- Anomaly does not automatically mean unsafe water.

- Anomaly detection depends strongly on what the model considers "normal."

- More AquaGuard-specific data should improve future adaptation.

## 22. Recommended Final ML Stack

Python

│

├── pandas


├── numpy

├── scikit-learn

├── XGBoost

├── SHAP

├── matplotlib

│

├── FastAPI

├── joblib

│

└── Firebase

No deep-learning framework is required for the three core models.

## 23. Final Product Concept

The final AquaGuard system should communicate three simple ideas:

## Flood Model:

"The river is expected to reach this level."

## TDS Model:

"The pond's TDS is expected to reach this level."

## Anomaly Model:

"The pond's current sensor pattern is unusual."

This gives the project a clear end-to-end ML + IoT purpose without relying on unnecessarily complicated models.
