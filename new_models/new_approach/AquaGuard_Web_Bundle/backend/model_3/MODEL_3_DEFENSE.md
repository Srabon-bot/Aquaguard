# Model 3: Pond Water-Quality Anomaly Detection

This folder contains the complete ML pipeline, models, and plots for **Model 3 (Pond Anomaly Detection)**, answering the PRD requirement to detect unusual combinations of sensor readings without needing a manually labelled "bad water" dataset.

## 1. Methodology

*   **Dataset:** Aquaponic Fish Pond IoT Dataset (2023) — containing pH, TDS, and Temperature.
*   **Target:** Unsupervised Anomaly Detection (No explicit labels).
*   **Features Engineeered:** 
    *   Absolute values: `pH`, `TDS`, `temperature`
    *   Deltas (Changes): `pH_change`, `TDS_change`, `temp_change` (Detects sudden spikes or drops, which are often more dangerous than slowly reaching a high absolute value).

## 2. Model Comparison

We evaluated two approaches for detecting anomalies:
1.  **Statistical Baseline (Z-Score):** A standard, simple threshold check. If any single sensor reading (or its change rate) deviates by more than $3$ standard deviations from the historical mean, it is flagged as an anomaly.
    *   *Result:* Detected 55 anomalies.
2.  **Isolation Forest:** A tree-based machine learning algorithm explicitly designed for anomaly detection. It works by "isolating" data points; anomalies are easier to isolate because their values are unusual.
    *   *Result:* Detected 67 anomalies (using a conservative 5% contamination assumption).

*Why Isolation Forest is better:* The statistical baseline struggles with **multivariate anomalies** (e.g., pH is slightly high and Temp is slightly high—neither breaks the Z-score limit on its own, but the combination is highly toxic). Isolation Forest naturally detects these complex multivariate edge cases.

## 3. Visualizations

To explain this unsupervised model to the defense board, we generated three plots:
1.  **Anomaly Timeline (`outputs/figures/anomaly_timeline_tds.png`):** Shows the time-series curve of TDS, with bright red dots overlaid exactly where the Isolation Forest triggered an anomaly alert. This proves the model aligns with real-world spikes.
2.  **Multivariate Scatter (`outputs/figures/scatter_ph_vs_tds.png`):** Plots pH against TDS, coloring anomalies in red. This clearly visually separates the dense cluster of "normal" operations from the scattered dangerous outliers.
3.  **Score Distribution (`outputs/figures/anomaly_score_distribution.png`):** A histogram of the raw anomaly scores output by the algorithm, showing where the threshold cutoff was mathematically placed.

## 4. Defense Tips for Model 3

When presenting this model to the board, focus on these critical points:
*   **Unsupervised Learning is a Strength:** Emphasize that you chose *not* to use supervised classification because real ponds rarely have perfect datasets of "fish died here". Anomaly detection learns what a "healthy" pond looks like and flags anything else, making it highly robust for real IoT deployments.
*   **State the Limitation (Crucial for Academics):** Explicitly state (as per your PRD) that an anomaly **does not equal disease or fish death**. It simply means *"The current sensor pattern differs substantially from normal historical patterns."* It is a decision-support signal prompting the farmer to check the pond.
*   **The Power of Deltas:** Mention that you engineered *delta features* (`pH_change`). Tell the board: "A pH of 8.0 might be normal if it rose slowly, but a jump from 7.0 to 8.0 in one hour is an anomaly. By feeding the deltas to the Isolation Forest, the model successfully learned to flag sudden environmental shocks."
