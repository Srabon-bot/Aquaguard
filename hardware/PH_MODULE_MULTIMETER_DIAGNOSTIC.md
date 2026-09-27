# pH Module Multimeter Diagnostic

A step-by-step multimeter test procedure to confirm (or rule out) a suspected hardware fault on the
pH-4502C-style sensor module, found during Step 1 calibration testing on 2026-08-15.

---

## 1. What led here (context, so this makes sense on its own)

During calibration testing, the module's analog output (`Po`, read on ESP32 GPIO34) was stuck locked
at exactly 3.300V (the ADC's maximum possible reading) no matter what was tried:

- Dipping the probe in vinegar, baking soda solution, or plain water — no change.
- Turning both blue trim potentiometers through their full range — no change.
- Shorting the BNC connector's center pin directly to its outer shell (a clean, defined "zero input"
  test) — no change, still 3.300V.
- Jumpering GPIO34 directly to the ESP32's own GND (bypassing the module entirely) — read a correct
  ~0.00V, proving the ESP32/GPIO34/breadboard side is completely fine.
- Touching *only* the BNC connector's outer metal shell (not a proper short) made the reading swing
  wildly (1.01V → 0.07V → 3.30V) and lit the board's red threshold LED.

That last result is the key clue: a properly grounded shell shouldn't do anything unusual when
touched. Wild swings from a bare touch is the classic signature of a **floating (not actually
grounded) point** picking up stray signal from your body acting as an antenna. The working theory is a
**broken or cold solder joint between the BNC connector's outer shell and the board's ground plane** —
which would explain every single symptom above, including why shorting the (floating) shell to the
center pin did nothing.

This guide confirms that theory with a multimeter, rather than continuing to guess.

### 1.1 Confirmed from the manufacturer's own spec sheet (added after the fact, evening of 2026-08-15)

This module is a **PH4502C**. Its official retailer spec sheet confirms several things that sharpen
the tests below:

- **Officially rated for 5V DC** (`VCC – 5V DC` in the pinout, "Heating voltage: 5±0.2V" in the specs
  — "heating voltage" is just an awkward translation of "supply voltage"). Confirms this project's
  3.3V wiring is a deliberate, documented safety deviation from the module's own spec, not a mistake.
- **The two trim pots are NOT interchangeable** — this matters, because yesterday's troubleshooting
  turned "both pots" without distinguishing them:
  - **`POT 1` (the one physically nearest the BNC connector) = "Analog reading offset"** — this is the
    one that adjusts `Po`'s baseline/offset. This is the pot the multimeter tests below care about.
  - **`POT 2` (the other one) = "PH limit setting"** — this only sets the threshold for `Do` (the
    digital high/low comparator output, which this project doesn't use). It has no expected effect on
    `Po` at all. So "turning both pots did nothing" from yesterday really only tested `POT 1`
    meaningfully — `POT 2` was never expected to move `Po` in the first place, which isn't a red flag
    on its own.
- **The official calibration procedure matches the YouTube technique used yesterday almost exactly**:
  short the BNC center pin to the shield, then adjust **`POT 1` specifically** until `Po` reads
  **exactly 2.500V** (at the module's rated 5V supply). That confirms 2.500V (at 5V) — and by the same
  proportional-to-supply logic used before, **~1.65V at this project's 3.3V wiring** — really is the
  documented target, not just an estimate from board theory.
- **The two `G` pins are officially different**: `Gnd – Gnd for PH probe` and `Gnd – Gnd for board`
  — separate labels, likely a deliberate noise-isolation ("star grounding") design so the sensitive
  high-impedance probe circuit doesn't pick up digital-side noise. Standard practice (and every
  practical wiring guide found) still ties both to the same common ground point when wiring it up,
  which is what this project already does. **This softens how to read test §3.2 below**: if it doesn't
  beep, that's less alarming than originally written — it could reflect this intentional separation
  (joined only at one distant point on the board, giving a very low but technically nonzero
  resistance) rather than a genuine second fault. Still worth running and reporting the result, just
  don't treat a no-beep there as automatically as serious as a no-beep on §3.1.

Sources: [PH4502C product page, RoboDoc (Bangladesh) — full pinout, specs, and POT1/POT2
descriptions](https://robodocbd.com/product/ph4502c-ph-sensor), general PH4502C wiring/calibration
guides confirming the short-to-shield + adjust-POT1-to-2.500V procedure and the shared-common-ground
convention for the two `Gnd` pins.

---

## 2. Before you start

- **Multimeter mode**: use **continuity/beep mode** (usually a diode/speaker icon on the dial) for
  Part 3, and **DC voltage mode** (usually labeled `V⎓` or `V---`, NOT `V~`) for Part 4. Getting these
  swapped is the most common multimeter mistake — continuity mode on a powered circuit gives
  meaningless readings, and voltage mode won't beep for continuity.
- **Power state**: Parts 3.1–3.4 (continuity checks) should be done with the **ESP32 unplugged/USB
  disconnected** — continuity mode pushes its own small test current through the circuit, and testing
  a powered board in this mode can give misleading readings or (rarely) damage sensitive components.
- **Part 4 (voltage checks)** needs the ESP32 **plugged in and running** the calibration tool sketch
  (`ph_calibration_tool.ino`), same as normal.
- Keep the probe dry and out of any liquid for all of Part 3 and 4.1–4.2 — you're testing the board
  itself, not a live reading.

---

## 3. Continuity tests (ESP32 unplugged)

For each row: touch one multimeter probe to the first point, the other probe to the second point, and
read the result. Polarity doesn't matter for continuity mode.

| # | Probe A | Probe B | Expected on a GOOD board | What it means |
|---|---|---|---|---|
| 3.1 | BNC connector's outer shell (the threaded metal barrel) | Module's `G` pin (either one — try both) | **Continuity (beep / ~0Ω)** | **This is the core test.** If this beeps, the shell is properly grounded and the theory above is wrong — move to Part 4 to look elsewhere. **If this does NOT beep (open circuit)** — confirms the suspected broken ground joint at the BNC connector. This is very likely the root cause. |
| 3.2 | Module's `G` pin labeled "for PH probe" | Module's `G` pin labeled "for board" | Continuity (beep), likely at very low but not necessarily zero resistance | These are officially two separate ground domains (probe vs. board, likely for noise isolation), joined at one common point per standard practice — expect a beep, but a *weak/borderline* one is less alarming here than on §3.1. A clean no-beep still points to a broader ground-plane fault, just hold it a bit more loosely than §3.1's result. |
| 3.3 | BNC connector's **center pin** | Module's `Po` pin | Continuity (beep) | Confirms the signal path from the connector to the output pin is intact (i.e., the amplifier chain itself isn't also physically broken). Expect this to beep — the fault so far points specifically at the *ground* side, not the signal side. |
| 3.4 | ESP32 GND pin (on the board itself, not through any wire) | The breadboard row you have your module's `G` wire plugged into | Continuity (beep) | Sanity check on your own wiring, already effectively proven yesterday by the direct GPIO34-to-GND test, but confirms the specific row/wire you're using now hasn't come loose since. |

**Read 3.1 first.** If it doesn't beep, you've confirmed the diagnosis — skip straight to §5 (repair
options) rather than working through every remaining row. Rows 3.2–3.4 are there to rule out
alternative explanations if 3.1 surprises you by beeping fine.

---

## 4. Voltage tests (ESP32 plugged in, calibration sketch running)

Now switch the multimeter to **DC voltage mode**. Keep the probe dry, out of any liquid, for 4.1–4.2.

| # | Probe A (red/+) | Probe B (black/–, i.e. reference) | Expected on a GOOD board | What it means |
|---|---|---|---|---|
| 4.1 | Module's `V+` pin | Module's `G` pin | **~3.3V** | Confirms real supply power is actually reaching the module. (Already indirectly confirmed yesterday by the V+ unplug test, but good to verify directly at the pins.) If this reads significantly less than 3.3V, the power wiring itself has a problem separate from the ground fault. |
| 4.2 | Module's `Po` pin | Module's `G` pin | Should match the Serial Monitor's `[live] raw voltage:` line at the same moment (currently expected: **~3.3V**, locked) | Cross-checks the module's actual analog output directly, independent of the ESP32's ADC — confirms the ESP32 isn't somehow misreading a perfectly fine signal. If the multimeter reads something *different* from what Serial shows, that would point to a GPIO34/ADC-side issue instead (unlikely given yesterday's direct-ground test, but worth ruling out). |
| 4.4 (optional bonus, if §3.1 turns out to beep and the theory is wrong) | Module's `Po` pin, BNC center pin shorted to shell | Module's `G` pin | **~1.65V** (the manufacturer's official calibration target, 2.500V at their rated 5V supply, scaled to this project's 3.3V wiring) | This is the module's own documented calibration check, from the official spec sheet: with the input shorted, adjusting `POT 1` (the pot nearest the BNC connector — not the other one, which only affects `Do`) should bring this to the target above. Only worth doing if §3.1 already beeped fine and the BNC-ground theory turned out to be wrong; if §3.1 didn't beep, this pot has nothing to reference and won't help. |
| 4.3 | BNC connector's outer shell | Module's `G` pin | Compare to §3.1's continuity result | With power on, if 3.1 showed no continuity, this should read some unstable/wandering voltage (not a clean 0V) — direct confirmation the shell is floating relative to the board's real ground even while powered. |

---

## 5. What the results mean, and what to do next

**If §3.1 has no continuity (the expected outcome given yesterday's symptoms):**

The BNC shell is confirmed disconnected from the board's ground plane — almost certainly a bad or
cold solder joint at the connector's mounting tabs. Two paths from here:

- **If you have a soldering iron**: this is often fixable. Locate where the BNC connector's shell
  tabs meet the board (usually 1–2 larger metal pads soldered directly to the connector's body, visible
  on the same side as the through-hole header pins). Reflow (melt and let re-solidify) the solder on
  those tabs — a cold joint often looks slightly dull/cracked compared to the shinier joints around it.
  Let it cool, then re-run §3.1 to confirm it now beeps before re-testing calibration.
- **If you don't have a soldering iron, or don't want to open it up**: treat this module as
  defective. The fix is a replacement module, not more wiring or software changes — everything on the
  ESP32/breadboard side has already been proven correct. Note the outcome in `HARDWARE_LOG.md` and
  pause Step 1 until a replacement is available (or swap in a spare if you have one).

**If §3.1 DOES show continuity (unexpected — the theory would be wrong):**

Work through §3.2–3.4 and §4.1–4.3 in order to see where the chain actually breaks. Come back with the
full set of readings (which rows beeped/didn't, and the two voltage numbers from 4.1–4.2) and we'll
figure out the next hypothesis from there — don't guess further on your own, since a wrong assumption
at this point could send troubleshooting in the wrong direction again.

---

## 6. Results checklist (fill in as you go)

| Test | Result (beep / no beep, or volts) |
|---|---|
| 3.1 — shell to G | |
| 3.2 — G to G | |
| 3.3 — center pin to Po | |
| 3.4 — ESP32 GND to breadboard row | |
| 4.1 — V+ to G | |
| 4.2 — Po to G (compare to Serial) | |
| 4.3 — shell to G, powered | |
| 4.4 — Po to G, shorted + POT 1 adjusted (only if §3.1 beeped) | |
