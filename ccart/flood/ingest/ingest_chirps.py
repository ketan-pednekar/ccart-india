"""
Module: chirps_ingest
CCART-Floods Framework (v2)
-------------------------------------------------------------
Purpose
-------
Ingest CHIRPS daily rainfall rasters, optionally clip them to a region
(e.g., India), clean invalid values, and establish the reference CHIRPS
grid used across the CCART rainfall and hazard subsystems.

This version is fully config-driven and supports:
- Global mode (no clipping)
- Regional mode (clip to India or any polygon)
"""

import re
from pathlib import Path

import numpy as np
import pandas as pd
import geopandas as gpd
import rasterio
import rasterio.mask

from ccart.flood.config import load_paths, load_flood_params


# ============================================================
# Load configuration
# ============================================================

paths = load_paths()
params = load_flood_params()

CHIRPS_DIR = Path(paths["chirps"]["daily_dir"])

# Optional clipping controls
CLIP = paths["chirps"].get("clip_to_region", False)
REGION_BOUNDARY = paths["chirps"].get("region_boundary", None)

BASELINE_START = params["baseline"]["start"]
BASELINE_END = params["baseline"]["end"]


# ============================================================
# Flexible CHIRPS filename pattern
# ============================================================

DATE_RE = re.compile(r"(\d{4})[.\-_](\d{1,2})[.\-_](\d{1,2})", re.IGNORECASE)


# ============================================================
# Load one CHIRPS day (optionally clipped)
# ============================================================

def load_day(fp: Path, region_geom=None, clip=True):
    """
    Load a single CHIRPS raster.
    If clip=True and region_geom is provided, clip to region.
    """

    with rasterio.open(fp) as src:
        if clip and region_geom is not None:
            out, tf = rasterio.mask.mask(
                src, region_geom, crop=True, filled=True, nodata=np.nan
            )
            arr = out[0].astype("float32")
        else:
            arr = src.read(1).astype("float32")
            tf = src.transform

    # Clean invalid values
    arr = np.where(
        (arr < 0) | (arr > 500) | (~np.isfinite(arr)),
        0.0,
        arr
    )

    return arr, tf


# ============================================================
# Inventory CHIRPS daily files
# ============================================================

def inventory_chirps(start_year=None, end_year=None):
    """
    Scan CHIRPS directory and build a sorted inventory of daily files.

    Returns:
        DataFrame with columns: path, year, month, day
    """

    chirps_dir = CHIRPS_DIR
    records = []

    for yr_dir in sorted(chirps_dir.glob("*")):
        if not yr_dir.is_dir():
            continue

        try:
            yr = int(yr_dir.name.strip().replace("\ufeff", ""))
        except ValueError:
            continue

        if start_year and yr < start_year:
            continue
        if end_year and yr > end_year:
            continue

        for fp in sorted(yr_dir.glob("*.tif*")):
            m = DATE_RE.search(fp.name)
            if m:
                records.append({
                    "path": fp,
                    "year": int(m.group(1)),
                    "month": int(m.group(2)),
                    "day": int(m.group(3))
                })

    file_df = (
        pd.DataFrame(records)
        .sort_values(["year", "month", "day"])
        .reset_index(drop=True)
    )

    if file_df.empty:
        raise RuntimeError(f"No CHIRPS files found in {chirps_dir}")

    return file_df


# ============================================================
# Establish CHIRPS reference grid
# ============================================================

def get_reference_grid(file_df, region_geom=None, clip=True):
    """
    Determine the reference grid (shape, transform, CRS)
    from the first CHIRPS file.
    """
    first_fp = file_df.iloc[0]["path"]
    arr, tf = load_day(first_fp, region_geom, clip=clip)
    shape = arr.shape
    crs = "EPSG:4326"
    return shape, tf, crs


# ============================================================
# Main entry point
# ============================================================

def load_chirps(start_year=None, end_year=None):
    """
    Main ingestion function.

    Returns:
        dict with:
            file_df
            shape
            transform
            crs
            region_geom
            clip
            load_day (callable)
    """

    # Load region boundary only if clipping is enabled
    if CLIP and REGION_BOUNDARY is not None:
        region = gpd.read_file(REGION_BOUNDARY).to_crs("EPSG:4326")
        region_geom = [region.union_all()]
    else:
        region_geom = None

    # Inventory CHIRPS files
    file_df = inventory_chirps(
        start_year=start_year or BASELINE_START,
        end_year=end_year or BASELINE_END
    )

    print("CHIRPS years seen in ingest:", sorted(file_df["year"].unique()))
    print("Reading CHIRPS from:", CHIRPS_DIR.resolve())
    print("Clipping enabled:", CLIP)

    # Establish reference grid
    shape, transform, crs = get_reference_grid(file_df, region_geom, clip=CLIP)

    years = sorted(file_df["year"].unique())

    # Build lat/lon coordinate arrays from transform
    ny, nx = shape
    lats = np.array([transform.f + transform.e * i for i in range(ny)])
    lons = np.array([transform.c + transform.a * j for j in range(nx)])

    return {
        "file_df": file_df,
        "years": years,
        "shape": shape,
        "lats": lats,
        "lons": lons,
        "transform": transform,
        "crs": crs,
        "region_geom": region_geom,
        "clip": CLIP,
        "load_day": lambda fp: load_day(fp, region_geom, clip=CLIP)
    }
