# Step 2 of 7 — Ultrasonic sensor (water level)

Second device in the rebuild. No calibration chemicals needed for this one — just a tape
measure or ruler to sanity-check the numbers.

---

## Part 1 — Wiring

| HC-SR04 pin | Connects to |
|---|---|
| VCC | ESP32 **5V** (this sensor needs 5V, not 3.3V, to work reliably) |
| GND | ESP32 **GND** |
| TRIG | ESP32 **GPIO 5** |
| ECHO | ESP32 **GPIO 18** — **through a voltage divider**, not directly |

### ⚠️ Why the voltage divider on ECHO

The HC-SR04's `ECHO` pin outputs a **5V** pulse, but ESP32 GPIOs only tolerate **3.3V**.
Wiring `ECHO` straight to `GPIO18` risks damaging that pin over time. Build this small divider
between them:

```
ECHO ---[1kΩ]---+--- GPIO18
                 |
               [2kΩ]
                 |
                GND
```

One leg of a 1kΩ resistor goes to `ECHO`; the other leg joins both `GPIO18` and one leg of a
2kΩ resistor; the 2kΩ resistor's other leg goes to `GND`. That junction (between the two
resistors) is what connects to `GPIO18` — it sits at roughly 3.3V when `ECHO` is driving 5V.

---

## Part 2 — Running the test

1. Wire the sensor as above.
2. Open `02_ultrasonic.ino` in the Arduino IDE (board: **ESP32 Dev Module**, correct port —
   same setup as Step 1) and upload it.
3. Open the Serial Monitor, baud rate **115200**.
4. You should see a `Distance: __ cm` line appear roughly once per second.

## Part 3 — Sanity check (instead of chemical calibration)

Ultrasonic sensors don't need the kind of calibration a pH probe does — they work directly off
the speed of sound, which is fixed. Instead, just confirm the numbers are trustworthy:

1. Hold a flat object (a book works well) directly in front of the sensor at a **known**
   distance — measure it with a ruler or tape measure, e.g. exactly 30 cm.
2. Compare to what the Serial Monitor reports. It should be within a centimeter or two of your
   measured distance.
3. Repeat at a second distance (e.g. 10 cm and 100 cm) to confirm it tracks correctly across the
   range you actually care about (whatever your aquarium/pond depth will be).
4. Move the object further away until you see `No echo received` — that's the sensor's range
   limit (~4–5 m for this sensor), or a sign the object is angled away from it.

### Mounting note for later

When this gets mounted over the aquarium/pond for real, **point it straight down at the water
surface**, not at an angle. Ultrasonic sensors rely on the echo bouncing straight back — an
angled sensor reflects sound away from the receiver and reports inflated or missing readings.
This isn't testable on a breadboard, just something to get right when it's actually mounted.

### If readings are noisy/jumpy

A little jitter (±0.5 cm) between readings is normal. If it's wildly inconsistent:
- Confirm the divider resistors are the right way around (1kΩ from ECHO, 2kΩ to GND — swapping
  them changes the voltage ratio and can make ECHO unreliable).
- Make sure nothing else is very close to the sensor's field of view — HC-SR04 has a fairly wide
  detection cone (~15°) and can pick up unintended nearby objects/walls.

---

Once this reads consistently and matches your ruler measurements, this sensor is done — move on
to Step 3 (thermistor) in `hardware/rebuild/03_thermistor/` (to be created when you're ready).
