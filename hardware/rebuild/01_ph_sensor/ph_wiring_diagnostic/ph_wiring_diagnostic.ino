// ============================================================================
// AquaGuard rebuild -- pH module WIRING DIAGNOSTIC (Po + To together)
// ============================================================================
// NOT the normal-use sketch and NOT the calibration tool -- this is a
// throwaway diagnostic to help isolate a suspected bad ground joint on the
// pH module (see hardware/HARDWARE_LOG.md 2026-08-15 entry and
// hardware/PH_MODULE_MULTIMETER_DIAGNOSTIC.md for the full story).
//
// Reads BOTH of the module's analog outputs at once:
//   Po (the actual pH signal) -> ESP32 GPIO34
//   To (the module's optional onboard temperature-probe input, normally
//       unused by this project) -> ESP32 GPIO33 -- GPIO35 is already used
//       by the TDS sensor (Step 4 of this rebuild) so it's skipped here,
//       and GPIO36/39 aren't broken out on every ESP32 board variant (some
//       30-pin boards omit them), so GPIO33 is used instead: a normal I/O
//       pin with an ADC1 channel, present on effectively every ESP32 dev
//       board, not used anywhere else in this project. Unlike GPIO34/35,
//       GPIO33 does have internal pull resistors and isn't "input-only" --
//       doesn't matter here since it's only ever being read, never driven,
//       and the module's own output still can't exceed the 3.3V it's
//       powered from either way
//
// WHY READ BOTH: if Po is stuck at 3.3V but To reads something that moves/
// looks sane, that means the rest of the board's ground plane is fine and
// the fault is specific to the path through the BNC connector (supports the
// "broken BNC shell solder joint" theory). If To is ALSO stuck at 3.3V,
// that points to a more general power/ground problem across the whole
// board, not just the BNC connector specifically.
//
// WIRING -- do this with FRESH jumper wires for every connection below, not
// just the new one, since re-wiring with different physical wires is itself
// part of what's being tested:
//   pH module "-"  / "G"  (GND)  -> ESP32 GND
//   pH module "+"  / "V+" (VCC)  -> ESP32 3.3V   <-- NOT 5V
//   pH module "Po" (pH signal)   -> ESP32 GPIO 34
//   pH module "To" (temp probe input, usually unused) -> ESP32 GPIO 33
//   pH module "Do" -> leave unconnected (not used here either)
//
// !! SAFETY: same rule as always -- do NOT power this module from 5V while
// Po/To are wired to GPIO34/GPIO33 -- 3.3V supply keeps the module's
// outputs physically incapable of exceeding what these pins can safely
// take (GPIO34 specifically has no over-voltage protection at all, so this
// matters most for that one, but keep the whole module at 3.3V regardless).
//
// If you don't have a real temperature probe plugged into "To", that's
// fine -- an unconnected/floating input on that pin is expected to read
// *something* (possibly noisy or pinned), the interesting comparison is
// simply whether it behaves differently from Po, not whether its number
// means an actual temperature.
// ============================================================================

#define PH_PIN   34   // Po
#define TEMP_PIN 33   // To

const float VREF    = 3.3;
const float ADC_RES = 4095.0;

// -- "To" temperature estimate: rough, single-point calibration -------------
// This board's onboard temperature sub-circuit (the small bead thermistor
// soldered near the BNC connector) has undocumented component values -- no
// datasheet found gives its series resistor or the NTC's own Beta/nominal
// resistance, unlike Step 3's separate, verified external thermistor. So
// this is NOT a real physics-derived conversion -- it's anchored to ONE real
// data point (a live 'To' voltage paired with an actual room-thermometer
// reading, 2026-08-15) and projected outward using a typical NTC-divider
// slope borrowed from Step 3's known-good circuit as a rough stand-in.
// Treat this as an estimate, not a trustworthy reading -- especially far
// from the ~32C it was anchored at.
//
// TO IMPROVE THIS: take a second real (voltage, true temperature) pair at a
// clearly different temperature (e.g. after the board's sat somewhere
// noticeably warmer or cooler for a while, checked against a real
// thermometer), then replace CAL_VOLTAGE_V/CAL_TEMP_C with a proper 2-point
// line through both pairs -- same idea as the pH probe's own 2-point
// calibration, just not built out into a full interactive tool since this
// pin isn't used by the actual project.
//
// SIGN CHECK: not verified which way this board's divider runs. To check:
// warm the small bead component (visible near the BNC connector) with a
// fingertip and watch 'To (temp)' below -- it should CLIMB as it warms. If
// it drops instead, flip the sign of SLOPE_C_PER_V.
const float CAL_VOLTAGE_V  = 1.900;   // live 'To' voltage at the moment of calibration
const float CAL_TEMP_C     = 32.0;    // real room temperature at that same moment
const float SLOPE_C_PER_V  = -40.0;   // rough guess, unverified -- see SIGN CHECK above

float readVoltage(int pin, int samples) {
  long sum = 0;
  for (int i = 0; i < samples; i++) {
    sum += analogRead(pin);
    delay(10);
  }
  float avgRaw = (float)sum / samples;
  return avgRaw * (VREF / ADC_RES);
}

float voltageToTempC(float voltage) {
  return CAL_TEMP_C + SLOPE_C_PER_V * (voltage - CAL_VOLTAGE_V);
}

void setup() {
  Serial.begin(115200);
  delay(500);
  Serial.println();
  Serial.println("=== pH module wiring diagnostic: Po (GPIO34) + To (GPIO33) ===");
  Serial.println("Re-wired with fresh jumpers? Watching both pins now.");
  Serial.println("'To' temperature is a ROUGH single-point estimate -- see comments above.");
  Serial.println();
}

void loop() {
  float vPo = readVoltage(PH_PIN, 30);
  float vTo = readVoltage(TEMP_PIN, 30);
  float tempC = voltageToTempC(vTo);

  Serial.print("Po (pH):   ");
  Serial.print(vPo, 3);
  Serial.print(" V      To (temp): ~");
  Serial.print(tempC, 1);
  Serial.print(" C  (");
  Serial.print(vTo, 3);
  Serial.println(" V)");

  delay(700);
}
