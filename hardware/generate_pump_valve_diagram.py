"""
Generates a one-page PDF diagram showing where to install a check valve on
each pump's discharge line, and why it stops the siphon. Pure matplotlib
(vector shapes -> PDF directly via savefig), no external diagramming tool.

Re-run any time the circuit changes -- this always regenerates from this
script, never hand-edited after the fact (same convention as
reports/generate_*_assets.py).

Usage:
    python generate_pump_valve_diagram.py
"""

from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch, Circle
from matplotlib.lines import Line2D

OUT_PATH = Path(__file__).resolve().parent / "PUMP_CHECK_VALVE_DIAGRAM.pdf"

BOX_STYLE = dict(boxstyle="round,pad=0.35,rounding_size=0.15", linewidth=1.6)
TANK_FILL = "#dbe9f7"
PUMP_FILL = "#fde9c9"
VALVE_FILL = "#c9f0d8"
EDGE = "#2b3a4a"


def box(ax, x, y, w, h, text, fill, fontsize=11, weight="bold"):
    ax.add_patch(FancyBboxPatch((x, y), w, h, facecolor=fill, edgecolor=EDGE, **BOX_STYLE))
    ax.text(x + w / 2, y + h / 2, text, ha="center", va="center",
             fontsize=fontsize, fontweight=weight, color="#1a1a1a")


def arrow(ax, x0, y0, x1, y1, label=None, label_dy=0.35):
    ax.add_patch(FancyArrowPatch((x0, y0), (x1, y1), arrowstyle="-|>",
                                   mutation_scale=22, linewidth=2, color=EDGE))
    if label:
        ax.text((x0 + x1) / 2, (y0 + y1) / 2 + label_dy, label,
                 ha="center", va="bottom", fontsize=9.5, color="#3a3a3a")


def check_valve_symbol(ax, cx, cy, r=0.42):
    """Standard check-valve symbol: circle with a ball, flow arrow through it."""
    ax.add_patch(Circle((cx, cy), r, facecolor=VALVE_FILL, edgecolor=EDGE, linewidth=1.8, zorder=3))
    ax.add_patch(FancyArrowPatch((cx - r * 0.85, cy), (cx + r * 0.85, cy),
                                   arrowstyle="-|>", mutation_scale=16,
                                   linewidth=2, color=EDGE, zorder=4))
    # the "ball" resting against its seat, spring hint behind it
    ax.add_patch(Circle((cx - r * 0.25, cy), r * 0.28, facecolor="#8a97a3",
                          edgecolor=EDGE, linewidth=1.2, zorder=5))


def draw_circuit(ax, y, source_label, dest_label, pump_label, flip_valve_pos=False):
    """One horizontal pump circuit: source -> pump -> check valve -> destination."""
    h = 1.3
    box(ax, 0.3, y, 2.6, h, source_label, TANK_FILL)
    arrow(ax, 2.9, y + h / 2, 4.1, y + h / 2)

    box(ax, 4.1, y, 2.4, h, pump_label, PUMP_FILL)
    arrow(ax, 6.5, y + h / 2, 7.7, y + h / 2, label="outlet")

    check_valve_symbol(ax, 8.35, y + h / 2)
    ax.text(8.35, y + h + 0.55, "CHECK VALVE\n(install here)",
             ha="center", va="bottom", fontsize=9.5, fontweight="bold", color="#0f4c5c")

    arrow(ax, 8.95, y + h / 2, 10.15, y + h / 2)
    box(ax, 10.15, y, 2.9, h, dest_label, TANK_FILL)


def main():
    fig, ax = plt.subplots(figsize=(13, 6.2))
    fig.subplots_adjust(top=0.82, bottom=0.19)
    ax.set_xlim(0, 13.6)
    ax.set_ylim(1.2, 7.4)
    ax.axis("off")

    fig.suptitle("AquaGuard — Pump Check-Valve Circuit Diagram", fontsize=17, fontweight="bold", y=0.975)
    fig.text(0.5, 0.925, "One check valve per pump, installed right at the pump's own outlet barb — "
             "each pump gets its own, not shared, not further downstream",
             ha="center", fontsize=10, color="#3a3a3a")

    draw_circuit(ax, 4.9, "POND / TANK\n(water level)", "DRAIN\n(outside)", "PUMP 1\n(drain)")
    draw_circuit(ax, 2.05, "SUPPLY / SOURCE", "POND / TANK", "PUMP 2\n(refill)")

    # Mechanism caption strip -- sits in the space below row 2, above the legend
    caption = (
        "How it works:  ①  Pump OFF → spring holds the poppet shut against its seat — sealed, no path through.   "
        "②  Pump ON → water pressure compresses the spring, lifts the poppet, water flows freely.   "
        "③  Pump OFF again → spring snaps shut instantly, before gravity/siphon pressure can push water backward through it."
    )
    fig.text(0.04, 0.05, caption, fontsize=9.3, color="#1a1a1a", wrap=True)

    legend_elems = [
        Line2D([0], [0], marker="o", color="w", markerfacecolor=TANK_FILL, markeredgecolor=EDGE, markersize=14, label="Tank / reservoir"),
        Line2D([0], [0], marker="o", color="w", markerfacecolor=PUMP_FILL, markeredgecolor=EDGE, markersize=14, label="Pump"),
        Line2D([0], [0], marker="o", color="w", markerfacecolor=VALVE_FILL, markeredgecolor=EDGE, markersize=14, label="Check valve (one-way)"),
    ]
    ax.legend(handles=legend_elems, loc="upper right", frameon=False, fontsize=9.5, bbox_to_anchor=(1.0, 1.1))

    fig.savefig(OUT_PATH, format="pdf", bbox_inches="tight")
    plt.close(fig)
    print(f"Wrote {OUT_PATH}")


if __name__ == "__main__":
    main()
