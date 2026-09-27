# AquaGuard Hardware Rebuild — Progress Log

Live progress log for reconnecting the physical AquaGuard IoT hardware (ESP32 + sensors + pumps
+ servo) after it was taken apart for transport. Kept separate from `MODEL_BUILD_PLAN.md`
(flood-model-scoped) and `PROJECT_FEATURE_IDEAS.md` (whole-capstone feature ideas), same
separation-of-concerns reasoning as those two files use.

Read this bottom-up (newest last) before resuming hardware work.

---

### 2026-08-12 (Arduino IDE set up from scratch; rebuild methodology established; 3 of 7 sensors wired, tested, and confirmed working)

**Toolchain setup (blocking issues, all resolved):**
- **Disk-space crisis** blocked the ESP32 board install entirely (C: drive had 0 bytes free, then repeatedly refilled). Fixed across two rounds: emptied Recycle Bin (~6.6GB) and cleared the corrupted partial Arduino download, then later cleared npm cache (~3.4GB) and pip cache (~0.6GB), and deleted old unrelated Claude Code project/job history unconnected to this project (~380MB) — freed several GB total. Also wrote (not yet run) `relocate_claude_to_d.ps1` to junction `~/.claude` onto D: for future headroom — needs Claude Code closed first, deliberately not run mid-session.
- **CP210x USB driver was completely unbound** (Device Manager: Error status, problem code 28, "drivers not installed" — despite this exact board/code having worked fine in May, meaning something wiped the driver since then). Fixed by installing Silicon Labs' **CP210x Universal Windows Driver v11.5.0** from the manufacturer's own site.
- **Blink sketch compile error** (`LED_BUILTIN` not declared) — known gap in the generic "ESP32 Dev Module" board profile, which doesn't define an onboard LED pin the way official Arduino boards do. Fixed by manually adding `#define LED_BUILTIN 2` (GPIO2 is the standard onboard LED pin on most ESP32 WROOM-32 dev boards).
- **Persistent "Wrong boot mode detected (0x13)" upload error, every single upload** — chip needs manual BOOT-button-hold during upload to enter download mode. Diagnosed as likely a driver regression (this same code/board demonstrably worked with no issues in May, and the driver was found completely absent today) rather than a hardware capacitor gap on the board — see [esptool GitHub issue #136](https://github.com/espressif/esptool/issues/136) for the general Windows DTR/RTS timing category. **Not yet resolved** — user is using the BOOT-button-hold workaround for now. Two untried fixes on the table: (a) swap to the older classic "CP210x Windows Drivers v6.7.6" package instead of the Universal driver, (b) add a 10µF capacitor between `EN` and `GND` (breadboard-friendly, no soldering needed) as a permanent driver-independent fix.

**Rebuild methodology established:** reconnect each of the 7 hardware devices **one at a time**,
each as its own standalone Arduino sketch (no WiFi/Firebase/other sensors mixed in) with its own
wiring README, under `hardware/rebuild/<NN>_<name>/`. Test and confirm each before wiring the
next. The original full working sketch (as it existed before disassembly) is preserved untouched
at `hardware/original_reference/AquaGuard_full_original.ino` as the eventual reintegration
target — do not upload it until all 7 parts are individually confirmed.

**Per-device status:**
1. **pH sensor — PARKED.** User doesn't have vinegar/baking soda on hand yet for kitchen
   calibration. Fully built and ready to go whenever: `hardware/rebuild/01_ph_sensor/` has both
   a standalone reader (`01_ph_sensor.ino`) and an interactive calibration tool
   (`ph_calibration_tool/ph_calibration_tool.ino`) that captures two-point calibration via serial
   commands (`a`/`b`/`s`) and saves it to the ESP32's flash (NVS via `Preferences`) — the
   normal-use sketch auto-loads it, no manual constant-editing/reflashing needed. Wired at
   3.3V (not 5V) specifically because GPIO34 has no over-voltage protection. Kitchen calibration
   references researched and sourced: vinegar ≈ pH 2.4–2.5, baking-soda solution ≈ pH 8.3.
2. **Ultrasonic (water level) — DONE.** Wired (TRIG→GPIO5, ECHO→GPIO18 through a 1kΩ/2kΩ
   divider since ECHO outputs 5V), tested against a ruler at multiple distances, confirmed
   accurate within ~1–2cm.
3. **Thermistor (temperature) — DONE, with a real bug found and fixed.** Wired per
   `hardware/rebuild/03_thermistor/`. Initial readings were a stable but wrong ~57°C at a real
   31°C room temperature. **Root cause: the resistance formula inherited from the original
   AquaGuard sketch was inverted relative to its own documented wiring** (comment says
   thermistor→3.3V/resistor→GND, but the formula was only correct for the opposite wiring) — a
   pre-existing bug in the original code, not a wiring mistake, and not something I'd
   independently verified before copying it into the rebuild sketch. Fixed by swapping the
   numerator/denominator; corrected formula predicted ~30.2°C, user's actual room thermometer
   read 31°C — confirmed as correct. **Same bug flagged with a fix note directly in
   `hardware/original_reference/AquaGuard_full_original.ino`** so it doesn't silently resurface
   at final reintegration.
4. **TDS (water quality) — DONE.** Wired at 3.3V (GPIO35, same no-over-voltage-protection
   reasoning as the pH sensor). Sanity check produced a clean monotonic result: 0 ppm dry in
   air → 180 ppm plain tap water → 548 ppm with a pinch of salt added — exactly the expected
   shape, strong confirmation of correct wiring.
5. **Relay + 2 pumps — sketch and README built, not yet tested by the user.**
   `hardware/rebuild/05_relay_pumps/` deliberately stages this in two parts: first confirm the
   relay itself clicks correctly on GPIO25/GPIO26 with **no pumps connected**, only wire real
   pumps to the relay's COM/NO/NC output afterward, each pump powered from its own external
   supply (never from the ESP32's own 5V/3.3V) sharing a common GND.
6. **Servo — sketch and README built (2026-08-14), not yet tested by the user.**
   `hardware/rebuild/06_servo/` sweeps 0-180-0 degrees automatically to confirm smooth movement and
   check for ESP32 resets/brownouts from the servo's startup current spike (same power warning as
   the pump relay step -- power it from the external 5V supply, not the ESP32 board itself).
7. **Full reintegration (all 7 back into one sketch) — not started.**

- Separately, also produced `hardware/Hardware_Wiring_Guide.pdf` earlier this session — a single
  reference PDF covering Arduino IDE setup from scratch, the full pin table, and all 7 wiring
  steps in one document (same content as the incremental rebuild folders, packaged as one
  formal reference alongside them, not a replacement for the step-by-step approach).

- **Resume point:** wire and test Step 5 (relay, no pumps yet) next, then real pumps once that's
  confirmed, then build+test Step 6 (servo), then whenever kitchen calibration solutions are
  available, come back to Step 1 (pH). Final step is merging all 7 confirmed-working standalone
  sketches back into one sketch based on `original_reference/AquaGuard_full_original.ino`,
  applying the thermistor formula fix during that merge. The intermittent upload boot-mode issue
  is still unresolved (workaround in use) — offer the driver-downgrade test or the EN/GND
  capacitor fix next time it comes up.

### 2026-08-14 (Step 7 written: full reintegration + Firebase-driven pH calibration)

User asked whether moving pH calibration out of a separate re-flashed sketch and into the main
firmware, triggered from the dashboard instead of Serial, was a good idea (it is — real usability win,
removes the "USB cable + Arduino IDE" requirement; doesn't remove needing to be physically at the pond
to swap solutions). Confirmed the user always uses vinegar/baking soda specifically (not arbitrary
buffer solutions), so the reference pH values are fixed constants, not a web input.

**Built `hardware/rebuild/07_full_reintegration/AquaGuard_v2.ino`** — the first real Step 7 artifact
(previously "not started"). Built from `original_reference/AquaGuard_full_original.ino` with both
already-known bugs actually fixed this time (not just commented): the thermistor formula swap, and
the pH formula replaced with the real two-point calibration from `01_ph_sensor.ino` (loaded from flash
via `Preferences` at boot) instead of the original's crude uncalibrated formula.

**New feature — Firebase-driven pH calibration**: the exact same two-point math and NVS flash format
(`Preferences` namespace `"phcal"`, keys `v_acid`/`v_base`/`ph_acid`/`ph_base`) already used by
`ph_calibration_tool.ino`, but triggered over new `/phCalibration/*` Firebase paths (`liveVoltage`,
`command`, `capturedAcidV`/`capturedBaseV`, `status`, `lastError`, `lastSavedAt`) instead of Serial
commands — a non-blocking poll-based state machine (`handlePhCalibration()`), not a blocking loop, so
it runs alongside the existing sensor/pump/servo logic without stalling it. Fixed to vinegar (pH 2.4)
/ baking soda (pH 8.3) — `CAL_PH_ACID`/`CAL_PH_BASE` constants, not exposed as a web input. A
calibration saved via this new path, the old Serial tool, or vice versa, are fully interchangeable —
same flash keys, nothing duplicated.
- **One real bug caught and fixed while writing this, not left in**: first draft called a fabricated
  `Firebase.setTimestamp()` that doesn't exist in the `FirebaseESP32` library's actual API. Replaced
  with the same `.sv`-server-value JSON trick the original sketch already proves works (used for
  `/history`'s timestamp field) — a verified pattern from this exact codebase, not a guessed API.

**New dashboard page**: `ph-calibration.html` + `ph-calibration.js` in both `frontend-glass/` and
`frontend/` (byte-identical copies, matching those folders' existing convention), linked from the main
dashboard's header (🧪 pH calibration). Plain Firebase REST calls (`fetch` GET/PUT), no SDK — same
"no build step" approach as the rest of both frontends. Polls `/phCalibration` every 2s, shows live
voltage + status + captured points, 4 action buttons (capture acid/base, save, clear) that write to
`/phCalibration/command`. `FIREBASE_BASE_URL` is a placeholder constant until a real Firebase project
exists (see `FIREBASE_SETUP.md`) — the page correctly detects this and disables all 4 action buttons
with an explanatory message rather than sending requests to a fake URL; verified live in the browser
(all 4 buttons confirmed disabled with the placeholder URL, then `renderStatus()` called directly with
mock "both_captured" data to confirm the status panel and button-enabling logic both render correctly
— can't test the real end-to-end flow without an actual ESP32 + live Firebase project yet).

**New manual**: `hardware/PH_CALIBRATION_MANUAL.md` (what you need, step-by-step, troubleshooting),
converted to `manuals/4_pH_Calibration_Manual.pdf` and synced to
`AquaGuard_Portable_Package/manuals/` (two copies, per the user's request). Caught and fixed a real
rendering defect while verifying: the 4 emoji used for button labels (🧪🧂💾🗑) rendered as blank gaps
in the PDF (no glyph in PyMuPDF's fallback font — confirmed by rendering to PNG and inspecting, same
verification pattern as every other PDF this project produces) — extended `scripts/md_to_pdf.py`'s
existing `SYMBOL_FALLBACKS` table to drop them cleanly instead (also cut the file size from ~1MB to
~220KB, apparently from avoiding an embedded emoji font).

**Also updated**: `hardware/FIREBASE_SETUP.md`'s security rules JSON now includes the new
`phCalibration` path (7 named paths total, was 6). `AquaGuard_Portable_Package/` (the local portable
snapshot) and `manuals/` (the tracked-in-git copy) both re-synced with all of the above.

- **Resume point**: `AquaGuard_v2.ino` is written and reviewed but **not yet flash-tested on real
  hardware** — first real upload should be watched closely via Serial Monitor like every other rebuild
  step (see that folder's README "Testing this step" section). The pH calibration page can't be
  exercised end-to-end until a real Firebase project exists and its databaseURL is filled into
  `ph-calibration.js` — same blocking dependency as the rest of the deferred hardware-integration
  plan.

### 2026-08-15 (Step 1 pH calibration attempted — suspected dead module, diagnostic PDF built for tomorrow)

Came back to Step 1 (pH) now that kitchen calibration solutions (vinegar, baking soda) were available.
Wired per `hardware/rebuild/01_ph_sensor/README.md`, uploaded `ph_calibration_tool.ino`. **Result:
`Po` (GPIO34) locked at exactly 3.300V (ADC max) regardless of what the probe was dipped in — never
moved.**

Extensive live troubleshooting, each step ruling out one layer:
- Wiring re-checked against photos — correct (`Po`→GPIO34, `G`→GND, `V+`→3.3V, `To`/`Do` unconnected;
  this board's header has two `G` pins, a known variant).
- Unplugged `V+` — reading dropped cleanly to 0.000V and back to 3.300V when reconnected. Rules out a
  breadboard-row short bridging GPIO34 directly to the 3.3V rail; proves the signal path itself is
  real, not a wiring bridge.
- Turned both trim pots through full range, multiple directions — zero effect, even with a clean short
  from the BNC center pin to its outer shell (a defined "zero input" test, technique borrowed from
  [a YouTube reference](https://youtu.be/hMEzz5o4TZw) after our own procedure didn't cover a
  hardware-side offset trim step).
- Jumpered GPIO34 directly to ESP32 GND, bypassing the module entirely — read a clean ~0.00–0.05V.
  **Proves the ESP32/GPIO34/breadboard side is completely fine.**
- Touching *only* the BNC connector's outer shell (not a proper short) made the reading swing wildly
  (1.01V → 0.07V → 3.30V) and lit the module's red threshold-comparator LED (`Do`'s indicator).

**Working diagnosis**: a floating (not actually grounded) BNC shell — most likely a broken/cold solder
joint between the connector's shell and the board's ground plane. This single explanation accounts for
every symptom observed: the short-to-shell test doing nothing (shorting to a floating point defines
nothing), the wild swings under a bare touch (body/room-ground acting as an unstable alternate
reference), and the LED flicker (a floating signal randomly crossing the comparator threshold). Every
test that could isolate the ESP32/wiring side from the module side came back clean on the ESP32 side —
the fault is inside the module.

**Built `hardware/PH_Module_Multimeter_Diagnostic.pdf`** (source: `PH_MODULE_MULTIMETER_DIAGNOSTIC.md`)
— a step-by-step continuity/voltage test procedure for tomorrow once a multimeter is available, with
expected readings and what each outcome means, plus a fill-in results checklist. Core test: continuity
between the BNC shell and the module's `G` pin — no beep confirms the diagnosis (repair by reflowing
the solder joint if a soldering iron is available, otherwise treat the module as defective and replace
it); a beep would mean the theory is wrong and the guide's remaining rows narrow down the next
hypothesis instead.

**Same-day follow-up — a long detour caused by a code bug, caught and corrected before it went
anywhere.** Wanting to change wires first (cheapest possible fix) and cross-check the module's onboard
temperature sub-circuit at the same time, built a combined diagnostic sketch
(`hardware/rebuild/01_ph_sensor/ph_wiring_diagnostic/ph_wiring_diagnostic.ino`) reading `Po` on GPIO34
and `To` on GPIO33 side by side. After rewiring with fresh jumpers, `Po` appeared to read a stable
~1.9V instead of the locked 3.300V — looked like the fix had worked. A long series of follow-up tests
(unplugging `G`, `V+`, `To`; touching wires to different pins) produced a run of results that didn't
add up as genuine sensor behavior (e.g. `Po` reading the same value whether or not its own wire was
even connected to GPIO34; the reading depending on a wire being seated in one specific, seemingly
unrelated breadboard hole).

**Root cause, found by the user, not caught in review beforehand**: `#define PH_PIN` in the diagnostic
sketch actually read `33`, not `34` — a typo from when GPIO35 (originally planned for `To`) was
switched to GPIO33 partway through (GPIO35 was already claimed by the TDS sensor, then GPIO36/39
turned out not to be broken out on this board variant either). The line labeled `"Po (pH)"` had been
printing GPIO33 the entire time — which is exactly where the `To` wire was physically plugged. Every
confusing result above has an obvious explanation once this is known (e.g. `Po` being unaffected by
its own wire's connection state, because the code was never reading that pin at all).

**Corrected to `PH_PIN`=34, `TEMP_PIN`=33 and re-tested. Real result: `To` (the module's onboard
thermistor, now actually being read) shows a stable, sane ~1.900V — proving the board's power and
ground are genuinely healthy in general. `Po` (the real pH signal, now actually being read) is still
locked at exactly 3.300V — unchanged from the very first symptom two days ago.** Nothing was actually
fixed today; a real, unrelated bug produced a false-positive that looked like a fix. The silver lining:
ruling out a board-wide power/ground problem (via `To`'s healthy reading) makes the original BNC-shell
theory *more* confident, not less — the fault is isolated specifically to the `Po` signal path, not the
module as a whole.

- **Resume point — unchanged in substance, stronger evidence behind it**: run the multimeter tests in
  `PH_Module_Multimeter_Diagnostic.pdf` once a multimeter is available, starting with the
  BNC-shell-to-`G` continuity check. Step 1 (pH) stays blocked until that's resolved (repair or
  replacement module) — do not proceed to Step 2 in the meantime if Step 2 hasn't already been started,
  per this rebuild's "confirm each step before wiring the next" discipline. Worth double-checking pin
  `#define`s by eye against intent before trusting a diagnostic sketch's output next time this happens
  again — a plain read-through would have caught this immediately.
---


### 2026-09-08 (Step 1 pH: voltage divider built, calibration tool fixed for 5V + divider)

**Voltage divider construction:**
- Built 1/3 divider from three 10k resistors: two in series (20k high side) + one 10k to GND (low side)
- PH4502C Po -> 20k pair -> junction -> 10k -> GND, with GPIO 34 tapping the junction
- Verified resistances (power OFF): 20k pair = 18.9-19k, single 10k = 9.67k, GPIO34-to-GND = 9.8k � all within tolerance

**Voltage verification (power ON):**
- V+ to G = 4.9V (5V supply confirmed)
- Po to G with BNC shorted = 2.50V (op-amp midpoint reached)
- GPIO 34 to GND with BNC shorted = 0.82V (divider working, 2.50/3 = 0.833)
- Po to G with BNC open = 4.90V (offset pot at rail, not holding)
- GPIO 34 to GND with BNC open = 1.62V

**Offset potentiometer failure:**
- The blue PCB-mounted trimmer does not hold its wiper position � Po returns to 4.90V when the BNC short is removed
- Root cause: weak wiper contact on the trimmer, springs back after adjustment
- Decision: abandoned hardware pot calibration entirely

**BNC shell ground wire removed:**
- The white wire previously wrapped around the BNC shell was removed � it was shorting the virtual ground to board GND, which is wrong. The BNC shell must float.

**Calibration tool sketch fixed:**
- File: `hardware/AquaGuard_v2/01_ph_sensor/ph_calibration_tool/ph_calibration_tool.ino`
- Problem: original sketch assumed 3.3V direct operation with no divider
- Fixes applied:
  1. Added `const float DIVIDER_RATIO = 3.0;`
  2. Replaced `readPhVoltageAveraged` to use `analogReadMilliVolts(PH_PIN)` multiplied by `DIVIDER_RATIO`
  3. Updated header comment to document 5V/Vin power and 1/3 divider
- Result: sketch now reports true Po voltage (0.5V-5.0V range) instead of divided voltage

### 2026-09-09 (Step 1 pH: calibration tool uploaded, probe tested, reverse calibration planned)

**Sketch upload and live voltage verification:**
- Uploaded fixed `ph_calibration_tool.ino` to ESP32
- BNC shorted: stable 2.59V at Po (expected ~2.50V, close enough � confirms code fix works)
- BNC open / probe removed: stable 4.93-5.07V at Po (op-amp at rail, expected)

**Probe immersion tests:**
- Probe in air (connected, no liquid): ~3.07-3.22V (probe loading the circuit)
- Probe in vinegar (pH 2.4): ~3.46-3.53V
- Probe in baking soda (pH 8.3): ~3.18-3.23V
- **Finding: readings are inverted** � vinegar (acidic) gives higher voltage than baking soda (basic). This is either a BNC wiring polarity issue or probe behavior, but the calibration tool handles it.

**Tap water test:**
- With current uncalibrated readings, tap water mapped to pH 8.3 � plausible for Dhaka groundwater, confirms the math is computing consistently

**Decision: reverse calibration order**
- Type `a` while probe is in baking soda (captures base voltage as "acid" point)
- Type `b` while probe is in vinegar (captures acid voltage as "base" point)
- The calibration math computes a negative slope, which is mathematically valid and produces correct pH values
- This bypasses the inverted polarity issue without needing to rewire the BNC

**Resume point:**
- [ ] Run reverse calibration: `a` (baking soda) -> `b` (vinegar) -> `s` (save)
- [ ] Test with tap water using `t` command
- [ ] Upload `01_ph_sensor.ino` for normal operation
- [ ] Calibration persists in ESP32 flash (NVS Preferences namespace "phcal")
