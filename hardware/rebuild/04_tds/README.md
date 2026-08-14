# Step 4 of 7 — TDS sensor (water quality / dissolved solids)

Fourth device in the rebuild. No calibration chemicals needed — just tap water and a pinch of
salt for a sanity check.

---

## Part 1 — Wiring

| TDS module pin | Connects to |
|---|---|
| VCC | ESP32 **3.3V** — **not 5V**, see warning below |
| GND | ESP32 **GND** |
| Signal / AOUT | ESP32 **GPIO 35** |

The probe (two metal prongs) plugs into the module board via its screw terminal or JST
connector — that part doesn't touch the ESP32 directly.

### ⚠️ Why 3.3V and not 5V

Same reasoning as the pH sensor in Step 1: **GPIO35 is an ESP32 input-only pin with no
built-in over-voltage protection.** Most of these TDS modules support a 3.3–5V supply range —
powering it at 3.3V keeps its analog output physically incapable of exceeding what GPIO35 can
safely read.

---

## Part 2 — Running the test

1. Wire the sensor as above.
2. Open `04_tds.ino` in the Arduino IDE (board: **ESP32 Dev Module**, same port as before) and
   upload it.
3. Open the Serial Monitor, baud rate **115200**.
4. You should see a `TDS: __ ppm` line print roughly once per second.

## Part 3 — Sanity check (no chemicals needed)

1. **Dry probe in air**: expect a low, possibly slightly noisy, near-zero reading. (The
   calibration formula can occasionally dip slightly negative at very low voltage — that's a
   cosmetic quirk of the polynomial at the extreme low end, not a sign anything's wrong.)
2. **Dip in plain tap water**: the number should rise and settle within a few seconds into a
   real, non-zero range — most tap water reads somewhere in the tens to low hundreds of ppm,
   varies a lot by region.
3. **Add a pinch of salt to that same water and stir**: the reading should rise noticeably
   further. Salt dissolves into ions that dramatically increase conductivity, which is exactly
   what a TDS sensor measures — a big, obvious jump here is the clearest possible confirmation
   the sensor is wired and working correctly. You don't need an exact number, just a clear
   upward jump.
4. Rinse and dry the probe when done.

### About the numbers themselves

This sketch uses the TDS module manufacturer's published calibration formula (a temperature-
compensated cubic polynomial) — not something derived for this project, so no reason to distrust
the shape of it the way the thermistor formula needed fixing. It assumes a fixed 25°C for
temperature compensation for now, since this sketch tests the TDS sensor in isolation. Once this
and the thermistor (Step 3) are both wired together in the final combined sketch, the real
measured temperature will be used automatically instead.

---

Once this reads near-zero in air, a real number in tap water, and jumps clearly higher with
added salt, this sensor is done — move on to Step 5 (relay + pumps) in
`hardware/rebuild/05_relay_pumps/` (to be created when you're ready).
