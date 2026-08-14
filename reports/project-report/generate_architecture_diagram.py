"""
Generates a one-page system-architecture diagram for the whole-project report
(reports/project-report/PROJECT_REPORT.md) -- pure matplotlib (vector shapes
-> PNG via savefig), same box/arrow convention as
hardware/generate_pump_valve_diagram.py and reports/*/generate_*_assets.py.

Re-run any time the system's shape changes -- this always regenerates from
this script, never hand-edited after the fact.

Usage:
    python generate_architecture_diagram.py
"""

from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch

OUT_PATH = Path(__file__).resolve().parent / "assets" / "architecture_diagram.png"

EDGE = "#2b3a4a"
BOX_STYLE = dict(boxstyle="round,pad=0.35,rounding_size=0.15", linewidth=1.6)

DATA_FILL = "#dbe9f7"
MODEL_FILL = "#fde9c9"
API_FILL = "#e6d9f5"
SITE_FILL = "#d8f0e0"
HW_FILL = "#f7d9d9"
CLOUD_FILL = "#fef3c7"


def box(ax, x, y, w, h, text, fill, fontsize=9.5, weight="bold"):
    ax.add_patch(FancyBboxPatch((x, y), w, h, facecolor=fill, edgecolor=EDGE, **BOX_STYLE))
    ax.text(x + w / 2, y + h / 2, text, ha="center", va="center",
             fontsize=fontsize, fontweight=weight, color="#1a1a1a", linespacing=1.35)


def arrow(ax, x0, y0, x1, y1, label=None, label_dx=0, label_dy=0.28, fontsize=8):
    ax.add_patch(FancyArrowPatch((x0, y0), (x1, y1), arrowstyle="-|>",
                                  mutation_scale=18, linewidth=1.8, color=EDGE))
    if label:
        ax.text((x0 + x1) / 2 + label_dx, (y0 + y1) / 2 + label_dy, label,
                 ha="center", va="bottom", fontsize=fontsize, color="#3a3a3a")


def main():
    fig, ax = plt.subplots(figsize=(11, 9.5))
    ax.set_xlim(0, 11)
    ax.set_ylim(-0.6, 11.6)
    ax.axis("off")
    ax.set_title("AquaGuard — System Architecture", fontsize=15, fontweight="bold",
                  color="#0f4c5c", pad=14)

    # Row 1: free public data sources
    box(ax, 0.3, 9.9, 2.3, 1.1, "Open-Meteo\nrainfall + soil\nmoisture (ERA5)", DATA_FILL)
    box(ax, 2.8, 9.9, 2.3, 1.1, "Open-Meteo\nFlood API\n(GloFAS v4 discharge)", DATA_FILL)
    box(ax, 5.3, 9.9, 2.3, 1.1, "NASA GFMS / DFO /\nGFD / FFWC\n(flood labels, training only)", DATA_FILL)
    box(ax, 7.8, 9.9, 2.9, 1.1, "MERIT Hydro (Earth Engine)\nstatic terrain features\n(elevation, slope, HAND)", DATA_FILL)

    arrow(ax, 1.45, 9.9, 1.45, 8.85)
    arrow(ax, 3.95, 9.9, 3.95, 8.85)
    arrow(ax, 6.45, 9.9, 4.6, 8.85, label="training only", label_dx=1.1, fontsize=7.5)
    arrow(ax, 9.25, 9.9, 5.3, 8.85, label="one-time sample", label_dx=1.6, fontsize=7.5)

    # Row 2: training pipeline -> 3 models
    box(ax, 0.3, 7.75, 5.0, 1.1, "backend/ training pipeline\nfeature engineering (lags, rolling, SWI) + label building",
        MODEL_FILL)
    arrow(ax, 1.6, 7.75, 1.6, 6.75, label="train")
    arrow(ax, 3.0, 7.75, 4.3, 6.75, label="train", label_dx=0.35)
    arrow(ax, 4.6, 7.75, 8.1, 6.75, label="train (offline)", label_dx=1.3)

    box(ax, 0.3, 5.6, 2.5, 1.15, "Flood-risk\nclassifier\n(LightGBM, 3 horizons)", MODEL_FILL)
    box(ax, 3.2, 5.6, 2.5, 1.15, "Discharge\nforecaster\n(LightGBM, 3 horizons)", MODEL_FILL)
    box(ax, 7.0, 5.6, 3.0, 1.15, "Flood susceptibility\n(Random Forest,\nterrain-only, static)", MODEL_FILL)

    # cascade note: placed in the genuinely empty gap between the discharge and
    # susceptibility boxes, not overlaid on top of any box/arrow label
    ax.text(6.35, 6.175, "discharge\nforecaster's own\noutput also feeds\nin as a live\nclassifier feature\n(cascade)",
            ha="center", va="center", fontsize=7.3, color="#3a3a3a", style="italic")

    arrow(ax, 1.55, 5.6, 3.6, 4.35, label="live /predict/risk", label_dx=1.15, label_dy=0.05, fontsize=7.5)
    arrow(ax, 4.45, 5.6, 4.45, 4.35, label="live /predict", label_dy=-0.42, fontsize=7.5)
    arrow(ax, 8.5, 5.6, 6.2, 4.35, label="static lookup", label_dx=-1.05, label_dy=0.05, fontsize=7.5)

    # Row 3: local API layer
    box(ax, 2.3, 3.15, 4.0, 1.1, "packages/ — 3 local FastAPI services\n127.0.0.1:8000 / 8001 / 8002 (run_all.py)",
        API_FILL)

    arrow(ax, 4.3, 3.15, 4.3, 2.05, label="fetch() from browser", fontsize=7.5)

    # Row 4: dashboard
    box(ax, 1.6, 0.9, 5.4, 1.0, "Dashboard (frontend-glass / frontend)\nstatic HTML/JS, hosted free on Vercel",
        SITE_FILL)

    # Right side: hardware + Firebase, parallel track
    box(ax, 7.6, 3.15, 3.1, 1.1, "AquaGuard_v2 ESP32 firmware\n7 sensors + 2 pumps + servo",
        HW_FILL)
    box(ax, 7.6, 0.9, 3.1, 1.0, "Firebase Realtime Database\n(free tier, scoped rules)", CLOUD_FILL)

    arrow(ax, 9.15, 3.15, 9.15, 1.9, label="writes /sensor, /pumps", fontsize=7.5)
    arrow(ax, 7.6, 1.4, 7.0, 1.4, label="reads/writes,\npolled every 3s", fontsize=7, label_dx=-0.55, label_dy=0.0)

    fig.text(0.5, 0.01,
              "Solid arrows = live, running today.  Dotted = designed and wired, pending real ESP32 flash.\n"
              "Blue boxes = free/no-key public data, used at training or lookup time only, never called live per request.",
              ha="center", fontsize=8, color="#555")

    fig.tight_layout(rect=[0, 0.035, 1, 1])
    # dpi=100, not higher: PyMuPDF's Story engine embeds <img> content as a raw
    # bitmap rather than re-compressing it (confirmed -- a 170dpi render here
    # inflated the final PDF to ~9.7MB from a 247KB source PNG). The image is
    # always displayed at a fixed 480pt width in the report regardless of
    # source resolution, so 100dpi here is still sharp on screen/print while
    # keeping the PDF a reasonable size.
    fig.savefig(OUT_PATH, dpi=100)
    print(f"Wrote {OUT_PATH}")


if __name__ == "__main__":
    main()
