# AquaGuard dashboard (frontend)

A single static page — no build step, no npm install. Plain HTML/CSS/JS.

## Running it

**Recommended: serve it locally** (geolocation and some browsers behave more reliably over
`http://` than a raw `file://` path):

```
cd frontend
python -m http.server 5500
```

Then open **http://localhost:5500** in your browser.

(Opening `index.html` directly by double-clicking it will often work too — try that first if you
don't want to run a server — but switch to the method above if "Use my location" doesn't prompt
for permission.)

## Before using the model sections

The two model cards ("Get flood risk" / "Get discharge forecast") call your own local FastAPI
services. Start whichever ones you want to use, each in its own terminal:

```
cd packages/flood-risk-classifier
uvicorn main:app --port 8000
```

```
cd packages/discharge-forecaster
uvicorn main:app --port 8001
```

See each package's own `README.md` for first-time venv setup. The dashboard's station dropdown
also depends on at least one of these running — it fetches the real 30-station list from
whichever service answers first.

If a service isn't running, its button still works — you'll get a clear on-page message with the
exact command to start it, instead of a silent failure.

## What's real vs. placeholder right now

- **Weather** — real, live, from Open-Meteo's free API. No key needed.
- **Both model cards** — real, live predictions from your own trained models, once their
  services are running.
- **Sensor tiles (pH / TDS / temperature / water level) and the tank fill visual** — **demo
  data**, clearly labeled with a "DEMO DATA" badge. These are a gentle random walk in
  `app.js`, not real readings. The hardware rebuild (`hardware/HARDWARE_LOG.md`) hasn't reached
  full reintegration with WiFi/Firebase yet, so there's no live data to show. This was a
  deliberate choice, not an oversight — see the project's standing rule against building on
  fabricated data as if it were real (`PROJECT_FEATURE_IDEAS.md`'s discussion log).
- **Pump control + water cycle** — **simulated**, clearly labeled "SIMULATED — NOT WIRED YET".
  Buttons only change on-screen state; nothing is written to Firebase. Manual toggle for each
  pump, plus a "Start water cycle" that runs pump 1 (drain) for an editable duration, then
  automatically switches to pump 2 (refill) for another editable duration, with a live progress
  bar and a cancel button. Same reasoning as the sensor data: real control needs real Firebase
  writes to `/pumps/pump1` / `/pumps/pump2` (the same paths `controlPumps()` in
  `hardware/original_reference/AquaGuard_full_original.ino` already reads), and that's held off
  until hardware is actually reintegrated — see the wiring note below.

## Wiring up real sensor data later

Once the hardware rebuild finishes Step 7 (full reintegration, pushing to the same Firebase
Realtime Database the original sketch used), replace the `tickDemoSensors()` block in `app.js`
with a Firebase Realtime Database listener instead. That does mean putting your Firebase project
config in this client-side file — fine for local/private use (your ESP32 firmware already embeds
the same credentials), but **don't publish this file anywhere public without first switching to
proper read-scoped Firebase security rules** rather than the legacy full-access database secret.

## Design

Neumorphic ("soft UI") style — elements are the same color as the page background, with depth
coming from paired light/dark shadows rather than borders or contrasting card fills. Status
colors (risk levels, trends) are the one deliberate exception: they carry real meaning, so they
use a tinted background + icon + text label instead of relying on the soft-shadow look, so risk
level is never conveyed by color alone.

Supports light/dark mode — follows your OS setting by default, or use the toggle in the top-right
corner (saved in `localStorage`).
