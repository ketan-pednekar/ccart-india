"""
CCART Hazard-Max Engine (2027–2100, CHIRPS-aligned grid)

Computes the pixel-wise maximum dynamic flood hazard layer for each scenario
(SSP370, SSP585) over the full future window 2027–2100.
"""

import numpy as np
import rasterio
from pathlib import Path
from ccart.flood.config import load_paths

# ---------------------------------------------------------
# PATHS
# ---------------------------------------------------------

paths = load_paths()
project_root = Path(paths["project_root"])

# Annual hazard rasters (input)
hazard_annual_dir = project_root / paths["flood"]["outputs"]["hazard_annual"]

# Output directory for period-max hazard
hazard_max_dir = project_root / paths["flood"]["outputs"]["hazard_max"]
hazard_max_dir.mkdir(parents=True, exist_ok=True)

# FSI static (for Indo-Floods NaN mask)
fsi_path = project_root / paths["flood"]["inputs"]["fsi"]


# ---------------------------------------------------------
# UTILITIES
# ---------------------------------------------------------

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


# ---------------------------------------------------------
# LOAD INDO-FLOODS MASK (FSI STATIC)
# ---------------------------------------------------------

with rasterio.open(fsi_path) as src:
    fsi_mask = src.read(1).astype("float32")

nan_mask = np.isnan(fsi_mask)


# ---------------------------------------------------------
# PERIOD-MAX COMPUTATION
# ---------------------------------------------------------

def compute_period_max(scenario):
    print(f"Computing period-max hazard for {scenario}...")

    # Load all annual hazard rasters for this scenario
    rasters = sorted(hazard_annual_dir.glob(f"hazard_{scenario}_*.tif"))
    if not rasters:
        raise RuntimeError(f"No hazard rasters found for {scenario}")

    # Initialize with first raster
    arr0, profile = load_raster(rasters[0])
    period_max = arr0.copy()

    # Pixel-wise max across all years
    for r in rasters[1:]:
        arr, _ = load_raster(r)
        period_max = np.nanmax(np.stack([period_max, arr]), axis=0)

    # Enforce Indo-Floods NaN mask
    fsi_arr, _ = load_raster(fsi_path)
    period_max[np.isnan(fsi_arr)] = np.nan

    # Save output
    out_path = hazard_max_dir / f"hazard_max_{scenario}_2027_2100.tif"
    save_raster(out_path, period_max, profile)
    print(f"Saved: {out_path}")


# ---------------------------------------------------------
# MAIN
# ---------------------------------------------------------

if __name__ == "__main__":
    compute_period_max("ssp370")
    compute_period_max("ssp585")
    print("Resilience design hazard layers complete.")

