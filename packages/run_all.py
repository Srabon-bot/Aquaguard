#!/usr/bin/env python
"""
Starts all 3 flood model services (flood-risk-classifier, discharge-forecaster,
flood-susceptibility) at once, each in its own subprocess on its own port, with
prefixed log output so you can tell which service printed what in one terminal.

Usage (after activating the shared venv and installing packages/requirements.txt):
    python run_all.py

Press Ctrl+C once to stop all three cleanly.

See packages/SETUP_MANUAL.md for the full first-time setup walkthrough.
"""

import subprocess
import sys
import threading
from pathlib import Path

PACKAGES_DIR = Path(__file__).resolve().parent

# (log prefix, folder name, port)
SERVICES = [
    ("classifier", "flood-risk-classifier", 8000),
    ("discharge", "discharge-forecaster", 8001),
    ("susceptibility", "flood-susceptibility", 8002),
]


def stream_output(proc: subprocess.Popen, prefix: str) -> None:
    """Reads a subprocess's combined stdout/stderr line by line and reprints it
    with a [prefix] tag, so all 3 services' logs are distinguishable in one
    terminal instead of interleaved anonymously."""
    assert proc.stdout is not None
    for line in proc.stdout:
        print(f"[{prefix}] {line}", end="")


def main() -> int:
    processes: list[tuple[str, subprocess.Popen]] = []

    for prefix, folder, port in SERVICES:
        service_dir = PACKAGES_DIR / folder
        if not service_dir.is_dir():
            print(f"[{prefix}] ERROR: expected folder not found: {service_dir}")
            print("Are you running this from inside the packages/ folder? See SETUP_MANUAL.md.")
            _shutdown(processes)
            return 1

        print(f"[{prefix}] starting on port {port} ...")
        proc = subprocess.Popen(
            [sys.executable, "-m", "uvicorn", "main:app", "--host", "127.0.0.1", "--port", str(port)],
            cwd=str(service_dir),
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
        )
        processes.append((prefix, proc))
        threading.Thread(target=stream_output, args=(proc, prefix), daemon=True).start()

    print()
    print("All 3 services starting. Once ready:")
    print("  classifier      -> http://127.0.0.1:8000/docs")
    print("  discharge       -> http://127.0.0.1:8001/docs")
    print("  susceptibility  -> http://127.0.0.1:8002/docs")
    print()
    print("Press Ctrl+C to stop all three.")
    print()

    try:
        # Block until any one of them exits on its own (e.g. crashes) or the
        # user hits Ctrl+C -- either way, fall through to a clean shutdown of
        # whatever's still running rather than leaving orphaned processes.
        while True:
            for prefix, proc in processes:
                code = proc.poll()
                if code is not None:
                    print(f"[{prefix}] exited unexpectedly (code {code}) -- stopping the others.")
                    _shutdown(processes)
                    return code
            for _, proc in processes:
                try:
                    proc.wait(timeout=0.5)
                except subprocess.TimeoutExpired:
                    pass
    except KeyboardInterrupt:
        print("\nStopping all 3 services ...")
        _shutdown(processes)
        return 0


def _shutdown(processes: list[tuple[str, subprocess.Popen]]) -> None:
    for prefix, proc in processes:
        if proc.poll() is None:
            proc.terminate()
    for prefix, proc in processes:
        try:
            proc.wait(timeout=10)
        except subprocess.TimeoutExpired:
            proc.kill()
            proc.wait()


if __name__ == "__main__":
    raise SystemExit(main())
