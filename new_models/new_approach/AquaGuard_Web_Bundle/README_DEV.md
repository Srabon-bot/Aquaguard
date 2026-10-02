# AquaGuard Web Developer Bundle

Hello! This folder contains a self-contained, fully portable version of the AquaGuard IoT Dashboard and its 3 Machine Learning models. 

## Folder Structure
* **`frontend/`** : Contains the pure HTML/JS/CSS website. You can edit `index.html`, `app.js`, and `style.css` here. The site is currently configured to fetch data from `http://127.0.0.1:8000`.
* **`backend/`** : Contains the FastAPI unified server and the 3 machine learning models (Flood, TDS, Anomaly). 
* **`HOW_TO_RUN_AQUAGUARD.md`** : The detailed instruction manual.

## Quick Start for Developers

1. **Start the API (Backend)**
   Open your terminal, navigate into the `backend/` folder, and install the requirements:
   ```bash
   cd backend
   pip install -r requirements.txt
   ```
   Then start the unified ML server:
   ```bash
   python -m uvicorn api_combined:app --host 0.0.0.0 --port 8000 --reload
   ```

2. **Work on the UI (Frontend)**
   Open the `frontend/` folder in VS Code. Use the **Live Server** extension to open `index.html`. 
   As long as the terminal with the backend API is running in the background, the UI cards for Flood, TDS, and Anomaly Detection will automatically populate with data from the AI models.

## API Endpoints Reference
If you need to make changes to `app.js`, here are the endpoints the backend is serving on port 8000:
* `GET /flood/api/v1/forecast` (Returns JSON array of 14-day river water levels)
* `GET /api/v1/tds` (Returns JSON with predicted +60min TDS and trend)
* `GET /api/v1/anomaly` (Returns JSON with anomaly score and status)
  * *Note:* You can pass `?pH=9&tds=400&temp=30` to simulate a spike.
