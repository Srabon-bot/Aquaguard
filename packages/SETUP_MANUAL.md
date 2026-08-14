# Model services — setup manual (all 3 at once)

This folder (`packages/`) is **fully self-contained and portable** — copy the *entire* `packages/`
folder (all 3 service subfolders plus this manual, `requirements.txt`, `run_all.py`,
`start_all.bat`/`start_all.sh`) to any computer with Python installed, and it will work with no
dependency on anything else from the rest of this repository. Every model's trained weights already
live inside its own `models/` subfolder — nothing outside `packages/` is needed.

This guide assumes you are **not** using Claude Code or any AI assistant — every step is a plain
command you type yourself. It gets all 3 services running with **one** virtual environment and
**one** command, instead of repeating setup 3 times.

---

## What's in this folder

| Item | What it is |
|---|---|
| `flood-risk-classifier/` | Flood risk (low/moderate/high) at 24h/48h/72h — its own README has full API docs |
| `discharge-forecaster/` | Predicted river discharge (m³/s) at 24h/48h/72h — its own README has full API docs |
| `flood-susceptibility/` | Terrain-based flood-proneness score — its own README has full API docs |
| `requirements.txt` | One consolidated dependency list covering all 3 services |
| `run_all.py` | Starts all 3 services at once, in one terminal, with labeled output |
| `start_all.bat` / `start_all.sh` | Double-click/no-typing shortcuts for `run_all.py` (Windows / Mac-Linux) |

Each service subfolder is still independently runnable on its own too (see that subfolder's own
README) — this manual is just the fast path for running all three together.

---

## Step 1: Check you have Python

Open a terminal (Command Prompt, PowerShell, or a Mac/Linux terminal) and type:

```
python --version
```

You need Python 3.10 or newer. If that command isn't found, try `python3 --version` instead. If
neither works, install Python from [python.org](https://python.org) first (on Windows, check the box
that says "Add Python to PATH" during installation).

## Step 2: Open a terminal inside this folder

Navigate to wherever you copied the `packages` folder, e.g.:

```
cd path/to/packages
```

Everything below assumes your terminal is sitting inside this exact folder.

## Step 3: Create ONE shared virtual environment

```
python -m venv .venv
```

This creates a `.venv` folder inside `packages/`, shared by all 3 services. You only need to do this
once.

## Step 4: Activate it

**Windows (Command Prompt):**
```
.venv\Scripts\activate.bat
```

**Windows (PowerShell):**
```
.venv\Scripts\Activate.ps1
```

**Mac/Linux:**
```
source .venv/bin/activate
```

You'll know it worked because your terminal prompt now starts with `(.venv)`. Do this every time you
open a new terminal to work with these services — it doesn't stay active permanently.

## Step 5: Install everything, once

```
pip install -r requirements.txt
```

This single install covers all 3 services (takes a minute or two, needs an internet connection).

## Step 6: Start all 3 services

```
python run_all.py
```

Or, without typing a command: double-click `start_all.bat` (Windows) or run `./start_all.sh`
(Mac/Linux) — both just call `run_all.py` using the venv you just set up.

You'll see labeled output like:
```
[classifier] starting on port 8000 ...
[discharge] starting on port 8001 ...
[susceptibility] starting on port 8002 ...

All 3 services starting. Once ready:
  classifier      -> http://127.0.0.1:8000/docs
  discharge       -> http://127.0.0.1:8001/docs
  susceptibility  -> http://127.0.0.1:8002/docs
```

Leave this terminal window open — all 3 keep running as long as this command is active. Press
`Ctrl+C` once to stop all three together (not three separate Ctrl+C's).

## Step 7: Check it's actually working

Open a **new** terminal window (leave `run_all.py` running in the first one) and either:

- Open your browser to any of the 3 `/docs` URLs printed above — each gives an interactive page to
  try that service's API directly, no coding needed.
- Or run these:
  ```
  curl "http://127.0.0.1:8000/predict?station_id=SW90"
  curl "http://127.0.0.1:8001/predict?station_id=SW90"
  curl "http://127.0.0.1:8002/predict?station_id=SW90"
  ```

If each returns a block of JSON (not a connection error), all 3 are working.

---

## Pointing a dashboard at these

If you're running `frontend-glass/` or `frontend/` from this same repo, it already expects exactly
these 3 ports (`8000`/`8001`/`8002`) — no configuration needed, just have `run_all.py` running before
you open the dashboard and click any of the model buttons.

---

## Troubleshooting

- **`ModuleNotFoundError`** — you forgot to activate the virtual environment (Step 4) before running
  `run_all.py`, or forgot Step 5's `pip install`.
- **"expected folder not found"** from `run_all.py`** — you're running the command from somewhere
  other than inside the `packages` folder itself. `cd` into it first (Step 2).
- **One service's `[prefix] exited unexpectedly`** — `run_all.py` deliberately stops the other two
  when this happens (rather than leaving a half-working set running silently). Scroll up in the same
  terminal for that service's own error output just above the "exited unexpectedly" line — it's the
  same error you'd see running that one service standalone (see its own README's Troubleshooting
  section).
- **A `models/` folder is missing inside one service** — make sure you copied the *entire* `packages`
  folder, including every subfolder's `models/` directory, not just the `.py` files.
- **Predictions take a few seconds** — normal; each call fetches fresh live weather/river data from a
  free public API before predicting.
- **`502` errors from a service** — the free weather API it depends on (Open-Meteo) is temporarily
  unreachable. Wait a minute and try again.

For anything specific to one service's API (request/response shape, example calls from JavaScript,
deployment notes), see that service's own `README.md` — this manual only covers getting all three
running together.
