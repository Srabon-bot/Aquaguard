# AquaGuard dashboard (glassmorphism variant)

**Same HTML and JS as `../frontend/`, byte-for-byte identical** — only `style.css` differs. This
is a visual re-skin, not a separate build: same functionality, same data, same everything, just a
different look. Whichever folder you actually use day to day, keep the other in mind if you ever
change a feature — the HTML/JS need updating in both places since they're plain copies, not a
shared source.

A single static page — no build step, no npm install. Plain HTML/CSS/JS.

## Running it

```
cd frontend-glass
python -m http.server 5502
```

Then open **http://localhost:5502** in your browser. (Different port from `../frontend`'s 5500
purely so you can run both side by side to compare.)

(Opening `index.html` directly by double-clicking it will often work too — try that first if you
don't want to run a server — but switch to the method above if "Use my location" doesn't prompt
for permission.)

## Before using the model sections

Same as the neumorphic version — see `../frontend/README.md`'s "Before using the model sections"
section, identical instructions apply here.

## What's real vs. placeholder right now

Identical to `../frontend/README.md` — weather and both model cards are real and live; sensor
tiles/tank visual are demo data; pump control + water cycle are simulated (local-only, no
Firebase writes). See that file for the full breakdown and reasoning.

## Design

**Glassmorphism** — translucent, blurred panels floating over a fixed vivid gradient background,
with a thin light border standing in for the edge a sheet of glass would catch. A few deliberate
departures from the "true glass" look, both for legibility:

- **Panel fill is fairly opaque** (~68% white in light mode, ~58% near-black in dark mode) rather
  than the very transparent 10-20% fill glassmorphism is sometimes done at. Real glass panels
  floating over a busy multi-color gradient fight text contrast badly at low opacity — blur and
  saturation carry the "glass" identity here, not raw see-through-ness, so text stays reliably
  legible no matter which part of the gradient sits behind any given panel.
- **Status colors (risk levels, trends) stay exactly the fixed, never-themed palette** from the
  neumorphic version — untouched by the glass re-skin, still paired with an icon + text label
  rather than relying on color alone.
- Buttons give tactile feedback with a brightness/lift on hover and a scale-down on press, instead
  of the neumorphic version's inset-shadow "pressed into the surface" trick — that particular
  effect doesn't read as glass.

Supports light/dark mode — follows your OS setting by default (a bright aqua/teal/indigo gradient
in light mode, a deep moody navy/teal gradient in dark mode), or use the toggle in the top-right
corner (saved in `localStorage`, independent from the neumorphic version's saved preference).

Requires `backdrop-filter` support (all current major browsers — Chrome, Edge, Safari, Firefox
103+). On a browser without it, panels still render with their solid-ish fill color, just without
the blur — functionally identical, just flatter looking.
