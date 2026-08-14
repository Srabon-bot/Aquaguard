# Step 1 of 7 — pH sensor (wiring + kitchen calibration)

This is the first device in the rebuild. Get this working and calibrated before wiring
anything else — every later step assumes you already have a stable, sane-reading pH sensor
to compare new readings against (e.g. "did adding the relay module disturb the pH reading?").

---

## Part 1 — Wiring

Your pH module (green board, BNC connector, two blue trim potentiometers) has a small pin
header. Look at the tiny printed letters directly under each pin on your physical board — this
is the standard layout for this style of module:

| Module pin | Connects to | Notes |
|---|---|---|
| `-` | ESP32 **GND** | |
| `+` | ESP32 **3.3V** | **Not 5V — see warning below** |
| `Po` | ESP32 **GPIO 34** | The analog pH signal — this is the only signal pin you need |
| `Do` | *(leave unconnected)* | A digital high/low threshold output — not used by this project |
| `To` | *(leave unconnected)* | For an optional separate temperature probe — not used here (temperature is handled by the thermistor in Step 3 of the rebuild) |

The glass-bulb probe itself connects to the board via the **BNC connector** (the round
threaded silver connector) — twist it on until it clicks/locks, don't just push it in loosely.

### ⚠️ Why 3.3V and not 5V

Most tutorials for this exact module tell you to power it from 5V, because that's what a
classic Arduino Uno uses. **Don't do that here.** Two real, documented problems with 5V on an
ESP32:

1. The module's `Po` output can swing close to its own supply voltage. At 5V supply, that means
   `Po` can output close to 5V.
2. ESP32's **GPIO34 is an input-only pin with no built-in over-voltage protection.** Anything
   above 3.3V on it can permanently damage that pin — confirmed by multiple ESP32-forum threads
   about exactly this sensor ([Arduino Forum thread](https://forum.arduino.cc/t/calibration-problem-ph-4502c-with-esp32/896577), [ESP32 Forum thread](https://esp32.com/viewtopic.php?t=36631)).

Powering the module from **3.3V instead** keeps `Po`'s output physically incapable of exceeding
3.3V, since it can't output more than it's supplied — safe for GPIO34 with no extra parts
needed. The trade-off is a smaller usable voltage range than the 5V tutorials assume, which is
exactly why this project calibrates in software (below) instead of trusting a fixed formula
copied from a 5V tutorial.

---

## Part 2 — Kitchen calibration solutions (no lab buffers needed)

A real lab calibrates a pH probe using purchased buffer powders/tablets (pH 4.01 / 6.86 / 9.18)
that dissolve to an exact, certified pH. We don't have those. Instead, we use two household
liquids with **well-documented, fairly consistent approximate pH values**, and calibrate
against those instead. This is a recognized hobbyist technique — not lab-grade precision, but
good enough to tell you whether your pond/aquarium water is trending acidic, neutral, or
alkaline, which is what this project actually needs.

| Solution | How to make it | Approximate pH |
|---|---|---|
| **Acidic reference** | Plain **white distilled vinegar**, straight from the bottle — check the label says "5% acidity" (standard for distilled white vinegar) | **~2.4–2.5** |
| **Alkaline reference** | Dissolve **~1 teaspoon of baking soda (sodium bicarbonate) into 1 cup of water** and stir until fully dissolved | **~8.3** |

**Why not just use plain water as a "pH 7" reference?** Plain water — even distilled/RO water —
isn't a stable calibration point. It has no buffering capacity, so it absorbs CO₂ from the air
and drifts acidic (down toward pH 5.5–6.5) within minutes of being exposed. That's why this
procedure skips a "neutral" reference entirely and instead calibrates a straight line through
the two more stable points above (acidic and alkaline), letting the math tell you where 7.0
falls in between, rather than trying to physically hold a sample at exactly neutral.

**Use tap water to dissolve the baking soda if that's what you have** — it introduces a small
amount of extra error, but sodium bicarbonate solutions are fairly self-buffering: their pH
sits close to ~8.3 across a wide range of concentrations, so being a bit imprecise with "1
teaspoon" doesn't move the result much. Distilled/RO water is a small improvement if you happen
to have it, not a requirement.

**Honesty note for your report:** these are *approximate* reference points, not certified
buffers. Say so explicitly wherever this calibration is documented — e.g. "calibrated against
household vinegar (~pH 2.4) and a baking-soda solution (~pH 8.3) in the absence of lab buffer
standards; expect several tenths of a pH unit of absolute error, though relative trends
(rising/falling) remain meaningful." That's a true, defensible statement — claiming lab-grade
accuracy here would not be.

---

## Part 3 — Calibration procedure (using the calibration tool)

There are two sketches in this folder:

| Sketch | Purpose |
|---|---|
| `ph_calibration_tool/ph_calibration_tool.ino` | Run this **first**. Interactive — you type single-letter commands while dipping the probe in each solution, and it saves the result to the ESP32's flash memory. |
| `01_ph_sensor.ino` | Normal-use sketch. Automatically loads whatever the calibration tool saved — no editing required. Run this **after** calibrating. |

The calibration is stored in the ESP32's internal flash (NVS), so it survives power cycles and
re-uploading either sketch. You only need to rerun the calibration tool if you want to
recalibrate later (e.g. the probe drifts after weeks of use).

**Before you start:** keep the breadboard and ESP32 well clear of the liquids — only the probe
tip should ever touch a solution. Work over a towel. It's fine to leave the ESP32 plugged into
your computer via USB throughout this procedure.

1. Wire the pH module as described in Part 1.
2. Open `ph_calibration_tool/ph_calibration_tool.ino` in the Arduino IDE (same board/port setup
   as the main `Hardware_Wiring_Guide.pdf` — ESP32 Dev Module) and upload it.
3. Open the Serial Monitor, baud rate **115200**, line ending set to **Newline** (so a typed
   letter is actually sent when you press Enter). You should see a startup banner and a
   `[live] raw voltage:` line updating roughly every second — this confirms the wiring is good
   before you touch any liquid.
4. Prepare the two solutions from Part 2, each in its own small cup.
5. **Rinse the probe tip with clean water** and gently blot it dry (don't rub the glass bulb).
6. Dip the probe into the **vinegar**. Watch the `[live]` voltage settle (stop drifting) for
   ~30–60 seconds, then type **`a`** and press Enter. The tool captures a clean averaged reading
   and prints it back to you.
7. Lift the probe out, rinse with clean water, blot dry.
8. Dip the probe into the **baking soda solution**. Once it settles, type **`b`** and press
   Enter.
9. Type **`s`** and press Enter. This computes the calibration line and saves it to flash — you
   should see a "Saved to flash" summary.
10. Rinse and dry the probe once more when done; don't let it sit dry for long periods — store it
    with its wet cap/cover, or in a small amount of clean water, per its usual storage
    instructions.
11. Optional immediate sanity check, still inside the calibration tool: rinse the probe, dip it
    in a **third liquid** (plain tap water works well), and type **`t`** — it prints a live pH
    using the calibration you just saved, no reflashing needed.
12. When satisfied, open `01_ph_sensor.ino` and upload it. Its startup banner should say
    `Status: CALIBRATED (loaded from flash)` and show the same two calibration points you just
    saved — confirming the normal-use sketch picked them up automatically.

### Sanity check

- Back in `01_ph_sensor.ino` (or using `t` in the calibration tool): the vinegar should read
  close to **2.4**, the baking soda solution close to **8.3**, and plain tap water somewhere in
  between — typically **6.5–8** depending on your local tap water (a range, not a bug).
- If the number goes the *wrong way* (e.g. vinegar reads high, baking soda reads low), the two
  points were likely captured in the wrong order — rerun the calibration tool and make sure `a`
  is captured while the probe is genuinely in the vinegar, `b` while it's in the baking soda
  solution.
- If `s` refuses to save with a "voltages are almost identical" warning, the probe likely wasn't
  rinsed/settled between dips, or didn't actually leave the first liquid — redo steps 5–9.
- To wipe a bad calibration and start over, type **`c`** in the calibration tool at any time.

Once this is behaving correctly and consistently, this sensor is done — move on to Step 2
(ultrasonic sensor) in `hardware/rebuild/02_ultrasonic/` (to be created when you're ready).

---

## Sources used for the calibration values above

- [Arduino Forum — Calibration Problem pH-4502C with ESP32](https://forum.arduino.cc/t/calibration-problem-ph-4502c-with-esp32/896577)
- [ESP32 Forum — ESP32 & PH-4502C pH Sensor](https://esp32.com/viewtopic.php?t=36631)
- [Cirkit Designer — How to Use ph4502c: Pinouts, Specs, and Examples](https://docs.cirkitdesigner.com/component/607ee68e-1b94-4135-add3-ebb6e47d72a5/ph4502c)
- Household calibration reference values (vinegar ~pH 2.4–2.5, baking-soda solution ~pH 8.3) —
  cross-referenced across multiple hobbyist/DIY pH-meter calibration guides discussing
  buffer-free calibration using vinegar and baking soda.
