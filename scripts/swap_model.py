#!/usr/bin/env python3
"""Model swap helper.

Copies model artifacts from one version directory to another and updates
backend/app/config.py with the new version string.

Usage:
    python scripts/swap_model.py --from-version 2026-08-07c --to-version 2026-08-30a
"""

import argparse
import re
import shutil
import sys
from pathlib import Path

BACKEND = Path(__file__).resolve().parent.parent / "backend"
MODELS_ROOT = BACKEND / "models"
MODELS_IMPROVED_ROOT = BACKEND / "models_improved"
CONFIG_PATH = BACKEND / "app" / "config.py"


def copy_version(src_dir: Path, dst_dir: Path) -> list[str]:
    """Copy all model artifacts from src_dir to dst_dir. Returns list of copied files."""
    if not src_dir.exists():
        raise FileNotFoundError(f"Source version directory not found: {src_dir}")
    if not src_dir.is_dir():
        raise NotADirectoryError(f"Source is not a directory: {src_dir}")

    dst_dir.mkdir(parents=True, exist_ok=True)
    copied = []
    for item in src_dir.iterdir():
        dst_item = dst_dir / item.name
        if item.is_file():
            shutil.copy2(item, dst_item)
            copied.append(item.name)
        elif item.is_dir():
            if dst_item.exists():
                shutil.rmtree(dst_item)
            shutil.copytree(item, dst_item)
            copied.append(f"{item.name}/")
    return copied


def update_config(new_version: str) -> bool:
    """Update flood_model_version in backend/app/config.py. Returns True if changed."""
    content = CONFIG_PATH.read_text()
    pattern = re.compile(r'(flood_model_version\s*:\s*str\s*=\s*)"[^"]*"')
    new_content, n = pattern.subn(r'\1"' + new_version + '"', content)
    if n == 0:
        raise RuntimeError(f"Could not find flood_model_version in {CONFIG_PATH}")
    if new_content != content:
        CONFIG_PATH.write_text(new_content)
        return True
    return False


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--from-version", required=True, help="Source model version directory name")
    parser.add_argument("--to-version", required=True, help="Destination model version directory name")
    parser.add_argument(
        "--source", choices=["models", "models_improved"], default="models",
        help="Which root to copy FROM (default: models)",
    )
    parser.add_argument(
        "--dest", choices=["models", "models_improved"], default="models_improved",
        help="Which root to copy TO (default: models_improved)",
    )
    args = parser.parse_args()

    src_root = MODELS_ROOT if args.source == "models" else MODELS_IMPROVED_ROOT
    dst_root = MODELS_ROOT if args.dest == "models" else MODELS_IMPROVED_ROOT

    src_dir = src_root / args.from_version
    dst_dir = dst_root / args.to_version

    print(f"Copying from {src_dir} -> {dst_dir}")
    copied = copy_version(src_dir, dst_dir)
    for name in copied:
        print(f"  {name}")

    changed = update_config(args.to_version)
    if changed:
        print(f"\nUpdated flood_model_version in {CONFIG_PATH} -> {args.to_version}")
    else:
        print(f"\nflood_model_version already set to {args.to_version} in {CONFIG_PATH}")

    print("\nTo apply the swap, restart the API:")
    print("  # If running via uvicorn directly:")
    print(f"    uvicorn app.main:app --reload")
    print("  # If running via docker/systemd, restart that service.")


if __name__ == "__main__":
    main()
