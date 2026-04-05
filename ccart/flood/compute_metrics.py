"""
Module: compute_metrics
CCART-Floods Framework
-------------------------------------------------------------

Purpose
-------
Computes CHIRPS-based rainfall metrics needed for the CCART hazard engine.
Currently implemented:

- Annual Rx2day (maximum 2-day rainfall per year, per pixel)
- Pixel-wise P95 of Rx2day over a baseline period

Design
------
All computations are memory-safe and operate year-by-year, mirroring the
dynamic hazard pipeline. Intermediate results (Rx2day per year) can be
saved to disk as .npy files for reuse.

Author
------
CCART Team
"""

import numpy as np
import pandas as pd
from pathlib import Path
import gc

from ccart.flood.chirps.ingest_chirps import load_chirps

from ccart.flood.config import CHIRPS_DAILY_DIR
print("Using CHIRPS directory:", CHIRPS_DAILY_DIR)



# ============================================================
# Rx2day: maximum 2-day rainfall per year
# ============================================================

def compute_rx2day_for_year(year, chirps_meta, rx2day_dir: Path | None = None):
    """
    Compute Rx2day (max 2-day rainfall) for a single year.
    """

    file_df     = chirps_meta["file_df"]
    shape       = chirps_meta["shape"]
    india_geom  = chirps_meta["india_geom"]
    load_day_fn = chirps_meta["load_day"]

    yr_files = (file_df[file_df["year"] == year]
                .sort_values(["month", "day"])["path"]
                .tolist())

    if len(yr_files) < 2:
        raise ValueError(f"Year {year}: fewer than 2 CHIRPS files, cannot compute Rx2day.")

    # Initialise sliding window with day 1
    day_prev, _ = load_day_fn(yr_files[0], india_geom)
    rx2day_yr   = np.zeros(shape, dtype="float32")

    for fp in yr_files[1:]:
        day_curr, _ = load_day_fn(fp, india_geom)

        # 2-day sum
        two_day = day_prev + day_curr

        # Safety cap: if each day is capped at 500 mm,
        # the theoretical 2-day max is 1000 mm.
        two_day = np.where(two_day > 1000, 0.0, two_day)

        # Update Rx2day
        np.maximum(rx2day_yr, two_day, out=rx2day_yr)

        day_prev = day_curr
        del day_curr, two_day

    del day_prev
    gc.collect()

    if rx2day_dir is not None:
        rx2day_dir.mkdir(parents=True, exist_ok=True)
        out_path = rx2day_dir / f"rx2day_{year}.npy"
        np.save(out_path, rx2day_yr)

    return rx2day_yr


def compute_rx2day_baseline(chirps_meta, start_year: int, end_year: int,
                            rx2day_dir: Path | None = None):
    """
    Compute Rx2day for all years in a baseline period.

    Parameters
    ----------
    chirps_meta : dict
        Output of load_chirps().
    start_year, end_year : int
        Inclusive year range.
    rx2day_dir : Path or None
        If provided, saves one .npy per year.

    Returns
    -------
    years_done : list[int]
        Years successfully processed.
    """

    file_df = chirps_meta["file_df"]
    years_available = sorted(file_df["year"].unique())
    years_target = [y for y in years_available if start_year <= y <= end_year]

    years_done = []

    for yr in years_target:
        if rx2day_dir is not None:
            out_path = rx2day_dir / f"rx2day_{yr}.npy"
            if out_path.exists():
                years_done.append(yr)
                continue

        rx2day_yr = compute_rx2day_for_year(yr, chirps_meta, rx2day_dir=rx2day_dir)
        max_val  = float(rx2day_yr.max())
        mean_val = float(rx2day_yr[rx2day_yr > 0].mean()) if (rx2day_yr > 0).any() else 0.0
        print(f"{yr}: Rx2day max={max_val:.1f} mm  mean(>0)={mean_val:.1f} mm")
        years_done.append(yr)

        del rx2day_yr
        gc.collect()

    return years_done


# ============================================================
# P95: pixel-wise 95th percentile of Rx2day over baseline
# ============================================================

def compute_p95_from_rx2day(rx2day_dir: Path,
                            out_path: Path | None = None) -> np.ndarray:
    """
    Compute pixel-wise P95 of Rx2day from saved annual Rx2day .npy files.

    Parameters
    ----------
    rx2day_dir : Path
        Directory containing rx2day_{year}.npy files.
    out_path : Path or None
        If provided, saves p95 array as .npy.

    Returns
    -------
    p95 : 2D float32 ndarray
        Pixel-wise 95th percentile of Rx2day.
    """

    npy_files = sorted(rx2day_dir.glob("rx2day_*.npy"))
    if not npy_files:
        raise RuntimeError(f"No rx2day_*.npy files found in {rx2day_dir}")

    print(f"Stacking {len(npy_files)} annual Rx2day arrays for P95 computation...")

    # Load each year, mask zeros as NaN to avoid biasing percentiles
    stack_list = []
    for f in npy_files:
        arr = np.load(f).astype("float32")
        arr = np.where(arr > 0, arr, np.nan)
        stack_list.append(arr)

    stack = np.stack(stack_list, axis=0)  # (n_years, rows, cols)
    p95 = np.nanpercentile(stack, 95, axis=0).astype("float32")

    del stack, stack_list
    gc.collect()

    if out_path is not None:
        out_path.parent.mkdir(parents=True, exist_ok=True)
        np.save(out_path, p95)

    return p95


# ============================================================
# Convenience wrapper: full baseline metrics
# ============================================================

def compute_baseline_metrics(start_year: int,
                             end_year: int,
                             rx2day_dir: Path,
                             p95_path: Path | None = None,
                             chirps_start_year: int | None = None,
                             chirps_end_year: int | None = None):
    """
    High-level helper to:
      1) load CHIRPS metadata
      2) compute Rx2day for baseline years
      3) compute P95 from saved Rx2day arrays

    Parameters
    ----------
    start_year, end_year : int
        Baseline period for Rx2day and P95.
    rx2day_dir : Path
        Directory to store rx2day_{year}.npy files.
    p95_path : Path or None
        If provided, saves P95 array as .npy.
    chirps_start_year, chirps_end_year : int or None
        Optional bounds for CHIRPS inventory (passed to load_chirps).

    Returns
    -------
    p95 : 2D float32 ndarray
        Pixel-wise 95th percentile of Rx2day.
    """

    chirps_meta = load_chirps(
        start_year=chirps_start_year or start_year,
        end_year=chirps_end_year or end_year
    )

    # 🔍 ADD THESE TWO LINES HERE
    print("CHIRPS years seen in metrics:", sorted(chirps_meta["file_df"]["year"].unique()))
    print("Saving Rx2day to:", rx2day_dir.resolve())

    compute_rx2day_baseline(
        chirps_meta=chirps_meta,
        start_year=start_year,
        end_year=end_year,
        rx2day_dir=rx2day_dir
    )

    p95 = compute_p95_from_rx2day(
        rx2day_dir=rx2day_dir,
        out_path=p95_path
    )

    print(f"P95 range: {np.nanmin(p95):.1f} – {np.nanmax(p95):.1f} mm/2day")
    return p95
