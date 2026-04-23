"""
CCART Hazard-Max Engine (2027–2100, CHIRPS-aligned grid)

Purpose:
    Compute the period-maximum dynamic flood hazard layer for each scenario
    (SSP370, SSP585) over the full future window 2027–2100.

Scientific Logic:
    For each scenario:
        1. Load all annual hazard rasters:
               hazard_ssp370_YYYY.tif
               hazard_ssp585_YYYY.tif
        2. Compute pixel-wise maximum across all years:
               hazard_max = max(hazard_2027, ..., hazard_2100)
        3. Preserve Indo-Floods NaN mask (no extrapolation)
        4. Save final period-maximum hazard layer:
               hazard_max_ssp370_2027_2100.tif
               hazard_max_ssp585_2027_2100.tif

Inputs (from paths.yaml):
    - flood.outputs.hazard directory containing annual hazard rasters

Outputs:
    - hazard_max_ssp370_2027_2100.tif
    - hazard_max_ssp585_2027_2100.tif

Notes:
    - No interpolation, smoothing, or IDW is applied.
    - Hazard-max is a resilience design layer: the worst-case hazard
      expected over the entire future period.
    - NaN mask from Indo-Floods is strictly preserved.
"""

import numpy as np
import rasterio
from pathlib import Path

from ccart.flood.config import load_paths

paths = load_paths()
project_root = Path(paths["project_root"])

hazard_dir = project_root / paths["flood"]["outputs"]["hazard"]
out_dir = project_root / paths["flood"]["outputs"]["hazard"]
out_dir.mkdir(parents=True, exist_ok=True)


def load_raster(path):
    with rasterio.open(path) as src:
        arr = src.read(1).astype("float32")
        profile = src.profile
    return arr, profile

def save_raster(path, array, profile):
    profile = profile.copy()
    profile.update(dtype="float32", compress="lzw")
    with rasterio.open(path, "w", **profile) as dst:
        dst.write(array.astype("float32"), 1)

def compute_period_max(scenario):
    print(f"Computing period-max hazard for {scenario}...")

    rasters = sorted(hazard_dir.glob(f"hazard_{scenario}_*.tif"))
    if not rasters:
        raise RuntimeError(f"No hazard rasters found for {scenario}")

    # initialize with first raster
    arr0, profile = load_raster(rasters[0])
    period_max = arr0.copy()

    for r in rasters[1:]:
        arr, _ = load_raster(r)
        period_max = np.nanmax(np.stack([period_max, arr]), axis=0)

    # preserve Indo-Floods mask
    period_max[np.isnan(arr0)] = np.nan

    out_path = out_dir / f"hazard_max_{scenario}_2027_2100.tif"
    save_raster(out_path, period_max, profile)
    print(f"Saved: {out_path}")

if __name__ == "__main__":
    compute_period_max("ssp370")
    compute_period_max("ssp585")

    print("Resilience design hazard layers complete.")
