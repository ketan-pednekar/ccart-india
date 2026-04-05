"""
Module: hazard_engine
CCART-Floods Framework
-------------------------------------------------------------

Purpose
-------
Compute climate-conditioned flood hazard using:
    H = FSI × max(Rx2day / P95, 0)

This module provides:
- a clean hazard computation function
- year-by-year historical hazard loop (CHIRPS)
- year-by-year future hazard loop (CMIP6 → CHIRPS reprojection)

All operations are memory-safe and grid-aligned.

Author
------
CCART Team
"""

from pathlib import Path
import numpy as np
import xarray as xr
from rasterio.warp import reproject, Resampling
from rasterio.transform import from_bounds
import gc


# ------------------------------------------------------------
# CORE HAZARD FUNCTION
# ------------------------------------------------------------

def compute_hazard(rx2day_grid, p95_grid, fsi_on_chirps):
    """
    Compute hazard = FSI × max(Rx2day / P95, 0).

    Parameters
    ----------
    rx2day_grid : 2D ndarray
    p95_grid    : 2D ndarray
    fsi_on_chirps : 2D ndarray

    Returns
    -------
    hazard : 2D float32 ndarray
    """
    rel = np.maximum(rx2day_grid / p95_grid, 0.0)
    hazard = fsi_on_chirps * rel
    return np.where(np.isfinite(fsi_on_chirps), hazard, np.nan).astype("float32")


# ------------------------------------------------------------
# HISTORICAL HAZARD LOOP (CHIRPS Rx2day)
# ------------------------------------------------------------

def compute_historical_hazard(rx2day_dir: Path,
                              p95_grid: np.ndarray,
                              fsi_on_chirps: np.ndarray,
                              out_dir: Path):
    """
    Compute historical hazard year-by-year using saved CHIRPS Rx2day arrays.

    Saves one .npy per year.
    """
    out_dir.mkdir(exist_ok=True)

    for npy_file in sorted(rx2day_dir.glob("rx2day_*.npy")):
        yr = int(npy_file.stem.split("_")[1])
        out_path = out_dir / f"hazard_hist_{yr}.npy"

        if out_path.exists():
            continue

        rx2day = np.load(npy_file)
        hazard = compute_hazard(rx2day, p95_grid, fsi_on_chirps)

        np.save(out_path, hazard)

        del rx2day, hazard
        gc.collect()


# ------------------------------------------------------------
# FUTURE HAZARD LOOP (CMIP6 → CHIRPS)
# ------------------------------------------------------------

def compute_future_hazard(cmip_dir: Path,
                          p95_grid: np.ndarray,
                          fsi_on_chirps: np.ndarray,
                          chirps_shape,
                          chirps_transform,
                          out_dir: Path,
                          start_year: int,
                          end_year: int):
    """
    Compute future hazard year-by-year using CMIP6 daily rainfall.

    Steps:
    - compute Rx2day via xarray rolling window
    - reproject CMIP6 grid → CHIRPS grid
    - compute hazard
    - save one .npy per year
    """
    out_dir.mkdir(exist_ok=True)

    cmip_files = sorted(cmip_dir.glob("*.nc"))

    for f in cmip_files:
        ds = xr.open_dataset(f)
        yr = int(ds.time.dt.year.values[0])

        if not (start_year <= yr <= end_year):
            ds.close()
            continue

        out_path = out_dir / f"hazard_fut_{yr}.npy"
        if out_path.exists():
            ds.close()
            continue

        da = ds["pr"]  # mm/day

        # Rx2day via rolling window
        rx2day_xr = da.rolling(time=2, min_periods=2).sum().max(dim="time").values.astype("float32")

        # Build CMIP transform
        cmip_lats = da["lat"].values
        cmip_lons = da["lon"].values
        cmip_tf = from_bounds(
            float(cmip_lons.min()), float(cmip_lats.min()),
            float(cmip_lons.max()), float(cmip_lats.max()),
            len(cmip_lons), len(cmip_lats)
        )

        # Reproject to CHIRPS grid
        rx2day_reproj = np.zeros(chirps_shape, dtype="float32")
        reproject(
            source=rx2day_xr,
            destination=rx2day_reproj,
            src_transform=cmip_tf, src_crs="EPSG:4326",
            dst_transform=chirps_transform, dst_crs="EPSG:4326",
            resampling=Resampling.bilinear
        )

        # Hazard
        hazard = compute_hazard(rx2day_reproj, p95_grid, fsi_on_chirps)
        np.save(out_path, hazard)

        del rx2day_xr, rx2day_reproj, hazard
        ds.close()
        gc.collect()

