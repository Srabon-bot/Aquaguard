# Step 6 of 7 — Servo

Sixth device in the rebuild. No calibration needed — just confirm it moves smoothly and doesn't
reset the ESP32 when it starts moving.

---

## Part 1 — Wiring

| Servo wire | Connects to |
|---|---|
| Signal (usually orange/yellow) | ESP32 **GPIO 13** |
| Power (red) | **5V** — not the ESP32's 3.3V, most hobby servos need 5V and more current than that rail supplies |
| Ground (brown/black) | ESP32 **GND** (shared ground, even though power comes from a separate 5V source) |

### ⚠️ If it twitches or resets the ESP32

That's a power problem, not a wiring-position problem. Most small hobby servos draw a brief current
spike when they start moving that a USB-only supply often can't deliver cleanly. Power the servo from
the same external 5V supply the pumps use (see `hardware/rebuild/05_relay_pumps/`), not from the
ESP32 board itself, if you see this.

---

## Part 2 — Running the test

1. Wire the servo as above.
2. Open `06_servo.ino` in the Arduino IDE (board: **ESP32 Dev Module**, correct port) and upload it.
3. Open the Serial Monitor, baud rate **115200**.
4. The servo should sweep smoothly from 0° to 180° and back, repeating, with each reached angle
   printed to Serial.

## Part 3 — Sanity check

No chemical/reference calibration needed here (unlike pH). Just confirm:
- The sweep is smooth, not jittery or stalling partway.
- It reaches the full 0°-180° range, not a truncated portion.
- No ESP32 resets/brownouts when the servo starts moving (see the power warning above if it does).

---

Once this moves smoothly and reliably, this step is done — the last step is Step 7, merging all 6
confirmed-working parts back into one sketch (`hardware/AquaGuard_v2/AquaGuard_v2.ino`, already built,
uses Firebase-triggered movement instead of this automatic sweep).
