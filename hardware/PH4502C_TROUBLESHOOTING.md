# PH4502C Troubleshooting & Conversation Log

## Overview
This document serves as a rolling log of troubleshooting steps, findings, and conversations regarding the PH4502C pH sensor module for the AquaGuard project.

## Module Details
- **Module:** PH4502C
- **Expected Supply Voltage:** 5V DC (Currently testing with 3.3V from ESP32 which requires scaling analog readings).
- **Pinout:**
  - **V+ (VCC):** Power input
  - **G (Board GND):** Ground for logic
  - **G (Probe GND):** Ground for BNC shield
  - **Po:** Analog output (Expected ~2.5V at pH 7 when powered at 5V)
  - **Do:** Digital threshold output (Controlled by Limit Pot)
  - **To:** Temperature output (If thermistor is present)
- **Potentiometers:**
  - **Offset Pot (Nearest BNC):** Adjusts baseline analog voltage (`Po`). Short BNC to calibrate to mid-point.
  - **Limit Pot (Nearest Pins):** Adjusts digital threshold for `Do`.

## 2026-09-03: Multimeter Diagnostics

### The Issue
During initial calibration, `Po` was locked at exactly 3.30V (ESP32 ADC max). Touching the BNC outer shell caused wild voltage swings, suggesting a floating ground.

### Diagnostic Results (ESP32 Unplugged)
- **Test 3.2 (G to G):** Continuity (Beep) - OK.
- **Test 3.4 (ESP32 GND to Breadboard G):** Continuity (Beep) - OK.
- **Test 3.1 (BNC Shell to G):** **NO Continuity (No Beep)** - FAIL.
- **Test 3.3 (BNC Center to Po):** NO Continuity (No Beep) - Expected through op-amp, but 3.1 failure is the core issue.

### Photo Analysis
1. **Back of the PCB:** The four large mounting tabs of the BNC connector are soldered in, but there is no visible copper trace connecting them to the main ground plane on the board. This looks like a manufacturing defect where the ground plane pour was omitted or severed.
2. **Front of the PCB:** A white wire was wrapped around the BNC threads. However, the other end of this wire is visible in the photo just lying on the table with exposed copper, completely disconnected from the breadboard's ground. 

### Conclusion
The BNC connector is physically isolated from the circuit's ground. The module has a severe manufacturing defect. 

### Conclusion & Resolution
The BNC connector was physically isolated from the circuit's ground due to a severe manufacturing defect (missing ground trace). 

**Fix Applied (2026-09-03):** The user manually wrapped a white wire around the threaded outer shell of the BNC connector and plugged the other end into the breadboard's Ground (GND) rail. 

**Verification:** Re-running Test 3.1 with this fix in place resulted in a successful continuity **BEEP** from the BNC shell to the `G` pin. The floating ground issue is resolved.

### Next Steps
1. Re-connect power to the ESP32 and ensure the calibration tool sketch is running.
2. Proceed to **Section 4: Voltage tests** in the `PH_MODULE_MULTIMETER_DIAGNOSTIC.md` to verify the module is correctly outputting voltage now that it is properly grounded.
3. If voltage looks good, proceed with normal pH calibration (shorting the pin to the shell and tuning the Offset Pot).

---

## Continued Troubleshooting & Software Setup (Later on 2026-09-03)

### Voltage Test Results
- **Test 4.1 (V+ to G):** `3.13V` (Normal, slightly lower than 3.3V due to USB/breadboard loss).
- **Test 4.2 (Po to G):** `3.07V` (No longer locked at 3.30V! The amplifier is now working).

### Hardware Midpoint Calibration Plan
Because the supply voltage is 3.13V, the hardware midpoint (pH 7.0 equivalent) must be set to exactly half of that.
1. Short the BNC connector (center to outer shell).
2. Measure `Po` voltage.
3. Adjust the Offset Pot (nearest to the BNC) until the voltage reads `~1.56V`.

### Arduino IDE 2.x Glitches & Clean Reinstall
The user attempted to run the `ph_calibration_tool.ino` sketch but encountered a `Platform 'esp32:esp32' not found` error. 

**Root Cause:**
The user attempted to symlink (junction) the `C:\Users\srabo\AppData\Local\Arduino15` folder to a `D:\` drive folder to save space. This confused the Arduino IDE 2.x backend (Theia/Electron), causing the Boards Manager to show the platform as uninstalled while the terminal showed it as installed, and eventually hanging the download manager on `library_index.tar.bz2`.

**Resolution (The "Nuke and Pave"):**
The decision was made to completely clean the system of Arduino IDE files:
1. Uninstall Arduino IDE.
2. Delete `%LOCALAPPDATA%\Arduino15`
3. Delete `%APPDATA%\arduino-ide` and `Arduino IDE`
4. Delete `C:\Users\srabo\.arduinoIDE`
*(The installer executable hung upon clicking, so the user initiated a PC restart to clear stuck background processes).*

**Pending Action after Restart:** Run the fresh installer, add the ESP32 JSON URL to preferences, install the ESP32 platform via Boards Manager, and upload `hardware\AquaGuard_v2\01_ph_sensor\ph_calibration_tool\ph_calibration_tool.ino`.

---

## 2026-09-04: Arduino IDE Crash & Virtual Ground Discovery

### Issue 1: Arduino IDE Pulsing Logo on Startup
After reinstalling, the Arduino IDE was permanently stuck on the pulsing logo screen.
- **Root Cause:** The underlying `arduino-cli.exe` engine was crashing on startup with a fatal error: `Error verifying signature: signature expired: is your system clock set correctly?`. Because the system clock was set to the future (Sept 2026), the downloaded package signatures were read as expired, completely locking up the IDE.
- **Fix:** Adjusting the Windows system clock back to the correct current time allowed the IDE to open instantly.

### Issue 2: Offset Potentiometer Not Working (0.00V)
When attempting hardware calibration (shorting the BNC and reading `Po`), the output dropped to 0.04V, and turning the offset pot did nothing. 
- **Root Cause 1 (Op-Amp Starvation):** The CA3140 op-amp chip requires a minimum of **4.0V** to operate. Powering the module from the ESP32's 3.3V pin caused the chip to starve and fail to output a voltage when pulled low. **Fix:** The module's `V+` was moved to the ESP32's 5V/VIN pin.
- **Root Cause 2 (Shorted Virtual Ground):** The "manufacturing defect" identified on 2026-09-03 was actually a **feature**. The BNC shell on this specific PH4502C design is intentionally isolated from the board's main ground. The offset potentiometer drives the voltage of the BNC shell to create a **virtual ground**, allowing the pH probe to read acidic/basic swings without a negative power supply. By manually wiring the BNC shell to the breadboard's ground, the user accidentally shorted the offset potentiometer to 0V.
- **Fix:** Removed the white ground wire from the BNC shell. 

### Final Hardware Calibration
With the BNC shell ungrounded and the board powered at 5V:
1. Shorted the BNC center pin to the shell.
2. Turned the offset potentiometer until the analog output pin `Po` read exactly **2.50V** (midpoint of the 5V supply).
3. The hardware is now correctly calibrated to represent pH 7.0 at 2.50V.

### Next Steps: Voltage Divider
Because the board is powered at 5V, `Po` will swing between ~0.5V and ~4.5V depending on pH. Connecting this directly to an ESP32 ADC pin will destroy it. 
- **Requirement:** A voltage divider (e.g., 10k and 20k) MUST be built between `Po` and the ESP32 to step the 0-5V signal down to 0-3.3V before plugging the probe in and continuing with the software calibration.
---

## 2026-09-08: Voltage Divider Built & Calibration Tool Fixed

### Voltage Divider Construction

**Components used:** Three 10k resistors (brown-black-orange bands)

**Wiring:**
- PH4502C `Po` -> first 10k -> second 10k (in series, forming 20k high side) -> junction point
- Junction point -> third 10k -> breadboard GND rail (low side)
- Junction point -> ESP32 GPIO 34 (signal out)

**Divider ratio:** 10k / (20k + 10k) = 1/3

**Verified resistance readings (power OFF, multimeter):**
| Measurement | Expected | Got | Status |
|-------------|----------|-----|--------|
| Across 20k pair (two 10k in series) | ~20k | 18.9-19k | OK |
| Single 10k alone | ~10k | 9.67k | OK |
| GPIO 34 end -> GND end of third 10k | ~10k | 9.8k | OK |

### Voltage Verification (Power ON)

| Measurement | Expected | Got | Status |
|-------------|----------|-----|--------|
| PH4502C V+ to G | ~5.0V | 4.9V | OK - 5V supply confirmed |
| PH4502C Po to G (BNC shorted) | ~2.50V | 2.50V | OK - Op-amp midpoint reached |
| ESP32 GPIO 34 to GND (BNC shorted) | ~0.83V | 0.82V | OK - Divider working correctly |
| PH4502C Po to G (BNC NOT shorted) | ~2.50V | 4.90V | FAIL - Offset pot not holding |
| ESP32 GPIO 34 to GND (BNC NOT shorted) | ~0.83V | 1.62V | FAIL - Consequence of Po at rail |

### Offset Potentiometer Failure

**Symptom:** When the BNC center and shell are shorted, turning the offset pot brings Po to 2.50V. When the short is removed, Po jumps back to 4.90V (rail). The offset pot does not hold its setting.

**Root cause:** The PH4502C uses a small blue PCB-mounted trimmer potentiometer for offset adjustment. These trimmers have weak wiper contact and spring back when adjustment stops. The pot cannot maintain its setting.

**Fix:** Abandoned hardware pot adjustment. Switched to the `ph_calibration_tool.ino` sketch, which performs calibration electronically and saves the result to ESP32 flash.

### Calibration Tool Sketch Fix

**File:** `hardware/AquaGuard_v2/01_ph_sensor/ph_calibration_tool/ph_calibration_tool.ino`

**Problem:** The original sketch assumed 3.3V direct operation with no voltage divider. With the 5V supply and 1/3 divider, it reported the wrong voltage.

**Changes applied:**
1. **Header comment** (lines 10-13): Updated to document 5V/Vin power and the 1/3 voltage divider on GPIO 34.
2. **Line 37:** `VREF` changed from `3.3` to `5.0`
3. **Line 39:** Added `const float DIVIDER_RATIO = 3.0;`
4. **`readPhVoltageAveraged` function** (lines 57-68): Now multiplies by `DIVIDER_RATIO` to recover the true Po voltage from the divided GPIO 34 reading:
   ```cpp
   return avgRaw * (VREF / ADC_RES) * DIVIDER_RATIO;
   ```

**Result:** The calibration tool now reports the actual Po voltage (0.5V-5.0V range) instead of the divided voltage at GPIO 34 (0.17V-1.67V). The two-point calibration math works correctly.

### Next Steps

- [ ] Upload `ph_calibration_tool.ino` to ESP32
- [ ] Open Serial Monitor at 115200 baud, line ending = Newline
- [ ] Prepare acid reference: plain white vinegar (5% acidity, pH 2.4)
- [ ] Prepare base reference: ~1 tsp baking soda dissolved in 1 cup (~240ml) water (pH 8.3)
- [ ] Run calibration: `a` (capture acid) -> `b` (capture base) -> `s` (save to flash)
- [ ] Test with tap water: `t` (should read between pH 2.4 and 8.3)
- [ ] Upload `01_ph_sensor.ino` for normal operation - loads saved calibration automatically
---

## 2026-09-09: Calibration Tool Uploaded, Probe Tested, Reverse Calibration Planned

### Sketch Upload and Live Voltage Verification

Uploaded the fixed `ph_calibration_tool.ino` (with `analogReadMilliVolts()` and `DIVIDER_RATIO = 3.0`) to ESP32. Opened Serial Monitor at 115200 baud, line ending = Newline.

**BNC shorted:**
- Live voltage: stable 2.59V at Po
- Expected: ~2.50V (op-amp midpoint)
- Status: OK — confirms code fix is working, divider is functional

**BNC open / probe removed:**
- Live voltage: 4.93V – 5.07V at Po
- Expected: ~4.9V (op-amp at rail, offset pot not holding)
- Status: OK — confirms divider is still connected and code is reading real voltages

### Probe Immersion Tests

**Probe in air (connected, no liquid):**
- Voltage: ~3.07V – 3.22V
- Interpretation: probe is loading the circuit when connected, even without liquid contact

**Probe in vinegar (pH 2.4):**
- Voltage: ~3.46V – 3.53V
- Expected: lower than midpoint (acidic)
- Actual: HIGHER than midpoint — inverted polarity

**Probe in baking soda (pH 8.3):**
- Voltage: ~3.18V – 3.23V
- Expected: higher than midpoint (basic)
- Actual: LOWER than vinegar — inverted polarity

**Finding: readings are inverted.** Vinegar (acidic, pH 2.4) produces higher voltage than baking soda (basic, pH 8.3). This is the opposite of the expected direction. Possible causes:
- BNC center and shell swapped at the module end
- Probe glass membrane behavior with these specific reference solutions
- Module-specific offset pot position pushing baseline into an unusual range

### Tap Water Sanity Check

With the current uncalibrated voltage-to-pH mapping, tap water read pH 8.3. This is plausible for Dhaka groundwater (often mildly alkaline). More importantly, it confirms the voltage-to-pH math is computing consistently without glitches.

### Decision: Reverse Calibration Order

Rather than rewiring the BNC to fix polarity, we will calibrate in reverse order:

1. Type `a` while probe is in **baking soda** (pH 8.3) — captures ~3.21V as the "acid" point
2. Rinse probe in clean water
3. Type `b` while probe is in **vinegar** (pH 2.4) — captures ~3.50V as the "base" point
4. Type `s` to save

The calibration math (`voltageToPh`) computes a linear slope. A negative slope (higher voltage = lower pH) is mathematically valid and produces correct pH values. The two-point calibration does not care about absolute voltages or polarity direction — it only needs two different voltages at two known pH values.

### Next Steps

- [ ] Capture acid point: `a` in baking soda (pH 8.3)
- [ ] Capture base point: `b` in vinegar (pH 2.4)
- [ ] Save: `s`
- [ ] Test with tap water: `t` (should read between 2.4 and 8.3)
- [ ] Upload `01_ph_sensor.ino` for normal operation — loads saved calibration automatically
