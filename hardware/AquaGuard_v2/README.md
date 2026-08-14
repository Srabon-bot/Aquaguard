# AquaGuard_v2 — one folder for the whole bring-up: per-device tests + the final combined firmware

Everything you need to wire up and test the hardware one device at a time, then upload the real
combined firmware last, all from this one folder — copies of the same sketches that live in
`hardware/rebuild/` (kept there too, as the documented build history), gathered here so you don't
need to jump between folders while actually working on the device.

```
AquaGuard_v2/
├── AquaGuard_v2.ino          <- the FINAL combined firmware, upload this LAST
├── 01_ph_sensor/               <- test each device one at a time, in this order,
├── 02_ultrasonic/                 as you physically wire each one in
├── 03_thermistor/
├── 04_tds/
├── 05_relay_pumps/
└── 06_servo/
```

## Recommended order

1. Wire **one** device (start with `01_ph_sensor/`, per `hardware/Hardware_Wiring_Guide.pdf`).
2. Open that step's own `.ino` in Arduino IDE, upload it, confirm it works via Serial Monitor (each
   step folder's sketch is a minimal, standalone test — no WiFi, no Firebase, no other devices mixed
   in, so a wiring mistake is obvious immediately instead of hiding inside the full sketch).
3. Move to the next device, repeat.
4. `01_ph_sensor/` also has a `ph_calibration_tool/` subfolder — run that once after wiring the pH
   probe (see `hardware/PH_CALIBRATION_MANUAL.md`), or just calibrate later through the dashboard's
   pH calibration page once the main firmware is running — either works, both save to the same place.
5. **Once all 6 are individually confirmed working**, wire everything together per the full diagram,
   fill in the 2 remaining values in `AquaGuard_v2.ino` (below), and upload that — the real, final,
   always-running firmware.

## 2 things to fill in before uploading `AquaGuard_v2.ino`

Open `AquaGuard_v2.ino`, find these lines near the top:

```cpp
#define WIFI_SSID     "YOUR_WIFI_SSID"
#define WIFI_PASSWORD "YOUR_WIFI_PASSWORD"

#define FIREBASE_HOST "aquasheild-2e2ca-default-rtdb.asia-southeast1.firebasedatabase.app"
#define FIREBASE_AUTH "YOUR_FIREBASE_DATABASE_SECRET"
```

1. **`WIFI_SSID` / `WIFI_PASSWORD`** — your own WiFi network's name and password.
2. **`FIREBASE_AUTH`** — your database secret. Get it from the Firebase console: gear icon → Project
   settings → Service accounts tab → Database secrets → Show. Full instructions:
   `hardware/FIREBASE_SETUP.md` Step 5.

**`FIREBASE_HOST` is already filled in** — that's your real "AquaSheild" project's Realtime Database
address. It's not a secret (safe to see/share), unlike the two items above.

**Never commit real WiFi/Firebase-secret values to git** — this file is tracked in the repo. Fill
them in locally only, and if you ever share this folder or push a change, put the placeholders back
first (or keep your real values in a separate untracked copy).

## Libraries needed

Arduino IDE → Tools → Manage Libraries, install:
- **Firebase ESP32 Client** (by Mobizt)
- **ESP32Servo**

(`WiFi` and `Preferences` ship with the ESP32 board package already.)

## After uploading

1. Open Serial Monitor at **115200 baud**.
2. Confirm it prints `WiFi Connected!` and your ESP32's IP address.
3. Confirm it prints either `pH calibration loaded from flash` or `No saved pH calibration yet` (both
   are fine — the second just means you haven't calibrated yet, see below).
4. Watch it print sensor readings every ~1.5 seconds.
5. Open `frontend-glass/ph-calibration.html` (fill in `FIREBASE_BASE_URL` at the top of
   `ph-calibration.js` with your databaseURL first, if you haven't) and confirm the live voltage
   reading updates and matches what Serial shows.
6. Calibrate the pH probe via that page (vinegar → base soda → save) — see
   `hardware/PH_CALIBRATION_MANUAL.md` for the full walkthrough.

## If something's not working

See `hardware/rebuild/07_full_reintegration/README.md`'s "Testing this step" section — same firmware,
same troubleshooting steps, this folder is just the copy with your real Firebase host pre-filled and
the correct folder-name structure for Arduino IDE.
