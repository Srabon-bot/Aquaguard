"""Download CHIRPS v2.0 global daily rainfall (1981-present, 0.05 deg) and
subset to the Ganges-Brahmaputra-Meghna (GBM) catchment, since flooding in
Bangladesh is driven as much by upstream rainfall in India/Nepal/Bhutan as by
local rain (see plan.md).

Source: https://data.chc.ucsb.edu/products/CHIRPS-2.0/global_daily/netcdf/p05/
One netCDF file per year, global coverage, ~1.3 GB/file. We stream each
year's file to a temp path, subset to the catchment bounding box, write the
much smaller subset to backend/data_raw/chirps/, then delete the temp
download so we never hold the full global grid on disk.

Usage:
    python train/ingest_chirps.py                 # all years, 1981-current
    python train/ingest_chirps.py --start 2015 --end 2022
    python train/ingest_chirps.py --years 2017 2019 2020
"""

import argparse
import datetime as dt
import sys
import tempfile
import time
from pathlib import Path

import requests
import xarray as xr

BASE_URL = "https://data.chc.ucsb.edu/products/CHIRPS-2.0/global_daily/netcdf/p05"
OUT_DIR = Path(__file__).resolve().parent.parent / "data_raw" / "chirps"

# Temp downloads (~1.1GB/year) go on D: rather than the system temp dir --
# the C: drive on this machine is nearly full (confirmed 2026-08-05, ~97%
# used, only a few GB free), and a python session getting killed mid-download
# has already once left an orphaned ~700MB temp dir behind on C:.
TMP_DIR = Path(__file__).resolve().parent.parent / "data_raw" / ".tmp_downloads"

# GBM catchment bounding box: covers Bangladesh plus the upstream reaches of
# the Ganges (northern India), Brahmaputra (NE India), and Meghna
# (Meghalaya/Assam, Surma-Kushiyara) basins. Deliberately generous — this is
# a coarse pre-filter, not the final feature-engineering region.
LAT_MIN, LAT_MAX = 20.0, 31.0
LON_MIN, LON_MAX = 73.0, 97.0

FIRST_YEAR = 1981


def year_url(year: int) -> str:
    return f"{BASE_URL}/chirps-v2.0.{year}.days_p05.nc"


def subset_path(year: int) -> Path:
    return OUT_DIR / f"chirps_gbm_{year}.nc"


MAX_DOWNLOAD_RETRIES = 4


def download_year(year: int, dest: Path) -> None:
    url = year_url(year)
    for attempt in range(1, MAX_DOWNLOAD_RETRIES + 1):
        written = 0
        total = 0
        try:
            resp = requests.get(url, stream=True, timeout=60)
            resp.raise_for_status()
            total = int(resp.headers.get("content-length", 0))
            with open(dest, "wb") as f:
                for chunk in resp.iter_content(chunk_size=1 << 20):
                    f.write(chunk)
                    written += len(chunk)
                    if total:
                        pct = 100 * written / total
                        print(f"\r  downloading {year}: {written / 1e6:.0f}/{total / 1e6:.0f} MB ({pct:.0f}%)", end="", flush=True)
            print()
            return
        except (requests.exceptions.ChunkedEncodingError,
                requests.exceptions.ConnectionError,
                requests.exceptions.Timeout) as exc:
            print(f"\n  [{year}] network error mid-download (attempt {attempt}/{MAX_DOWNLOAD_RETRIES}, "
                  f"{written / 1e6:.0f}/{total / 1e6:.0f} MB before drop): {exc}")
            if attempt == MAX_DOWNLOAD_RETRIES:
                raise
            wait = 5 * attempt
            print(f"  retrying in {wait}s...")
            time.sleep(wait)


def subset_and_save(tmp_path: Path, out_path: Path, year: int) -> None:
    ds = xr.open_dataset(tmp_path)
    lat_name = "latitude" if "latitude" in ds.coords else "lat"
    lon_name = "longitude" if "longitude" in ds.coords else "lon"

    lat_vals = ds[lat_name].values
    lat_ascending = lat_vals[0] < lat_vals[-1]
    lat_slice = slice(LAT_MIN, LAT_MAX) if lat_ascending else slice(LAT_MAX, LAT_MIN)

    subset = ds.sel({lat_name: lat_slice, lon_name: slice(LON_MIN, LON_MAX)})
    subset = subset.load()  # force read before we delete the source file

    # Write to a temp path in the same dir, then atomically rename into place.
    # Writing straight to out_path would let a crash/power-cut mid-write leave
    # a truncated .nc file sitting at out_path -- which the resume check
    # (`out_path.exists()`) would then wrongly treat as "already done" and
    # skip forever, silently corrupting that year. The rename is atomic (same
    # filesystem), so out_path only ever exists in a fully-written state.
    partial_path = out_path.with_suffix(out_path.suffix + ".partial")
    subset.to_netcdf(partial_path)
    ds.close()
    partial_path.replace(out_path)
    print(f"  saved subset: {out_path} ({out_path.stat().st_size / 1e6:.1f} MB, "
          f"{subset.sizes.get('time', '?')} days)")


def process_year(year: int, force: bool = False) -> None:
    out_path = subset_path(year)
    if out_path.exists() and not force:
        print(f"[{year}] already have subset at {out_path}, skipping (use --force to redo)")
        return

    print(f"[{year}] fetching {year_url(year)}")
    TMP_DIR.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix=f"chirps_{year}_", dir=TMP_DIR) as tmp_dir:
        tmp_path = Path(tmp_dir) / f"chirps-v2.0.{year}.days_p05.nc"
        try:
            download_year(year, tmp_path)
        except requests.HTTPError as exc:
            print(f"[{year}] download failed: {exc} -- likely no data for this year yet, skipping", file=sys.stderr)
            return
        except (requests.exceptions.ChunkedEncodingError,
                requests.exceptions.ConnectionError,
                requests.exceptions.Timeout) as exc:
            print(f"[{year}] download failed after {MAX_DOWNLOAD_RETRIES} retries (network error): {exc} "
                  f"-- skipping this year, rerun the script later to retry it", file=sys.stderr)
            return
        subset_and_save(tmp_path, out_path, year)


def main():
    current_year = dt.date.today().year
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--start", type=int, default=FIRST_YEAR)
    parser.add_argument("--end", type=int, default=current_year)
    parser.add_argument("--years", type=int, nargs="*", help="explicit list of years, overrides --start/--end")
    parser.add_argument("--force", action="store_true", help="redownload/resubset years that already have output")
    args = parser.parse_args()

    OUT_DIR.mkdir(parents=True, exist_ok=True)

    years = args.years if args.years else range(args.start, args.end + 1)
    for year in years:
        process_year(year, force=args.force)


if __name__ == "__main__":
    main()
