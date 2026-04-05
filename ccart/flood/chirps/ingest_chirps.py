"""
Module: ingest_chirps
CCART-Floods Framework
-------------------------------------------------------------
Purpose
-------
Ingests CHIRPS daily rainfall rasters, clips them to India, cleans
invalid values, and establishes the reference CHIRPS grid used across
the CCART rainfall and hazard subsystems.
"""

import numpy as np
import pandas as pd
import geopandas as gpd
import rasterio
import rasterio.mask
from pathlib import Path
import re

from ccart.flood.config import (
    CHIRPS_DAILY_DIR,
    INDIA_SHP
)

# ============================================================
# Flexible CHIRPS filename pattern
# ============================================================

date_re = re.compile(r"(\d{4})[.\-_](\d{1,2})[.\-_](\d{1,2})", re.IGNORECASE)


# ============================================================
# Load one CHIRPS day clipped to India
# ============================================================

def load_day(fp, india_geom):
    with rasterio.open(fp) as src:
        out, tf = rasterio.mask.mask(
            src, india_geom, crop=True, filled=True, nodata=np.nan
        )

    arr = out[0].astype("float32")

    # Clean: negatives, non-finite, and rare extreme artefacts
    arr = np.where(
        (arr < 0) | (arr > 500) | (~np.isfinite(arr)),
        0.0,
        arr
    )

    return arr, tf


# ============================================================
# Inventory CHIRPS daily files
# ============================================================

def inventory_chirps(chirps_dir=CHIRPS_DAILY_DIR, start_year=None, end_year=None):
    """
    Scan CHIRPS directory and build a sorted inventory of daily files.
    """

    records = []

    for yr_dir in sorted(chirps_dir.glob("*")):
        if not yr_dir.is_dir():
            continue

        clean_name = yr_dir.name.strip().replace("\ufeff", "")
        try:
            yr = int(clean_name)
        except:
            continue

        if start_year and yr < start_year:
            continue
        if end_year and yr > end_year:
            continue

        for fp in sorted(yr_dir.glob("*.tif*")):
            m = date_re.search(fp.name)
            if m:
                records.append({
                    "path": fp,
                    "year": int(m.group(1)),
                    "month": int(m.group(2)),
                    "day": int(m.group(3))
                })

    file_df = (pd.DataFrame(records)
               .sort_values(["year", "month", "day"])
               .reset_index(drop=True))

    if file_df.empty:
        raise RuntimeError(f"No CHIRPS files found in {chirps_dir}")

    return file_df


# ============================================================
# Establish CHIRPS reference grid
# ============================================================

def get_reference_grid(file_df, india_geom):
    first_fp = file_df.iloc[0]["path"]
    arr, tf = load_day(first_fp, india_geom)
    shape = arr.shape
    crs = "EPSG:4326"
    return shape, tf, crs


# ============================================================
# Main entry point
# ============================================================

def load_chirps(start_year=None, end_year=None):
    """
    Main ingestion function.
    """

    # Load India boundary
    india = gpd.read_file(INDIA_SHP).to_crs("EPSG:4326")
    india_geom = [india.union_all()]

    # Inventory CHIRPS files
    file_df = inventory_chirps(
        chirps_dir=CHIRPS_DAILY_DIR,
        start_year=start_year,
        end_year=end_year
    )

    print("CHIRPS years seen in ingest:", sorted(file_df["year"].unique()))
    print("Reading CHIRPS from:", CHIRPS_DAILY_DIR.resolve())

    # Establish reference grid
    shape, transform, crs = get_reference_grid(file_df, india_geom)

    return {
        "file_df": file_df,
        "shape": shape,
        "transform": transform,
        "crs": crs,
        "india_geom": india_geom,
        "load_day": load_day
    }
