#!/usr/bin/env bash
# Double-click/terminal convenience wrapper for Mac/Linux -- see SETUP_MANUAL.md for first-time setup.
# Assumes the shared virtual environment already exists at packages/.venv (Step 3 of the manual).

cd "$(dirname "$0")" || exit 1

if [ ! -f ".venv/bin/python" ]; then
    echo "Could not find packages/.venv/bin/python"
    echo "Run the first-time setup in SETUP_MANUAL.md before using this script."
    exit 1
fi

exec ".venv/bin/python" run_all.py
