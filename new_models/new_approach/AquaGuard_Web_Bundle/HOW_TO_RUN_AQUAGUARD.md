# AquaGuard System: Local Deployment & Portability Guide

Yes! The system is now **fully portable**. All absolute paths (`D:\Projects\...`) have been removed from the backend architecture. The Python scripts now use relative directory mapping (like `os.path.dirname(__file__)`), which means you can zip this entire project, copy it to a USB drive, paste it on your professor's PC, or deploy it to a cloud server, and it will run instantly without breaking.

This document explains exactly how to run the full end-to-end system (Frontend Dashboard + All 3 Machine Learning Models).

---

## 1. Prerequisites

Before running the project on a new PC, ensure the computer has:
*   **Python 3.9+** installed (check by running `python --version` in terminal).
*   A modern web browser (Chrome, Edge, Firefox).

## 2. One-Time Setup (Installing Dependencies)

If you have moved the project to a new PC, you need to install the Python libraries required by the Machine Learning models.

1. Open a terminal (Command Prompt or PowerShell).
2. Navigate to the `new_approach` folder:
   ```bash
   cd path/to/pred_flood/new_models/new_approach
   ```
3. Install the required libraries using the provided `requirements.txt`:
   ```bash
   pip install -r requirements.txt
   ```
   *(This installs FastAPI, Pandas, Scikit-Learn, XGBoost, SHAP, etc.)*

---

## 3. Step-by-Step Running Guide

To see the fully integrated system, you need to run two things: the **Backend Server** and the **Frontend Website**.

### Step A: Start the Unified ML Backend
The backend powers all three machine learning models. 

1. Open your terminal and navigate to the `new_approach` folder.
2. Run the unified API script:
   ```bash
   cd path/to/pred_flood/new_models/new_approach
   python -m uvicorn api_combined:app --host 0.0.0.0 --port 8000 --reload
   ```
3. **Success Check:** You should see `Uvicorn running on http://0.0.0.0:8000`. Keep this terminal window open! 
   * *Optional:* You can view the automatic API documentation by visiting `http://127.0.0.1:8000/docs` in your browser.

### Step B: Open the Frontend Dashboard
The frontend is built with vanilla HTML/JS, making it extremely lightweight and portable.

1. Navigate to the `frontend` folder (`pred_flood/frontend`).
2. Simply double-click **`index.html`** to open it in your browser.
3. *Alternative (Recommended for best performance):* If you use VS Code, right-click `index.html` and select **"Open with Live Server"**.

---

## 4. What You Will See on the Dashboard

If the backend is running correctly, the frontend will automatically connect to it and display the results of all 3 models:

1. **Model 1 (River Flood Forecast):** Scroll to the bottom to see the Bahadurabad water-level hydrograph, current alerts, and bilingual farmer advice.
2. **Model 2 (Pond Water Quality AI):** Located right under the top live-sensor tiles. You will see the `+60 min` predicted TDS value. If the model predicts a sharp increase, the card will turn orange/yellow.
3. **Model 3 (Anomaly Detection):** Next to Model 2, you will see the Isolation Forest anomaly score. 
   * **Demo Tip:** Click the **"Simulate Sensor Spike"** button! This sends a fake dangerous reading (pH 9.5, TDS 450) to the backend. The Isolation Forest will catch it, and the card will instantly turn **RED** and display `ANOMALY DETECTED` for 5 seconds before returning to normal. This is a massive crowd-pleaser for defense presentations.

---

## 5. Troubleshooting on a New PC

* **"Forecast service offline" error on the website:** 
  This means the website cannot find the backend. Ensure your terminal running `uvicorn api_combined:app` is open, hasn't crashed, and is running on port `8000`.
* **Python command not found:**
  Ensure Python is added to the system `PATH` during installation.
* **Missing module errors:**
  Ensure you ran `pip install -r requirements.txt`. If `joblib` or `fastapi` is missing, install it manually: `pip install fastapi uvicorn scikit-learn pandas`.
