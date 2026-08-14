# Step 7 of 7 — Full reintegration (v2)

The last rebuild step: all previously-tested sensors/pumps/servo merged back into one always-running
sketch, plus the new Firebase-driven pH calibration feature. **Not yet flash-tested on real hardware**
— written and reviewed carefully (reusing already-tested code wherever possible), but this specific
merged file hasn't been uploaded to a real board yet. Treat the first upload like any other rebuild
step: watch the Serial Monitor closely before trusting it.

---

## Before uploading

1. **Every individual sensor/pump should already be confirmed working** via `hardware/rebuild/
   01_ph_sensor/` through `05_relay_pumps/` (see `hardware/HARDWARE_LOG.md` for current status) —
   this step assumes that groundwork, it doesn't repeat it.
2. **Fill in your real WiFi + Firebase credentials.** Open `AquaGuard_v2.ino` and replace the 4
   placeholder `#define`s near the top (`WIFI_SSID`, `WIFI_PASSWORD`, `FIREBASE_HOST`,
   `FIREBASE_AUTH`) with your real values — see `hardware/FIREBASE_SETUP.md` for where to get them.
   **Never commit real values here** — this file is tracked in git.
3. **Publish the Firebase rules from `hardware/FIREBASE_SETUP.md`**, which now include a
   `phCalibration` path (added for this feature) alongside `sensor`/`pumps`/`control`/`alerts`/
   `history`/`servoTrigger`.
4. **Run the pH calibration tool once first** (`hardware/rebuild/01_ph_sensor/ph_calibration_tool/`)
   if you haven't already, OR just calibrate through the new dashboard page after uploading this
   sketch — either way works, since both save to the same flash location (see below).
5. **Libraries needed** (Arduino IDE → Library Manager): `Firebase ESP32 Client` (Mobizt),
   `ESP32Servo`. `Preferences` and `WiFi` ship with the ESP32 board package already.

## What's new here vs. every other rebuild step

This is the first sketch in the rebuild that does **everything at once** — WiFi, Firebase, all 4
currently-wired sensors, both pumps, the servo — matching
`hardware/original_reference/AquaGuard_full_original.ino`'s original scope, but with two real bugs
fixed (see `AquaGuard_v2.ino`'s own header comment for details: the thermistor formula, and the pH
formula) and one new feature:

### The pH calibration page (new)

Previously, recalibrating the pH probe meant re-flashing a *separate* sketch
(`ph_calibration_tool.ino`) over USB, running it via Serial Monitor, then re-flashing back to
whichever normal-use sketch. **That's gone now** — the exact same two-point calibration math lives
permanently inside this one sketch, dormant until triggered over Firebase instead of Serial. Open
`ph-calibration.html` (in `frontend/` or `frontend-glass/`) on any phone/browser on the same network
as your Firebase project, and:

1. Dip the probe in vinegar, click **Capture acid point**.
2. Dip the probe in the baking soda solution, click **Capture base point**.
3. Click **Save calibration**.

Fixed to vinegar (pH 2.4) / baking soda (pH 8.3) always — matches
`CAL_PH_ACID`/`CAL_PH_BASE` in `AquaGuard_v2.ino`. Saves to the same flash location
(`Preferences` namespace `"phcal"`, keys `v_acid`/`v_base`/`ph_acid`/`ph_base`) that
`01_ph_sensor.ino` and `ph_calibration_tool.ino` already use — a calibration saved from any of the
three is readable by all three, nothing is duplicated or out of sync.

You still need to be physically at the pond to actually swap the probe between the two solutions —
this removes the "need a laptop + USB cable + Arduino IDE" requirement, not the physical part.

## What's still NOT in this sketch

Deliberately out of scope for this step (separate, not-yet-built future work):

- Water-quality safety auto-cycling (drain+refill automatically if pH/TDS/temp go out of safe range).
- Water-level setpoint control (auto-drain toward a marked level).
- The model-informed pump-suggestion panel on the dashboard.
- Converting `/sensor/waterLevel` from raw sensor-to-surface distance into a "cm of water" value.

## Testing this step

1. Upload `AquaGuard_v2.ino`, open Serial Monitor at 115200 baud.
2. Confirm WiFi connects and Firebase initializes (same messages as the original reference sketch).
3. Confirm it prints "pH calibration loaded from flash" (if you already calibrated) or "No saved pH
   calibration yet" (if you haven't) — either is fine, both are expected states.
4. Watch the normal sensor readings print every ~1.5s, same as before.
5. Open `ph-calibration.html`, confirm the live voltage reading updates roughly once a second and
   matches what Serial is showing.
6. Run through the 3-step calibration flow above, confirm Serial prints "pH calibration saved to
   flash" and the next `/sensor/ph` reading uses it (no longer prints "Not calibrated yet").
