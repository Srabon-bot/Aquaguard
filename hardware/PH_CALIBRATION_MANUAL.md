# pH Calibration Manual

How to calibrate the AquaGuard pH probe using the dashboard's pH calibration page — no laptop, no USB
cable, no re-flashing the ESP32. Just two kitchen ingredients and a phone.

---

## What you need

- The probe already wired and the ESP32 running
  `hardware/rebuild/07_full_reintegration/AquaGuard_v2.ino` (see that folder's `README.md` for setup
  — WiFi/Firebase credentials filled in, Firebase rules published).
- Plain white vinegar (5% acidity — the regular kind from any kitchen).
- Baking soda + water: dissolve about 1 teaspoon of baking soda in 1 cup of water, stirred well.
- Two small cups/containers to dip the probe in.
- Clean water to rinse the probe between solutions.
- A phone or laptop browser on the **same network** as the ESP32, open to `ph-calibration.html`
  (linked from the main dashboard's header — the 🧪 pH calibration button).

Why these two solutions specifically: vinegar sits at a known, reliable acid reference (pH ≈ 2.4) and
baking-soda solution at a known base reference (pH ≈ 8.3) — both cheap, safe, and available in any
kitchen, no lab chemicals or buffer-solution packets needed. These two fixed values are built into the
firmware; this page and manual assume you're always using these same two solutions.

---

## Step-by-step

### 1. Rinse the probe

Rinse the pH probe tip with clean water before starting, and again every time you switch between
solutions below — carrying residue from one solution into the next throws off the reading.

### 2. Capture the acid point (vinegar)

1. Dip the probe in the vinegar.
2. On the pH calibration page, watch the **live voltage** reading — wait for it to stop drifting
   (settle), usually a few seconds.
3. Click **🧪 Capture acid point (vinegar)**.
4. The page's status will change to show the captured voltage. If it doesn't update within a couple of
   seconds, see [Troubleshooting](#troubleshooting) below.

### 3. Rinse, then capture the base point (baking soda)

1. Rinse the probe with clean water.
2. Dip it in the baking soda solution.
3. Wait for the live voltage to settle again.
4. Click **🧂 Capture base point (baking soda)**.

### 4. Save

Once both points show as captured, click **💾 Save calibration**. This writes the calibration to the
ESP32's permanent flash memory (it survives power loss and reboots) and takes effect **immediately** —
no reboot needed, no re-flashing.

### 5. Rinse and return the probe to the pond

You're done. The next `/sensor/ph` reading the dashboard shows will already use the new calibration.

---

## How often should I recalibrate?

pH probes drift over time (weeks to a few months, depending on the probe and how it's stored between
uses). A rough sign it's time to recalibrate: readings that don't move at all when you know conditions
have changed, or readings that seem consistently off from what you'd expect. There's no harm in
recalibrating more often than needed — it takes a couple of minutes.

---

## Troubleshooting

- **The page shows "This page isn't wired up yet"** — `FIREBASE_BASE_URL` hasn't been filled in inside
  `ph-calibration.js` yet. See `hardware/FIREBASE_SETUP.md`.
- **Live voltage never updates / stays at "—"** — the ESP32 isn't reachable. Check it's powered on,
  connected to WiFi (its Serial Monitor prints "WiFi Connected!" on boot), and that
  `FIREBASE_BASE_URL` in `ph-calibration.js` matches the same Firebase project the ESP32's
  `FIREBASE_HOST` points at.
- **"The two captured voltages are almost identical" error when saving** — this means the probe didn't
  actually register a different reading between the two solutions, usually because it wasn't rinsed
  between them, wasn't given time to settle, or wasn't actually moved. Rinse thoroughly, recapture both
  points, try again.
- **Want to start over completely?** Click **🗑 Clear saved calibration** — this erases the saved
  calibration from flash entirely (the sensor will read "Not calibrated yet" until you calibrate
  again).
- **Using a different reference solution than vinegar/baking soda?** Not supported by this page on
  purpose — the reference pH values (2.4 / 8.3) are fixed constants in the firmware
  (`CAL_PH_ACID`/`CAL_PH_BASE` in `AquaGuard_v2.ino`). If you switch reference liquids, those two
  constants need to change and the firmware re-flashed — see that file's own comments.

---

## Under the hood (optional reading)

This page doesn't do any pH math itself — it just shows you the ESP32's live reading and sends simple
"capture now" / "save" commands over Firebase. All the actual calibration math (the same two-point
linear formula used by `hardware/rebuild/01_ph_sensor/`) runs on the ESP32 itself, exactly as it
always has — only the *trigger* moved from a USB-connected Serial Monitor to this web page. See
`hardware/rebuild/07_full_reintegration/README.md` for the full technical protocol if you're curious
or need to debug it.
