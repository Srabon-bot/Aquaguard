// ============================================================================
// AquaGuard dashboard — no build step, plain fetch calls.
//
// Talks to THREE things:
//  1. Bahadurabad Forecast API (new_approach FastAPI) -> http://127.0.0.1:8000
//  2. Open-Meteo's free current-weather API (no key needed, external)
//  3. Firebase Realtime Database -> live sensor readings + pump control,
//     the same /sensor/*, /pumps/* paths hardware/AquaGuard_v2/AquaGuard_v2.ino
//     reads/writes. Plain REST (fetch), no SDK -- see fbGet/fbPut below.
// ============================================================================

const BAHADURABAD_API = "http://127.0.0.1:8000";
const FIREBASE_BASE_URL = "https://aquasheild-2e2ca-default-rtdb.asia-southeast1.firebasedatabase.app";

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
// Station list — hardcoded to Bahadurabad since that is what our new model
// is trained on.  The old classifier / discharge services are removed.
// ---------------------------------------------------------------------------
function loadStations() {
  const select = document.getElementById("stationSelect");
  stationsCache = [{ station_id: "SW46.9L", name: "Bahadurabad", river: "Jamuna / Brahmaputra", lat: 25.1, lon: 89.6 }];
  select.innerHTML =
    '<option value="">— choose a station —</option>' +
    stationsCache.map(s => `<option value="${s.station_id}">${s.name} (${s.river})</option>`).join("");
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

function geoErrorMessage(err) {
  const fallback = "Pick a station from the dropdown instead — no location access needed.";
  if (err.code === err.PERMISSION_DENIED) return `Location permission was denied. ${fallback}`;
  if (err.code === err.TIMEOUT)           return `Location timed out. ${fallback}`;
  if (err.code === err.POSITION_UNAVAILABLE) return `Couldn't determine your location. ${fallback}`;
  return `Couldn't get your location (${err.message}). ${fallback}`;
}

function setLocation(loc) {
  currentLocation = loc;
  setLocationStatus(`Using: ${loc.label} (${loc.lat.toFixed(3)}, ${loc.lon.toFixed(3)})`);
  loadWeather(loc.lat, loc.lon);
  loadBahadurabad(); // trigger forecast on location select
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
// Bahadurabad water-level forecast — calls the new FastAPI
// GET /api/v1/forecast?date=YYYY-MM-DD
// ---------------------------------------------------------------------------

const STATUS_CLASS  = { NORMAL: "good",    WARNING: "warning", DANGER: "critical", EXTREME: "critical" };
const STATUS_EMOJI  = { NORMAL: "✅",      WARNING: "⚠️",     DANGER: "🚨",      EXTREME: "🔴" };
const HORIZON_ICONS = { 1: "📅 +1 day",   3: "📅 +3 days",   7: "📅 +7 days",   14: "📅 +14 days" };
const DANGER_LEVEL  = 19.05;

function bhdShow(id, show) {
  document.getElementById(id).style.display = show ? (id.includes("Cards") || id.includes("Advice") ? "grid" : "block") : "none";
}

async function loadBahadurabad(dateOverride) {
  // show spinner, hide everything else
  bhdShow("bhdLoading",       true);
  bhdShow("bhdError",         false);
  bhdShow("bhdAlertBanner",   false);
  bhdShow("bhdObsRow",        false);
  bhdShow("bhdForecastCards", false);
  bhdShow("bhdChartWrap",     false);
  bhdShow("bhdAdviceCards",   false);

  try {
    const date = dateOverride || new Date().toISOString().slice(0, 10);
    const res  = await fetch(`${BAHADURABAD_API}/api/v1/forecast?date=${date}`);
    if (!res.ok) {
      const body = await res.json().catch(() => ({}));
      throw new Error(body.detail || `API returned HTTP ${res.status}`);
    }
    const data = await res.json();

    bhdShow("bhdLoading", false);
    renderBhdAlert(data);
    renderBhdObsRow(data);
    renderBhdForecastCards(data);
    renderBhdHydrograph(data);
    renderBhdAdvice(data);

  } catch (e) {
    bhdShow("bhdLoading", false);
    const err = document.getElementById("bhdError");
    const isNet = e instanceof TypeError;
    err.innerHTML = isNet
      ? `<strong>🔌 Forecast service offline.</strong><br>
         Start it first: <code>cd new_models/new_approach &amp;&amp; uvicorn api:app --port 8000 --reload</code>`
      : `<strong>Forecast error:</strong> ${escapeHtml(e.message)}`;
    bhdShow("bhdError", true);
  }
}

function renderBhdAlert(data) {
  const banner = document.getElementById("bhdAlertBanner");
  const code   = data.overall_risk_level ?? "NORMAL";
  const cls    = STATUS_CLASS[code] ?? "warning";
  const emoji  = STATUS_EMOJI[code] ?? "⚠️";
  banner.className = `alert-banner ${cls}`;
  const maxPred = data.forecasts ? Math.max(...data.forecasts.map(p => p.predicted_level_m)) : data.current_level_m;
  const aboveDanger = maxPred > DANGER_LEVEL;
  // Use the +1d advice_en for the banner summary
  const advEn = (data.forecasts && data.forecasts[0]) ? data.forecasts[0].advice_en : "";
  banner.innerHTML = `
    <strong>${emoji} ${code}</strong>
    &nbsp;— Current level <strong>${(data.current_level_m ?? 0).toFixed(2)} m</strong>.
    ${aboveDanger
      ? ` Peak forecast <strong>${maxPred.toFixed(2)} m</strong> exceeds danger level (19.05 m).`
      : ` All forecast values within safe range.`}
    &nbsp;<span style="font-size:0.82rem;opacity:0.8">${escapeHtml(advEn)}</span>`;
  bhdShow("bhdAlertBanner", true);
}

function renderBhdObsRow(data) {
  document.getElementById("bhdCurrLevel").textContent = (data.current_level_m ?? 0).toFixed(2);
  document.getElementById("bhdAsOf").textContent      = data.as_of_date ?? "—";
  document.getElementById("bhdDailyChange").textContent = data.daily_change_cm != null
    ? (data.daily_change_cm >= 0 ? "+" : "") + data.daily_change_cm.toFixed(0) : "—";
  document.getElementById("bhdRain").textContent = data.catchment_rain_mm != null
    ? data.catchment_rain_mm.toFixed(1) : "—";
  bhdShow("bhdObsRow", true);
}

function renderBhdForecastCards(data) {
  const container = document.getElementById("bhdForecastCards");
  container.innerHTML = (data.forecasts || []).map(p => {
    const cls   = STATUS_CLASS[p.status_code] ?? "warning";
    const emoji = STATUS_EMOJI[p.status_code] ?? "⚠️";
    const above = p.predicted_level_m > DANGER_LEVEL;
    const diff  = ((p.predicted_level_m - DANGER_LEVEL) * 100).toFixed(0);
    const aboveText = above
      ? `<span class="bhd-above-danger">▲ ${diff} cm above danger</span>`
      : `<span class="bhd-below-danger">✓ ${Math.abs(diff)} cm below danger</span>`;
    return `
      <div class="bhd-forecast-card neu-raised ${cls}">
        <div class="bhd-card-header">
          <span class="bhd-horizon">${HORIZON_ICONS[p.horizon_days] ?? `+${p.horizon_days}d`}</span>
          <span class="status-chip ${cls}"><span class="status-dot"></span>${emoji} ${p.status_code}</span>
        </div>
        <div class="bhd-card-level">${p.predicted_level_m.toFixed(2)}<span class="bhd-unit"> m PWD</span></div>
        ${aboveText}
        <div class="bhd-rmse">Model RMSE: ±0.08–0.31 m</div>
      </div>`;
  }).join("");
  bhdShow("bhdForecastCards", true);
}

function renderBhdHydrograph(data) {
  const svg    = document.getElementById("bhdChart");
  const raw    = data.hydrograph || [];
  if (!raw.length) return;

  // Normalise: API uses level_m + is_forecast (bool); map to {date, wl, type}
  const points = raw.map(p => ({
    date: p.date,
    wl:   p.level_m,
    type: p.is_forecast ? "forecast" : "observed",
  }));

  const W = 800, H = 220, PL = 55, PR = 28, PT = 15, PB = 30;
  const plotW = W - PL - PR, plotH = H - PT - PB;

  const allWl   = points.map(p => p.wl);
  const minWl   = Math.min(...allWl, DANGER_LEVEL) - 0.3;
  const maxWl   = Math.max(...allWl, DANGER_LEVEL) + 0.3;
  const wlRange = maxWl - minWl;

  const xOf = i => PL + (i / (points.length - 1)) * plotW;
  const yOf = v => PT + plotH - ((v - minWl) / wlRange) * plotH;

  // Grid lines
  const ticks = 5;
  let gridLines = "";
  for (let t = 0; t <= ticks; t++) {
    const v = minWl + (wlRange / ticks) * t;
    const y = yOf(v);
    gridLines += `<line x1="${PL}" y1="${y.toFixed(1)}" x2="${W - PR}" y2="${y.toFixed(1)}" stroke="var(--border)" stroke-dasharray="3,3" stroke-width="0.5"/>`;
    gridLines += `<text x="${PL - 4}" y="${y.toFixed(1)}" text-anchor="end" font-size="9" fill="var(--text-muted)" dominant-baseline="middle">${v.toFixed(1)}</text>`;
  }

  // Danger line
  const dy = yOf(DANGER_LEVEL);
  const dangerLine = `<line x1="${PL}" y1="${dy.toFixed(1)}" x2="${W - PR}" y2="${dy.toFixed(1)}" stroke="#ef4444" stroke-width="1.5" stroke-dasharray="6,3"/>
    <text x="${W - PR + 2}" y="${dy.toFixed(1)}" font-size="8" fill="#ef4444" dominant-baseline="middle">DL</text>`;

  const obsPoints = points.filter(p => p.type === "observed");
  const fcPoints  = points.filter(p => p.type === "forecast");
  const obsLast   = obsPoints[obsPoints.length - 1];

  const obsCoords = obsPoints.map((p, i) => `${xOf(i).toFixed(1)},${yOf(p.wl).toFixed(1)}`).join(" ");
  const fcStart   = obsLast ? points.indexOf(obsLast) : obsPoints.length - 1;
  const fcCoords  = [obsLast, ...fcPoints].map((p, i) => {
    const xi = i === 0 ? fcStart : obsPoints.length + i - 1;
    return `${xOf(xi).toFixed(1)},${yOf(p.wl).toFixed(1)}`;
  }).join(" ");

  // X-axis date labels
  const labelStep = Math.max(1, Math.floor(points.length / 8));
  let xLabels = "";
  points.forEach((p, i) => {
    if (i % labelStep !== 0 && i !== points.length - 1) return;
    const label = p.date ? p.date.slice(5) : `d${i}`;
    xLabels += `<text x="${xOf(i).toFixed(1)}" y="${H - 4}" text-anchor="middle" font-size="8" fill="var(--text-muted)">${label}</text>`;
  });

  svg.innerHTML = `
    ${gridLines}
    ${dangerLine}
    <polyline points="${obsCoords}" fill="none" stroke="var(--accent)" stroke-width="2" stroke-linejoin="round"/>
    <polyline points="${fcCoords}"  fill="none" stroke="#f59e0b"       stroke-width="2" stroke-dasharray="6,3" stroke-linejoin="round"/>
    ${obsPoints.map((p, i) => `<circle cx="${xOf(i).toFixed(1)}" cy="${yOf(p.wl).toFixed(1)}" r="3" fill="var(--accent)"/>`).join("")}
    ${fcPoints.map((p, i) => `<circle cx="${xOf(obsPoints.length + i).toFixed(1)}" cy="${yOf(p.wl).toFixed(1)}" r="3.5" fill="#f59e0b" stroke="white" stroke-width="1"/>`).join("")}
    ${xLabels}
  `;
  bhdShow("bhdChartWrap", true);
}

function renderBhdAdvice(data) {
  // Use the +3d horizon for the main advice (best tradeoff of skill & lead time)
  const fc3d  = data.forecasts && data.forecasts.find(f => f.horizon_days === 3);
  const advEn = fc3d ? fc3d.advice_en : (data.forecasts && data.forecasts[0] ? data.forecasts[0].advice_en : "No advice available.");
  const advBn = fc3d ? fc3d.advice_bn : (data.forecasts && data.forecasts[0] ? data.forecasts[0].advice_bn : "");
  const container = document.getElementById("bhdAdviceCards");
  container.innerHTML = `
    <div class="bhd-advice-card neu-flat">
      <div class="bhd-advice-lang">🇬🇧 English Advice (+3 day forecast)</div>
      <p class="bhd-advice-text">${escapeHtml(advEn)}</p>
    </div>
    <div class="bhd-advice-card neu-flat">
      <div class="bhd-advice-lang">🇧🇩 Bengali / বাংলা পরামর্শ (+৩ দিনের পূর্বাভাস)</div>
      <p class="bhd-advice-text bhd-bengali">${escapeHtml(advBn)}</p>
    </div>`;
  bhdShow("bhdAdviceCards", true);
}


document.getElementById("refreshForecast").addEventListener("click", () => loadBahadurabad());

// ---------------------------------------------------------------------------
// Utility
// ---------------------------------------------------------------------------
function escapeHtml(str) {
  const div = document.createElement("div");
  div.textContent = str ?? "";
  return div.innerHTML;
}

// ---------------------------------------------------------------------------
// Pump control — REAL. Writes to /pumps/pump1 and /pumps/pump2, the same
// paths hardware/AquaGuard_v2/AquaGuard_v2.ino's controlPumps() reads and
// drives the relay from.
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
// Pond Water Quality AI (Models 2 & 3)
// ---------------------------------------------------------------------------

async function loadWaterQualityAI(simulateSpike = false) {
  try {
    // 1. Fetch Model 2: TDS Forecast
    const resTds = await fetch(`${BAHADURABAD_API}/api/v1/tds`);
    if (resTds.ok) {
      const tdsData = await resTds.json();
      document.getElementById('tdsCurrValue').textContent = tdsData.current_tds || "--";
      document.getElementById('tdsPredValue').textContent = tdsData.predicted_tds_60min || "--";
      document.getElementById('tdsTrend').textContent = tdsData.trend || "--";
      
      const cardTds = document.getElementById('cardTDSForecast');
      if (tdsData.trend === "INCREASING") {
        cardTds.style.borderLeft = "4px solid var(--status-warning)";
      } else {
        cardTds.style.borderLeft = "4px solid var(--status-good)";
      }
    }

    // 2. Fetch Model 3: Anomaly Detection
    // If simulateSpike is true, we pass extreme parameters to force an anomaly
    let anomalyUrl = `${BAHADURABAD_API}/api/v1/anomaly`;
    if (simulateSpike) {
      anomalyUrl += `?pH=9.5&tds=450&temp=33`;
    }

    const resAnom = await fetch(anomalyUrl);
    if (resAnom.ok) {
      const anomData = await resAnom.json();
      const statusEl = document.getElementById('anomalyStatus');
      const scoreEl = document.getElementById('anomalyScore');
      const msgEl = document.getElementById('anomalyMsg');
      const cardAnom = document.getElementById('cardAnomaly');

      statusEl.textContent = anomData.status || "--";
      scoreEl.textContent = anomData.anomaly_score || "--";
      msgEl.textContent = anomData.message || "--";

      if (anomData.status === "ANOMALY DETECTED") {
        statusEl.style.color = "var(--status-critical)";
        cardAnom.style.borderLeft = "4px solid var(--status-critical)";
      } else {
        statusEl.style.color = "var(--status-good)";
        cardAnom.style.borderLeft = "4px solid var(--status-good)";
      }
    }
  } catch (err) {
    console.error("Failed to load Water Quality AI:", err);
  }
}

document.getElementById('btnTestAnomaly')?.addEventListener('click', () => {
  loadWaterQualityAI(true);
  // Reset back to normal after 5 seconds
  setTimeout(() => loadWaterQualityAI(false), 5000);
});

// ---------------------------------------------------------------------------
// Boot
// ---------------------------------------------------------------------------
loadStations();
pollSensorsAndPumps();
setInterval(pollSensorsAndPumps, 3000);
window.matchMedia("(prefers-color-scheme: dark)").addEventListener("change", updateThemeIcon);
// Load Bahadurabad forecast immediately on page open (no location needed)
loadBahadurabad();
// Load Pond Water Quality AI models
loadWaterQualityAI();
