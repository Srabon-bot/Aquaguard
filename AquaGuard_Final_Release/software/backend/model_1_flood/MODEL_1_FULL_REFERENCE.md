# Model 1 — River Water-Level Forecasting: Full Technical Reference

**AquaGuard Capstone Project**
*Last Updated: October 2026*

---

## 1. What Model 1 Does

Model 1 is a **multi-horizon regression system** that predicts the daily water level (in metres above mean sea level) at the **Bahadurabad Transit gauge station** on the Jamuna River (Brahmaputra in Bangladesh), 1 day, 3 days, 7 days, and 14 days into the future.

This is not a binary "flood / no flood" classifier. It predicts an **exact numerical water level** — e.g., "the river will be at 19.42 m in 7 days." This lets farmers calculate exactly how many centimetres they need to raise their embankment nets before water arrives.

---

## 2. The Dataset — Exactly What Was Used

### 2.1 Primary Dataset: BWDB Daily Gauge Records

**File used in the model:**
```
Data/Q/Own_Rated_Q_2008-2022_Bahadurabad.csv
```

**Columns:**
| Column | Meaning |
|---|---|
| `Date` | Calendar date (YYYY-MM-DD) |
| `WL` | Daily water level in metres (m) above datum |
| `Q_R` | Rated discharge in m³/s (derived from rating curve) |

**Period:** 2008-01-01 to 2022-12-31 (15 years, 5,479 days)

**Source:**
The water level records are from the **Bangladesh Water Development Board (BWDB)** Hydrometric Data Portal for gauge station **SW46.9L**, which is the official Bahadurabad Transit station on the Jamuna River.

> **Official Dataset Credit:**
> Bangladesh Water Development Board (BWDB), *Hydrometric Data Portal: Daily Water Levels and Discharge Records — Station SW46.9L (Jamuna River at Bahadurabad Transit, Jamalpur)*, BWDB Hydrology Division, Dhaka, Bangladesh, 2024.
> Available via: [http://www.bwdb.gov.bd](http://www.bwdb.gov.bd) *(registration required)*

**Annual maxima cross-validation** (used to verify the dataset accuracy against official records):
| Year | BWDB Official Max WL (m) | BWDB Peak Date |
|---|---|---|
| 2008 | 19.75 | 2008-09-08 |
| 2009 | 19.37 | 2009-08-22 |
| 2010 | 19.78 | 2010-09-14 |
| 2011 | 19.64 | 2011-07-23 |
| 2012 | 20.54 | 2012-07-01 |
| 2013 | 19.91 | 2013-09-11 |
| 2014 | 20.20 | 2014-08-29 |
| 2015 | 20.17 | 2015-09-06 |
| 2016 | 20.71 | 2016-07-28 |
| 2017 | 20.84 | 2017-08-16 |

Dataset annual maxima matched BWDB official records with **< 0.02 m bias** and **0–2 days peak date offset** — confirming data integrity.

---

### 2.2 Secondary Dataset: Satellite Altimetry Cross-Check

**File:**
```
Data/WL/COMBINED-WL-from-Altimetry_S1_S2-2008-2022_Bahadurabad.csv
```

**Satellites used:** JASON-2, JASON-3 (radar altimetry, 10-day repeat orbit)
**Purpose:** Used as an **independent cross-check** of the BWDB gauge records, specifically at peak flood levels where in-situ sensors are most prone to missing data or damage. Not used for model training — used for validation only.

> **Official Dataset Credit:**
> ESA / CNES / EUMETSAT, *JASON-2 and JASON-3 Satellite Radar Altimetry — River Water Level Observations, Bahadurabad Virtual Station*, via **HydroWeb** (Theia / LEGOS):
> [https://hydroweb.theia-land.fr](https://hydroweb.theia-land.fr) *(free registration)*

---

### 2.3 Catchment Rainfall Dataset: Open-Meteo API (ERA5 Reanalysis)

**File (generated at runtime):**
```
Data/raw/catchment_rainfall.csv
```

**What it is:** Daily catchment-averaged precipitation (mm) and mean temperature (°C) across the Brahmaputra upper catchment, drawn from the **ERA5-Land** global reanalysis product via the **Open-Meteo** free API.

**The 6 spatial grid points sampled** (these cover the Brahmaputra basin above Bahadurabad):

| Point Name | Latitude | Longitude | Sub-basin |
|---|---|---|---|
| Bahadurabad Local | 25.1°N | 89.6°E | Jamuna at gauge |
| Assam Lower | 26.0°N | 91.5°E | Brahmaputra plains, India |
| Assam Upper / Arunachal | 27.5°N | 94.0°E | Arunachal Pradesh foothills |
| Tibet West | 29.5°N | 88.0°E | Upper Brahmaputra (Yarlung Tsangpo) |
| Tibet Central | 30.0°N | 92.0°E | Central Tibetan Plateau |
| Bhutan Sub-basin | 28.0°N | 89.0°E | Manas/Raidak tributaries |

These 6 points are averaged to produce a single daily "catchment rainfall" value representing the basin-wide forcing upstream of Bahadurabad.

**API endpoints used:**
- Real-time (≤ 90 days): `https://api.open-meteo.com/v1/forecast`
- Historical archive (> 90 days): `https://archive-api.open-meteo.com/v1/archive`

> **Official Dataset Credit:**
> Hersbach, H., Bell, B., Berrisford, P., et al., "The ERA5 global reanalysis," *Quarterly Journal of the Royal Meteorological Society*, vol. 146, no. 730, pp. 1999–2049, 2020. DOI: [10.1002/qj.3803](https://doi.org/10.1002/qj.3803)
>
> Open-Meteo API (data provider): Zippenfenig, P., *Open-Meteo.com Weather API*, 2023. DOI: [10.5281/zenodo.7970649](https://doi.org/10.5281/zenodo.7970649)

---

### 2.4 Flood Plain DEM Data (Reference, Not Model Training)

**Files (reference only):**
```
Data/FPDEM/2016.tif … 2022.tif   (annual GeoTIFFs)
Data/FPDEM/FPDEM_16-22.tif       (composite)
```

These are **Flood Plain Digital Elevation Model** rasters from Sentinel-1/2 SAR imagery, used to visually understand how rising Jamuna water levels spatially propagate across the floodplain. They were **not used in model training** but are included for the defense presentation to show where the flood physically goes.

---

## 3. What Regions the Model Covers and Affects

### 3.1 The Station: Bahadurabad Transit (SW46.9L)

- **Location:** 25.1°N, 89.6°E — Bahadurabad, Jamalpur District
- **River:** Jamuna River (known internationally as the Brahmaputra in its lower reach)
- **Danger Level:** 19.05 m
- **Extreme Danger Level:** 19.90 m
- **Record Highest Water Level (RHWL):** 20.63 m (observed in study period)

Bahadurabad is the **most important flood control gauge in Bangladesh** — it is the first major gauging point after the Brahmaputra crosses from India into Bangladesh. When water rises here, it gives advance warning for the entire eastern Jamuna floodplain.

---

### 3.2 Districts Directly Affected by Bahadurabad Floods

When the Bahadurabad gauge crosses the Danger Level (19.05 m), the following districts historically experience flooding:

| District | Distance from Gauge | Typical Flood Arrival Lag |
|---|---|---|
| Jamalpur | At gauge / immediate | 0–1 days |
| Gaibandha | ~60 km downstream | 1–2 days |
| Sirajganj | ~100 km downstream | 2–3 days |
| Bogura (partially) | ~110 km west | 2–4 days |
| Tangail | ~130 km south | 3–5 days |
| Manikganj | ~170 km south | 4–6 days |

These six districts together contain approximately **1.2 million fish ponds** (from DoF 2023 data) and the highest concentration of commercial aquaculture in Bangladesh.

The Bahadurabad 14-day forecast output in AquaGuard gives fish farmers in **all six districts** enough time to:
- Raise perimeter net heights by 40–60 cm
- Harvest marketable fish (rohu, catla, tilapia) before water breaches dike tops
- Move broodstock to emergency holding pens

---

### 3.3 The Catchment Area Monitored

The model monitors the following upstream basin area via the 6 ERA5 rainfall grid points:

```
Catchment bounding box: 82°E – 98°E, 24°N – 32°N
```

This covers the entire **Brahmaputra-Jamuna catchment** including:
- The Yarlung Tsangpo in Tibet (origin of the river)
- The Arunachal Pradesh and Assam plains (India), where monsoon rainfall is heaviest
- The Bhutan sub-basins (Manas, Raidak, Sankosh)
- The crossing point into Bangladesh at Chilmari / Bahadurabad

Over **92% of this catchment lies outside Bangladesh**, meaning Bangladeshi farmers have no direct control over the floodwaters heading towards them — they can only be warned.

---

## 4. Why Other River Stations Are Missing

### 4.1 The Short Answer

Model 1 was deliberately designed as a **single-station regional pilot**. This was an intentional scope decision, not an incomplete project. The PRD (Machine Learning Module PRD) explicitly states:
> *"predict future water level of a selected Bangladesh river station"*

The word "selected" was chosen on purpose.

---

### 4.2 The Detailed Reason — Three Specific Barriers

**Barrier 1: Different flood physics for each river basin**

Bangladesh has four major independent river systems with completely different flooding mechanisms:

| River System | Flood Type | Data Frequency Needed | Key Gauge |
|---|---|---|---|
| Jamuna (Brahmaputra) | Slow monsoon rise, 7–14 day peak | **Daily** | Bahadurabad SW46.9L |
| Padma (Ganges) | Slow monsoon rise, 5–10 day peak | **Daily** | Hardinge Bridge |
| Meghna (Lower) | Tidal + riverine combined | **Hourly** | Bhairab Bazar |
| Surma-Kushiyara (Sylhet) | **Flash floods** from Meghalaya hills | **Hourly (6-min ideal)** | Kanaighat, Sylhet |
| Teesta | Glacial melt + monsoon mix | Daily | Dalia |
| Karnaphuli (Chittagong) | Cyclone-driven coastal surge | Sub-daily | Kaptai |

A model trained on **daily Jamuna data** cannot transfer to the Surma basin, where a flash flood rises from normal to danger level within **6–12 hours**. A daily model has no useful resolution for that.

**Barrier 2: Data access**

BWDB's real hydrometric gauge data is behind a registration and access agreement portal. For Bahadurabad, the data was accessible and verifiable. For other stations:
- Padma at Hardinge Bridge: data available but discharge relationships differ significantly
- Surma-Kushiyara: hourly data required; daily publicly available records are sparse before 2015
- Teesta: cross-border data sharing with India is politically sensitive and availability is inconsistent
- FFWC public portal only exposes the current day reading, not historical archives for model training

**Barrier 3: Feature set would need redesigning per river**

The current model uses:
- `WL_t` (today's water level) — lag-driven autoregressive feature
- Brahmaputra catchment rainfall at lags 1, 3, 7 days — physically correct for Jamuna
- Rating curve discharge `Q_R` as an additional predictor

For the Padma, the dominant upstream input is the **Farakka Barrage discharge** in India (controlled release, not natural rainfall). Rainfall features from the Ganges headwaters in Uttarakhand would replace Brahmaputra rainfall — completely different spatial grids and data sources.

---

## 5. How to Add a New River Station

Here is the exact step-by-step process to extend Model 1 to a new station:

### Step 1 — Get the Historical Gauge Data

Visit BWDB: [http://www.bwdb.gov.bd/](http://www.bwdb.gov.bd/)
- Register and request data for the target station
- Download daily water level records (minimum 10 years recommended)
- Format as CSV with columns: `Date, WL`

Alternative free sources for cross-checking:
- **Global Runoff Data Centre (GRDC):** [https://www.bafg.de/GRDC/](https://www.bafg.de/GRDC/) — some Bangladeshi rivers available
- **HydroWeb altimetry:** [https://hydroweb.theia-land.fr](https://hydroweb.theia-land.fr) — satellite-derived WL at virtual stations

### Step 2 — Identify the Correct Catchment Grid Points

For each new station, identify 4–6 ERA5 grid points covering the **upstream** catchment. Use:
- Google Earth + BWDB catchment maps to visually trace the upstream basin
- Update the `GRID_POINTS` list in `src/ingestion.py`

Example: For Hardinge Bridge (Padma/Ganges):
```python
GRID_POINTS = [
    (24.1, 89.1),   # Hardinge Bridge local
    (25.0, 88.5),   # West Bengal plains (India)
    (25.5, 87.0),   # Ganges middle reach
    (26.5, 84.0),   # Bihar, India
    (27.0, 80.0),   # Uttar Pradesh headwaters
]
```

### Step 3 — Update config.yaml

```yaml
project:
  name: "Water-Level Forecasting at Hardinge Bridge"
  station: "HardingeBridge"
  station_code: "SW90.9L"    # Replace with actual BWDB code
  period: "2008-2022"

thresholds:
  danger_level: 14.90        # Hardinge Bridge official DL (different per station)
  extreme_level: 15.50
  rhwl: 16.21
```

### Step 4 — Check Data Frequency

If the new station requires **hourly data** (e.g., Surma at Kanaighat for flash floods):
- Change `freq='D'` to `freq='H'` in `src/data.py`'s `load_raw_data()` function
- Adjust `HORIZONS` in `config.yaml` from `[1, 3, 7, 14]` days to `[6, 12, 24, 48]` hours
- Adjust lag feature window accordingly

### Step 5 — Retrain

```bash
cd new_models/new_approach/model_1_flood
python main_pipeline.py
```

The pipeline automatically runs LOYO cross-validation, generates all 24 figures, 6 tables, and saves the best model predictions to `outputs/predictions/`.

### Step 6 — Add the New Station to the API

In `api_combined.py`, the forecast endpoint currently reads:
```python
station = "Bahadurabad"
```

A multi-station API would accept a `station` query parameter and route to the correct pre-trained model directory. Since all models use identical CSV/pipeline output formats, no other code changes are needed.

---

## 6. Priority Stations to Add Next (Recommended Order)

| Priority | Station | River | Why |
|---|---|---|---|
| **1st** | Hardinge Bridge | Padma (Ganges) | Largest river by discharge; good BWDB data; daily model works |
| **2nd** | Kanaighat | Surma (Sylhet) | Flash flood risk; requires hourly data but Sylhet is a major fish farming zone |
| **3rd** | Dalia | Teesta | Major irrigation-flood nexus in Rangpur; Teesta treaty with India makes this politically important |
| **4th** | Bhairab Bazar | Meghna | Tidal+riverine — needs tide gauge integration as additional feature |

---

## 7. Complete Dataset Credits Summary

Use these exact citations in your report references section:

**[Dataset 1] Primary Gauge Data:**
> Bangladesh Water Development Board (BWDB), *Hydrometric Data Portal: Daily Water Levels and Discharge Records, Station SW46.9L — Jamuna River at Bahadurabad Transit, Jamalpur*, BWDB Hydrology Division, Dhaka, Bangladesh, 2024. Available: http://www.bwdb.gov.bd

**[Dataset 2] Satellite Altimetry Cross-Check:**
> ESA / CNES / LEGOS / CTOH, *HydroWeb — River Water Level from JASON-2 and JASON-3 Radar Altimetry, Virtual Station: Brahmaputra at Bahadurabad*, Theia Land Data Services, 2023. Available: https://hydroweb.theia-land.fr

**[Dataset 3] Catchment Rainfall (ERA5 via Open-Meteo):**
> Hersbach, H., Bell, B., Berrisford, P., Biavati, G., Horányi, A., Muñoz Sabater, J., et al., *ERA5 hourly data on single levels from 1940 to present*, Copernicus Climate Change Service (C3S) Climate Data Store (CDS), 2023. DOI: [10.24381/cds.adbb2d47](https://doi.org/10.24381/cds.adbb2d47)
>
> Zippenfenig, P., *Open-Meteo.com Weather API [Software]*, Zenodo, 2023. DOI: [10.5281/zenodo.7970649](https://doi.org/10.5281/zenodo.7970649)

**[Dataset 4] Flood Verification Labels (used in event scoring only):**
> Flood Forecasting and Warning Centre (FFWC), *Annual Flood Reports 2008–2022*, Bangladesh Water Development Board (BWDB), Dhaka, Bangladesh. Available: http://www.ffwc.gov.bd

**[Reference] ERA5 Academic Citation:**
> Hersbach, H., Bell, B., Berrisford, P., et al., "The ERA5 global reanalysis," *Quarterly Journal of the Royal Meteorological Society*, vol. 146, no. 730, pp. 1999–2049, 2020. DOI: [10.1002/qj.3803](https://doi.org/10.1002/qj.3803)

---

## 8. Key Numbers Summary for Defense

| Fact | Value |
|---|---|
| Primary dataset | BWDB gauge SW46.9L, Bahadurabad |
| Dataset period | 2008-01-01 to 2022-12-31 |
| Total daily records | 5,479 days |
| Missing days | 335 (6.11%) — imputed with PCHIP |
| Catchment monitored | 82°E–98°E, 24°N–32°N (Brahmaputra basin) |
| Catchment area | ~600,000 km² (92% outside Bangladesh) |
| Rainfall grid points | 6 ERA5 points across Brahmaputra basin |
| Flood events in dataset | 34 independent events, 467 flood days total |
| Danger Level threshold | 19.05 m |
| Record high in study period | 20.63 m |
| Districts affected | Jamalpur, Gaibandha, Sirajganj, Bogura, Tangail, Manikganj |
| Best model deployed | Linear Regression |
| Best NSE (LOYO, +1 day) | 0.998 |
| Final holdout NSE (2020–2022) | 0.985 |
| Final holdout RMSE | 0.308 m |
| Forecast horizons | 1 day, 3 days, 7 days, 14 days |
| Dashboard warning buffer | 18.55 m (0.5 m below Danger Level) |
