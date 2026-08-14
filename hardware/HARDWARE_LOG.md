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
6. **Servo — not yet built.**
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
