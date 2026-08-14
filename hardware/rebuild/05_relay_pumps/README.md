# Step 5 of 7 — Relay module + 2 pumps ("2 motors")

Fifth device in the rebuild, and the first one involving real current draw — go carefully
through this one in two stages: **relay alone first, then real pumps.**

---

## Part 1 — Wiring the relay (no pumps yet)

| Relay module pin | Connects to |
|---|---|
| VCC | ESP32 **5V** (most relay modules need 5V to reliably switch, even with a 3.3V trigger signal) |
| GND | ESP32 **GND** |
| IN1 | ESP32 **GPIO 25** (pump/motor 1) |
| IN2 | ESP32 **GPIO 26** (pump/motor 2) |

**Do not connect anything to the relay's COM/NO/NC output terminals yet.** This first stage only
tests that the ESP32 can control the relay board itself.

### Running the test

1. Upload `05_relay_pumps.ino`.
2. Open Serial Monitor, baud **115200**.
3. You should see relay 1 click (and its onboard LED light) for 2 seconds, then off for 2
   seconds, then the same for relay 2, repeating — matching the `Relay 1: ON` / `Relay 1: OFF`
   text in the Serial Monitor.

### If it's backwards

This code assumes **active LOW** (GPIO LOW = relay ON), which is the default for most hobbyist
relay modules. If the relay's LED lights up exactly when the Serial Monitor says `OFF` (and vice
versa), your module is **active HIGH** instead — swap `HIGH`/`LOW` in the two `digitalWrite()`
calls inside `pulseRelay()` and re-upload.

---

## Part 2 — Wiring real pumps (only after Part 1 is confirmed working)

**⚠️ Never connect pump motors directly to the ESP32's 5V or 3.3V pins.** Motors draw far more
current than the ESP32 can safely supply — doing this can brown out or permanently damage the
board. Pumps get their power from their **own external supply** (battery pack or wall adapter
matching the pump's voltage), switched through the relay:

```
Pump power supply (+) -> Relay COM
Relay NO               -> Pump (+)
Pump (-)                -> Pump power supply (-)
```

Use **NO** (Normally Open) so each pump defaults to OFF and only switches on when the relay
activates — matching this sketch's startup state.

**Common ground reminder:** the pump power supply's negative/ground must also connect back to
the ESP32's GND (in addition to the relay's own GND from Part 1) — even though it's a separate
supply. Without a shared ground, the relay may switch unreliably or not at all.

### Testing with real pumps connected

Re-run `05_relay_pumps.ino` (no code changes needed) with pumps now wired through the relay
outputs. You should see/hear the actual pumps turn on and off in the same 2-second pattern as
before. Keep the pump outlets/tubing pointed somewhere safe (a bucket, sink, or dry run with no
water) for this first real test, in case anything's mis-wired.

---

Once both relays reliably switch their pumps on and off on command, this device is done — move
on to Step 6 (servo) in `hardware/rebuild/06_servo/` (to be created when you're ready).
