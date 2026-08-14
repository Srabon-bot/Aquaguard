// ============================================================================
// AquaGuard dashboard — no build step, plain fetch calls.
//
// Talks to FOUR things:
//  1. The flood-risk-classifier service  -> http://127.0.0.1:8000
//  2. The discharge-forecaster service   -> http://127.0.0.1:8001
//  3. Open-Meteo's free current-weather API (no key needed, external)
//  4. Firebase Realtime Database -> live sensor readings + pump control,
//     the same /sensor/*, /pumps/* paths hardware/AquaGuard_v2/AquaGuard_v2.ino
//     reads/writes. Plain REST (fetch), no SDK -- see fbGet/fbPut below.
// ============================================================================

const CLASSIFIER_BASE     = "http://127.0.0.1:8000";
const DISCHARGE_BASE      = "http://127.0.0.1:8001";
const SUSCEPTIBILITY_BASE = "http://127.0.0.1:8002";
const FIREBASE_BASE_URL   = "https://aquasheild-2e2ca-default-rtdb.asia-southeast1.firebasedatabase.app";

async function fbGet(path) {
  const res = await fetch(`${FIREBASE_BASE_URL}/${path}.json`);
  if (!res.ok) throw new Error(`Firebase GET ${path} failed: HTTP ${res.status}`);
  return res.json();
}

async function fbPut(path, value) {
  const res = await fetch(`${FIREBASE_BASE_URL}/${path}.json`, {
    method: "PUT",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(value),
  });
  if (!res.ok) throw new Error(`Firebase PUT ${path} failed: HTTP ${res.status}`);
  return res.json();
}

let currentLocation = null; // { lat, lon, label, station_id | null }
let stationsCache = [];

// Latest results for the CURRENT location, used to compute the combined
// score once both are available -- reset to null whenever the location
// changes (see setLocation()), so a stale score from a previous station
// never gets shown against a new one.
let latestClassifierProba24h = null;
let latestSusceptibilityScore = null;
let latestSusceptibilityBand = null;
let latestDischargeTrend24h = null; // "rising" | "falling" | "steady" | "unknown" | null

// ---------------------------------------------------------------------------
// Theme toggle
// ---------------------------------------------------------------------------
(function initTheme() {
  const saved = localStorage.getItem("aquaguard-theme");
  if (saved) document.documentElement.setAttribute("data-theme", saved);
  updateThemeIcon();
})();

document.getElementById("themeToggle").addEventListener("click", () => {
  const current = document.documentElement.getAttribute("data-theme");
  const next = current === "dark" ? "light" : "dark";
  document.documentElement.setAttribute("data-theme", next);
  localStorage.setItem("aquaguard-theme", next);
  updateThemeIcon();
});

function updateThemeIcon() {
  const isDark = document.documentElement.getAttribute("data-theme") === "dark"
    || (!document.documentElement.getAttribute("data-theme")
        && window.matchMedia("(prefers-color-scheme: dark)").matches);
  document.getElementById("themeIcon").textContent = isDark ? "☀️" : "🌙";
}

// ---------------------------------------------------------------------------
// Station list (populates the dropdown; tries the classifier service first,
// falls back to the discharge service if only that one's running)
// ---------------------------------------------------------------------------
async function loadStations() {
  const select = document.getElementById("stationSelect");
  for (const base of [CLASSIFIER_BASE, DISCHARGE_BASE]) {
    try {
      const res = await fetch(`${base}/stations`);
      if (!res.ok) continue;
      const data = await res.json();
      stationsCache = data.stations;
      select.innerHTML = '<option value="">— choose a station —</option>' +
        stationsCache
          .slice()
          .sort((a, b) => a.name.localeCompare(b.name))
          .map(s => `<option value="${s.station_id}">${s.name} (${s.river})</option>`)
          .join("");
      return;
    } catch (e) {
      // try next base
    }
  }
  select.innerHTML = '<option value="">No model service reachable — start one first</option>';
  setLocationStatus(
    "Couldn't reach either model service to load the station list. " +
    "\"Use my location\" still works. See frontend/README.md to start a service."
  );
}

document.getElementById("stationSelect").addEventListener("change", (e) => {
  const id = e.target.value;
  if (!id) return;
  const station = stationsCache.find(s => s.station_id === id);
  if (!station) return;
  setLocation({ lat: station.lat, lon: station.lon, label: station.name, station_id: station.station_id });
});

// ---------------------------------------------------------------------------
// Geolocation
// ---------------------------------------------------------------------------
document.getElementById("geoBtn").addEventListener("click", () => {
  if (!navigator.geolocation) {
    setLocationStatus("Geolocation isn't available in this browser.");
    return;
  }
  setLocationStatus("Requesting your location…");
  navigator.geolocation.getCurrentPosition(
    (pos) => {
      setLocation({
        lat: pos.coords.latitude,
        lon: pos.coords.longitude,
        label: "Your location",
        station_id: null,
      });
    },
    (err) => setLocationStatus(geoErrorMessage(err)),
    { enableHighAccuracy: false, timeout: 20000 }
  );
});

// Per-error-code messages -- "Timeout expired" in particular is almost
// always the OS's own Location Services being off (Windows: Settings ->
// Privacy & security -> Location), not a bug here or anything to do with
// this site's backend: the browser's in-page permission prompt only grants
// the *website* permission, the OS can still silently block the actual
// position lookup underneath it, which is exactly what times out. Picking
// a station from the dropdown works either way and needs no location
// access at all -- surfaced here explicitly so a stuck user has an
// immediate way forward instead of just seeing an error.
function geoErrorMessage(err) {
  const fallback = "Pick a station from the dropdown instead — no location access needed.";
  if (err.code === err.PERMISSION_DENIED) {
    return `Location permission was denied. ${fallback}`;
  }
  if (err.code === err.TIMEOUT) {
    return `Location timed out — usually means Location Services is turned off at the OS level ` +
      `(not just the browser), or this device has no GPS/WiFi to get a position from. ${fallback}`;
  }
  if (err.code === err.POSITION_UNAVAILABLE) {
    return `Your device couldn't determine a location right now. ${fallback}`;
  }
  return `Couldn't get your location (${err.message}). ${fallback}`;
}

function setLocation(loc) {
  currentLocation = loc;
  setLocationStatus(`Using: ${loc.label} (${loc.lat.toFixed(3)}, ${loc.lon.toFixed(3)})`);
  document.getElementById("runClassifier").disabled = false;
  document.getElementById("runDischarge").disabled = false;
  document.getElementById("runSusceptibility").disabled = false;
  document.getElementById("runAllModels").disabled = false;
  // New location -- any previously-combined score no longer applies to it.
  latestClassifierProba24h = null;
  latestSusceptibilityScore = null;
  latestSusceptibilityBand = null;
  latestDischargeTrend24h = null;
  document.getElementById("combinedRiskWrap").style.display = "none";
  loadWeather(loc.lat, loc.lon);
}

function setLocationStatus(text) {
  document.getElementById("locationStatus").textContent = text;
}

// ---------------------------------------------------------------------------
// Weather (Open-Meteo, free, no key)
// ---------------------------------------------------------------------------
const WEATHER_CODES = {
  0: "Clear sky", 1: "Mainly clear", 2: "Partly cloudy", 3: "Overcast",
  45: "Fog", 48: "Depositing rime fog",
  51: "Light drizzle", 53: "Moderate drizzle", 55: "Dense drizzle",
  61: "Slight rain", 63: "Moderate rain", 65: "Heavy rain",
  66: "Freezing rain", 67: "Heavy freezing rain",
  71: "Slight snow", 73: "Moderate snow", 75: "Heavy snow",
  80: "Slight rain showers", 81: "Moderate rain showers", 82: "Violent rain showers",
  95: "Thunderstorm", 96: "Thunderstorm with hail", 99: "Thunderstorm with heavy hail",
};

async function loadWeather(lat, lon) {
  const body = document.getElementById("weatherBody");
  body.innerHTML = '<div class="empty-state"><span class="spinner"></span>Loading weather…</div>';
  try {
    const url = `https://api.open-meteo.com/v1/forecast?latitude=${lat}&longitude=${lon}` +
      `&current=temperature_2m,relative_humidity_2m,precipitation,weather_code,wind_speed_10m&timezone=auto`;
    const res = await fetch(url);
    if (!res.ok) throw new Error(`Open-Meteo returned ${res.status}`);
    const data = await res.json();
    const c = data.current;
    const desc = WEATHER_CODES[c.weather_code] ?? `Weather code ${c.weather_code}`;
    body.innerHTML = `
      <div class="weather-grid">
        <div class="weather-item"><span class="w-label">Temperature</span><span class="w-value">${c.temperature_2m}°C</span></div>
        <div class="weather-item"><span class="w-label">Humidity</span><span class="w-value">${c.relative_humidity_2m}%</span></div>
        <div class="weather-item"><span class="w-label">Precipitation</span><span class="w-value">${c.precipitation} mm</span></div>
        <div class="weather-item"><span class="w-label">Wind</span><span class="w-value">${c.wind_speed_10m} km/h</span></div>
        <div class="weather-desc">${desc}</div>
      </div>`;
  } catch (e) {
    body.innerHTML = `<div class="error-box">Couldn't load weather: ${e.message}</div>`;
  }
}

// ---------------------------------------------------------------------------
// Flood risk classifier
// ---------------------------------------------------------------------------
const RISK_STATUS = { low: "good", moderate: "warning", high: "critical" };
const RISK_ICON = { low: "✓", moderate: "!", high: "▲" };

async function runClassifierAnalysis() {
  if (!currentLocation) return;
  const out = document.getElementById("classifierResult");
  out.innerHTML = '<div class="empty-state"><span class="spinner"></span>Running classifier…</div>';
  try {
    const data = await callModel(CLASSIFIER_BASE, currentLocation);
    const rows = data.horizons.map(h => {
      const status = RISK_STATUS[h.risk_level] ?? "warning";
      return `
        <div class="horizon-row">
          <span class="horizon-label">${h.horizon}</span>
          <span class="status-chip ${status}">${RISK_ICON[h.risk_level] ?? "?"} ${h.risk_level.toUpperCase()}</span>
          <span class="horizon-detail">probability ${(h.probability * 100).toFixed(0)}%</span>
        </div>`;
    }).join("");
    const reasoning = (data.reasoning || []).map(r => `<li>${escapeHtml(r)}</li>`).join("");
    out.innerHTML = `
      <p style="margin:4px 0 8px;font-size:0.85rem;color:var(--text-secondary)">
        Nearest station: <strong>${escapeHtml(data.station_name)}</strong>
        (${data.station_distance_km} km away, ${escapeHtml(data.basin)} basin)
      </p>
      ${rows}
      ${reasoning ? `<ul class="reasoning-list">${reasoning}</ul>` : ""}
      <p class="honesty-note">
        At this model's operating threshold, roughly 14–18% of "HIGH" alerts are followed by an
        actual flood — it's deliberately tuned to catch 85% of real floods even at the cost of
        more false alarms. Treat this as an early-warning signal, not a certainty.
      </p>`;
    const h24 = data.horizons.find(h => h.horizon === "24h");
    latestClassifierProba24h = h24 ? h24.probability : null;
    maybeRenderCombinedRisk();
  } catch (e) {
    out.innerHTML = modelErrorHtml(e, "flood-risk-classifier", 8000);
  }
}

document.getElementById("runClassifier").addEventListener("click", runClassifierAnalysis);

// ---------------------------------------------------------------------------
// Discharge forecaster
// ---------------------------------------------------------------------------
const TREND_ARROW = { rising: "↑", falling: "↓", steady: "→", unknown: "?" };

async function runDischargeAnalysis() {
  if (!currentLocation) return;
  const out = document.getElementById("dischargeResult");
  out.innerHTML = '<div class="empty-state"><span class="spinner"></span>Running forecaster…</div>';
  try {
    const data = await callModel(DISCHARGE_BASE, currentLocation);
    const rows = data.forecasts.map(f => `
      <div class="horizon-row">
        <span class="horizon-label">${f.horizon}</span>
        <span class="trend-arrow ${f.trend}">${TREND_ARROW[f.trend] ?? "?"} ${f.trend}</span>
        <span class="horizon-detail">${f.predicted_discharge_m3s.toLocaleString(undefined, { maximumFractionDigits: 0 })} m³/s</span>
      </div>`).join("");
    const current = data.current_discharge_m3s != null
      ? `${data.current_discharge_m3s.toLocaleString(undefined, { maximumFractionDigits: 0 })} m³/s`
      : "unavailable";
    out.innerHTML = `
      <p style="margin:4px 0 8px;font-size:0.85rem;color:var(--text-secondary)">
        Nearest station: <strong>${escapeHtml(data.station_name)}</strong>
        (${data.station_distance_km} km away) — current discharge: <strong>${current}</strong>
      </p>
      ${rows}
      <p class="honesty-note">${escapeHtml(data.note)}</p>`;
    const f24h = data.forecasts.find(f => f.horizon === "24h");
    latestDischargeTrend24h = f24h ? f24h.trend : null;
    maybeRenderCombinedRisk();
  } catch (e) {
    out.innerHTML = modelErrorHtml(e, "discharge-forecaster", 8001);
  }
}

document.getElementById("runDischarge").addEventListener("click", runDischargeAnalysis);

// ---------------------------------------------------------------------------
// Flood susceptibility -- static terrain-based, no forecast horizon. See
// packages/flood-susceptibility/README.md for what this measures and why
// it's a different question from the other two models.
// ---------------------------------------------------------------------------
const SUSCEPTIBILITY_BAND_STATUS = { low: "good", moderate: "warning", high: "serious", very_high: "critical" };
const SUSCEPTIBILITY_BAND_ICON = { low: "✓", moderate: "!", high: "▲", very_high: "▲" };

async function runSusceptibilityAnalysis() {
  if (!currentLocation) return;
  const out = document.getElementById("susceptibilityResult");
  out.innerHTML = '<div class="empty-state"><span class="spinner"></span>Running susceptibility model…</div>';
  try {
    const data = await callModel(SUSCEPTIBILITY_BASE, currentLocation);
    const status = SUSCEPTIBILITY_BAND_STATUS[data.susceptibility_band] ?? "warning";
    const bandLabel = data.susceptibility_band.replace("_", " ").toUpperCase();
    const factors = (data.top_factors || []).map(f => f.replace(/_/g, " ")).join(", ");
    out.innerHTML = `
      <p style="margin:4px 0 8px;font-size:0.85rem;color:var(--text-secondary)">
        Nearest station: <strong>${escapeHtml(data.station_name)}</strong>
        (${data.station_distance_km} km away, ${escapeHtml(data.basin)} basin)
      </p>
      <div class="horizon-row">
        <span class="horizon-label">terrain</span>
        <span class="status-chip ${status}">${SUSCEPTIBILITY_BAND_ICON[data.susceptibility_band] ?? "?"} ${bandLabel}</span>
        <span class="horizon-detail">mean ${(data.susceptibility_score * 100).toFixed(0)}% · peak nearby ${(data.peak_score * 100).toFixed(0)}%</span>
      </div>
      ${factors ? `<p style="margin:8px 0 0;font-size:0.82rem;color:var(--text-muted)">Top factors: ${escapeHtml(factors)}</p>` : ""}
      <p class="honesty-note">${escapeHtml(data.honesty_note)}</p>`;
    latestSusceptibilityScore = data.susceptibility_score;
    latestSusceptibilityBand = data.susceptibility_band;
    maybeRenderCombinedRisk();
  } catch (e) {
    out.innerHTML = modelErrorHtml(e, "flood-susceptibility", 8002);
  }
}

document.getElementById("runSusceptibility").addEventListener("click", runSusceptibilityAnalysis);

// ---------------------------------------------------------------------------
// Run all 3 models together (one-button analysis) -- so the full pipeline
// summary below always completes without needing 3 separate manual clicks.
// The 3 analysis functions are independent (each hits its own local
// service), so they run in parallel; each already updates its own
// latest*/DOM state and calls maybeRenderCombinedRisk() on completion, so
// whichever finishes last naturally renders the complete summary.
// ---------------------------------------------------------------------------
document.getElementById("runAllModels").addEventListener("click", async () => {
  if (!currentLocation) return;
  const btn = document.getElementById("runAllModels");
  const originalText = btn.textContent;
  btn.disabled = true;
  btn.textContent = "Running all 3 models…";
  try {
    await Promise.all([
      runClassifierAnalysis(),
      runDischargeAnalysis(),
      runSusceptibilityAnalysis(),
    ]);
  } finally {
    btn.disabled = false;
    btn.textContent = originalText;
  }
});

// ---------------------------------------------------------------------------
// Pipeline result -- what all 3 models feed into.
//
// Deliberately NOT a single LOW/MODERATE/HIGH/SEVERE word: that collapses
// three independent, genuinely different pieces of evidence into one
// pre-judged label, hiding exactly the information a user would want to
// weigh for themselves (e.g. "modest live risk, but on ground that rarely
// floods" reads very differently than "high live risk on ground that
// floods often" even if a single blended score happened to land the same).
// Instead this states each fact plainly and lets the reader draw their own
// conclusion -- see buildFactualSummary().
//
// The classifier's own 24h probability already has the discharge
// forecaster's prediction baked in server-side (the "cascade" feature, see
// packages/flood-risk-classifier/flood_model.py). The susceptibility score
// is reported separately, not pre-multiplied into one number, for the same
// reason -- see packages/flood-susceptibility/README.md "Combining with
// the other two models" for the formula still shown as supplementary
// detail below the summary, for anyone who wants the arithmetic.
// ---------------------------------------------------------------------------

const DISCHARGE_TREND_PHRASE = {
  rising: "is currently rising",
  falling: "is currently falling",
  steady: "is currently steady",
};
const SUSCEPTIBILITY_FREQUENCY = {
  very_high: "very often",
  high: "often",
  moderate: "sometimes",
  low: "rarely",
};

function buildFactualSummary() {
  const probaPct = Math.round(latestClassifierProba24h * 100);
  const sentence1 = `Based on current rainfall, soil moisture, and river discharge, the flood model ` +
    `estimates a ${probaPct}% chance of flooding here within the next 24 hours.`;

  const trendPhrase = DISCHARGE_TREND_PHRASE[latestDischargeTrend24h];
  const sentence2 = trendPhrase
    ? `River discharge ${trendPhrase}.`
    : `River discharge trend is not available for this location.`;

  const frequency = SUSCEPTIBILITY_FREQUENCY[latestSusceptibilityBand] ?? "sometimes";
  const suscPct = Math.round(latestSusceptibilityScore * 100);
  const sentence3 = `This location's terrain has ${frequency} been associated with flooding in the ` +
    `historical satellite record (susceptibility score ${suscPct}%).`;

  return [sentence1, sentence2, sentence3];
}

function maybeRenderCombinedRisk() {
  const wrap = document.getElementById("combinedRiskWrap");
  if (latestClassifierProba24h == null || latestSusceptibilityScore == null) {
    wrap.style.display = "none";
    return;
  }
  const modulator = 0.5 + 0.5 * latestSusceptibilityScore;
  const combined = Math.min(1, latestClassifierProba24h * modulator);
  const sentences = buildFactualSummary();

  const out = document.getElementById("combinedRiskResult");
  out.innerHTML = `
    <p class="pipeline-summary">${sentences.map(escapeHtml).join(" ")}</p>
    <div class="combined-score-row">
      <span class="combined-score-value">${(combined * 100).toFixed(0)}%</span>
      <span class="combined-score-detail">
        combined estimate: ${(latestClassifierProba24h * 100).toFixed(0)}% classifier (24h, already informed
        by the discharge forecast) × ${modulator.toFixed(2)} susceptibility modulator
        (${(latestSusceptibilityScore * 100).toFixed(0)}% terrain score) — shown for reference, not as a verdict
      </span>
    </div>`;
  wrap.style.display = "block";
}

async function callModel(base, loc) {
  const params = loc.station_id
    ? `station_id=${encodeURIComponent(loc.station_id)}`
    : `lat=${loc.lat}&lon=${loc.lon}`;
  const res = await fetch(`${base}/predict?${params}`);
  if (!res.ok) {
    const body = await res.json().catch(() => ({}));
    throw new Error(body.detail || `HTTP ${res.status}`);
  }
  return res.json();
}

function modelErrorHtml(e, pkgName, port) {
  const looksUnreachable = e instanceof TypeError; // fetch throws TypeError on network failure
  if (looksUnreachable) {
    return `<div class="error-box">
      Couldn't reach the ${pkgName} service on port ${port}. Start it first:
      <br><code>cd packages/${pkgName} && uvicorn main:app --port ${port}</code>
      <br>See <code>packages/${pkgName}/README.md</code> for full setup.
    </div>`;
  }
  return `<div class="error-box">Error: ${escapeHtml(e.message)}</div>`;
}

function escapeHtml(str) {
  const div = document.createElement("div");
  div.textContent = str;
  return div.innerHTML;
}

// ---------------------------------------------------------------------------
// Pump control — REAL. Writes to /pumps/pump1 and /pumps/pump2, the same
// paths hardware/AquaGuard_v2/AquaGuard_v2.ino's controlPumps() reads and
// drives the relay from. setPump() updates the UI immediately (optimistic —
// feels instant on click) and also fires the Firebase write; the live poller
// further down (pollSensorsAndPumps()) reconciles the UI to whatever
// Firebase actually reports every few seconds, so it stays correct even if
// a write fails, drops, or the pump state changes from something other than
// this page (e.g. a second browser tab).
// ---------------------------------------------------------------------------
const pumpState = { 1: false, 2: false };
let cycleTimer = null;

function setPump(num, isOn, { write = true } = {}) {
  pumpState[num] = isOn;
  const chip = document.getElementById(`pump${num}Status`);
  const btn = document.getElementById(`pump${num}Toggle`);
  chip.className = `status-chip ${isOn ? "good on-pulse" : "muted"}`;
  chip.innerHTML = `<span class="status-dot"></span>${isOn ? "ON" : "OFF"}`;
  btn.textContent = isOn ? "Turn OFF" : "Turn ON";
  // aria-pressed, not role="switch": this is a <button> that performs a
  // toggle action, which is the correct ARIA pattern for that element (a
  // real switch role belongs on checkbox-style inputs, not buttons).
  btn.setAttribute("aria-pressed", String(isOn));

  if (write) {
    fbPut(`pumps/pump${num}`, isOn).catch(e => {
      console.error(`Couldn't write pump${num} state to Firebase:`, e);
    });
  }
}

function setManualPumpControlsEnabled(enabled) {
  document.getElementById("pump1Toggle").disabled = !enabled;
  document.getElementById("pump2Toggle").disabled = !enabled;
}

[1, 2].forEach((num) => {
  document.getElementById(`pump${num}Toggle`).addEventListener("click", () => {
    setPump(num, !pumpState[num]);
  });
});

// --- Water cycle: timed drain, then timed refill, automatically ---
function setCycleUI({ running, phase, progressPct, statusText }) {
  document.getElementById("startCycle").style.display = running ? "none" : "inline-flex";
  document.getElementById("cancelCycle").style.display = running ? "inline-flex" : "none";
  document.getElementById("cycleProgressWrap").style.display = running ? "block" : "none";
  const bar = document.getElementById("cycleProgressBar");
  bar.style.width = `${progressPct ?? 0}%`;
  bar.classList.toggle("phase-refill", phase === "refill");
  document.getElementById("cycleStatus").textContent = statusText;
  setManualPumpControlsEnabled(!running);
}

function runPhase(pumpNum, otherPumpNum, durationSec, phaseLabel, phaseClass, onDone) {
  setPump(otherPumpNum, false);
  setPump(pumpNum, true);
  const totalMs = durationSec * 1000;
  const startedAt = Date.now();

  cycleTimer = setInterval(() => {
    const elapsed = Date.now() - startedAt;
    const remaining = Math.max(0, totalMs - elapsed);
    const pct = Math.min(100, (elapsed / totalMs) * 100);
    setCycleUI({
      running: true,
      phase: phaseClass,
      progressPct: pct,
      statusText: `${phaseLabel}… ${Math.ceil(remaining / 1000)}s remaining`,
    });
    if (elapsed >= totalMs) {
      clearInterval(cycleTimer);
      setPump(pumpNum, false);
      onDone();
    }
  }, 200);
}

document.getElementById("startCycle").addEventListener("click", () => {
  const drainSec = Math.max(1, parseInt(document.getElementById("drainSeconds").value, 10) || 30);
  const refillSec = Math.max(1, parseInt(document.getElementById("refillSeconds").value, 10) || 30);

  setCycleUI({ running: true, phase: "drain", progressPct: 0, statusText: `Draining… ${drainSec}s remaining` });

  runPhase(1, 2, drainSec, "Draining", "drain", () => {
    runPhase(2, 1, refillSec, "Refilling", "refill", () => {
      setCycleUI({ running: false, phase: null, progressPct: 0, statusText: "Cycle complete ✓" });
    });
  });
});

document.getElementById("cancelCycle").addEventListener("click", () => {
  if (cycleTimer) clearInterval(cycleTimer);
  cycleTimer = null;
  setPump(1, false);
  setPump(2, false);
  setCycleUI({ running: false, phase: null, progressPct: 0, statusText: "Cancelled." });
});

// ---------------------------------------------------------------------------
// Live sensor data — polled from Firebase (/sensor/*), the same path
// hardware/AquaGuard_v2/AquaGuard_v2.ino publishes to every ~1.5s.
// ---------------------------------------------------------------------------
// TANK_HEIGHT_CM is still an ASSUMED placeholder, not a measured constant --
// the firmware currently publishes /sensor/waterLevel as raw ultrasonic
// distance (sensor-to-water-surface, smaller = more water), not yet
// converted to "cm of water" (see AquaGuard_v2.ino's own header comment,
// "STILL NOT included"). The fill-percentage math below divides by this
// constant as if waterLevel were already water depth, which is only
// correct once that conversion is built and this constant is set to the
// real measured sensor-mount height. Until then, treat the tank fill
// percentage/visual as approximate, not calibrated -- the 4 sensor tiles
// above it (pH/TDS/temp/level) are real regardless.
const TANK_HEIGHT_CM = 60;

let sensorPollFailures = 0;

// ---------------------------------------------------------------------------
// Sensor thresholds — one source of truth for the gauge ring color, the tile
// status chip, and the alert banner, so "warning" or "critical" always means
// the same thing everywhere on this page. `min`/`max` set the full range the
// gauge ring sweeps; `good`/`warn` are inclusive bands within that range.
// Anything outside `warn` is critical. These are real aquaculture-safe
// ranges (pH/TDS/temperature) except `level`, which inherits the same
// TANK_HEIGHT_CM caveat noted above -- not calibrated to a real measured
// tank depth yet.
// ---------------------------------------------------------------------------
const SENSOR_CONFIG = {
  ph:    { label: "pH",  min: 0, max: 14,          good: [6.5, 8.5], warn: [6.45, 8.55], format: v => v.toFixed(2) },
  tds:   { label: "TDS", min: 0, max: 1000,        good: [0, 500],   warn: [0, 560],     format: v => `${Math.round(v)}` },
  temp:  { label: "Temperature", min: 0, max: 40,  good: [20, 30],   warn: [19, 31],     format: v => v.toFixed(1) },
  level: { label: "Water level", min: 0, max: TANK_HEIGHT_CM, good: [20, 55], warn: [10, TANK_HEIGHT_CM], format: v => v.toFixed(1) },
};
const SPARKLINE_LEN = 30;
const sensorHistory = { ph: [], tds: [], temp: [], level: [] };

function classifySensor(key, value) {
  const { good, warn } = SENSOR_CONFIG[key];
  if (value >= good[0] && value <= good[1]) return "good";
  if (value >= warn[0] && value <= warn[1]) return "warning";
  return "critical";
}

const CHIP_TEXT = { good: ["✓", "OK"], warning: ["!", "WARN"], critical: ["▲", "ALERT"] };

function renderSensorTile(key, value) {
  const cfg = SENSOR_CONFIG[key];

  // pH in particular is legitimately absent from Firebase until the probe
  // has been calibrated at least once (AquaGuard_v2.ino only ever writes
  // /sensor/ph after a successful calibration) -- show that honestly
  // instead of a fabricated number or a silent gap.
  if (value == null || Number.isNaN(value)) {
    document.getElementById(`tile-${key}`).textContent = key === "ph" ? "—" : "—";
    const chip = document.getElementById(`chip-${key}`);
    chip.className = "status-chip muted tile-chip";
    chip.innerHTML = `<span class="status-dot"></span>${key === "ph" ? "NOT CALIBRATED" : "NO DATA"}`;
    return null;
  }

  const status = classifySensor(key, value);

  document.getElementById(`tile-${key}`).textContent = cfg.format(value);

  const pct = Math.max(0, Math.min(100, ((value - cfg.min) / (cfg.max - cfg.min)) * 100));
  const ring = document.getElementById(`gauge-${key}`);
  ring.style.setProperty("--gauge-pct", pct.toFixed(1));
  ring.style.setProperty("--gauge-color", `var(--status-${status})`);

  const chip = document.getElementById(`chip-${key}`);
  const [icon, text] = CHIP_TEXT[status];
  chip.className = `status-chip ${status} tile-chip`;
  chip.innerHTML = `<span class="status-dot"></span>${icon} ${text}`;

  const hist = sensorHistory[key];
  hist.push(value);
  if (hist.length > SPARKLINE_LEN) hist.shift();
  const lo = Math.min(...hist), hi = Math.max(...hist);
  const span = hi - lo || 1; // avoid /0 before enough history varies
  const points = hist
    .map((v, i) => {
      const x = (i / Math.max(1, hist.length - 1)) * 100;
      const y = 26 - ((v - lo) / span) * 24; // invert: higher value -> higher on screen
      return `${x.toFixed(1)},${y.toFixed(1)}`;
    })
    .join(" ");
  document.querySelector(`#spark-${key} polyline`).setAttribute("points", points);

  return status;
}

function updateSensorAlertBanner(statuses) {
  const banner = document.getElementById("sensorAlertBanner");
  const critical = Object.entries(statuses).filter(([, s]) => s === "critical").map(([k]) => SENSOR_CONFIG[k].label);
  const warning = Object.entries(statuses).filter(([, s]) => s === "warning").map(([k]) => SENSOR_CONFIG[k].label);

  if (critical.length) {
    banner.className = "alert-banner critical";
    banner.textContent = `▲ ${critical.join(", ")} out of safe range — check the tank now.`;
    banner.style.display = "flex";
  } else if (warning.length) {
    banner.className = "alert-banner warning";
    banner.textContent = `! ${warning.join(", ")} approaching the edge of the safe range.`;
    banner.style.display = "flex";
  } else {
    banner.style.display = "none";
  }
}

async function pollSensorsAndPumps() {
  try {
    const [sensor, pumps] = await Promise.all([fbGet("sensor"), fbGet("pumps")]);
    sensorPollFailures = 0;

    updateSensorAlertBanner({
      ph: renderSensorTile("ph", sensor?.ph),
      tds: renderSensorTile("tds", sensor?.tds),
      temp: renderSensorTile("temp", sensor?.temp),
      level: renderSensorTile("level", sensor?.waterLevel),
    });

    if (typeof sensor?.waterLevel === "number") {
      const fillPct = Math.max(0, Math.min(100, (sensor.waterLevel / TANK_HEIGHT_CM) * 100));
      document.getElementById("tankLevelPct").textContent = `${fillPct.toFixed(0)}%`;
      const waterRect = document.getElementById("tankWater");
      const tankTop = 8, tankBottom = 152, tankFullHeight = tankBottom - tankTop;
      const waterHeight = (fillPct / 100) * tankFullHeight;
      waterRect.setAttribute("y", tankBottom - waterHeight);
      waterRect.setAttribute("height", waterHeight);
    }

    // Reconcile pump chips/buttons to whatever Firebase actually reports --
    // but only when a local water-cycle animation isn't actively driving
    // them (cycleTimer set), so this poll doesn't visually fight with that
    // timer's own in-progress phase.
    if (!cycleTimer && pumps) {
      if (typeof pumps.pump1 === "boolean") setPump(1, pumps.pump1, { write: false });
      if (typeof pumps.pump2 === "boolean") setPump(2, pumps.pump2, { write: false });
    }
  } catch (e) {
    sensorPollFailures += 1;
    if (sensorPollFailures === 1) {
      // Only surface this on the first failure, not every failed poll --
      // avoids flickering an error state between two otherwise-fine reads
      // if a single request happens to drop.
      console.error("Couldn't reach Firebase for live sensor/pump data:", e);
    }
  }
}

// ---------------------------------------------------------------------------
// Boot
// ---------------------------------------------------------------------------
loadStations();
pollSensorsAndPumps();
setInterval(pollSensorsAndPumps, 3000);
window.matchMedia("(prefers-color-scheme: dark)").addEventListener("change", updateThemeIcon);
