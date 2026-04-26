"""
CCART FSI Uplift Engine (CHIRPS-aligned grid)

FSI_uplift = FSI_static * (Rx2max_future / P95)

Inputs:
- static_fsi.tif (on CHIRPS grid)
- p95_chirps_2day.tif
- rx2max_ssp370_2027_2100_chirps.tif
- rx2max_ssp585_2027_2100_chirps.tif

Outputs:
- fsi_uplift_ssp370.tif
- fsi_uplift_ssp585.tif
"""

import rasterio
import numpy as np
from pathlib import Path

from ccart.flood.config import load_paths

# ---------------------------------------------------------
# PATHS
# ---------------------------------------------------------

paths = load_paths()
project_root = Path(paths["project_root"])

static_fsi_path = project_root / paths["flood"]["inputs"]["fsi"]
p95_path = project_root / paths["flood"]["inputs"]["p95"]

rx2_370_path = project_root / paths["flood"]["inputs"]["rx2_370"]
rx2_585_path = project_root / paths["flood"]["inputs"]["rx2_585"]


out_dir = project_root / paths["flood"]["outputs"]["fsi_uplift"]
out_dir.mkdir(parents=True, exist_ok=True)


# ---------------------------------------------------------
# UTILITIES
# ---------------------------------------------------------

def load_raster(path):
    with rasterio.open(path) as src:
        arr = src.read(1).astype("float32")
        profile = src.profile
    return arr, profile


def save_raster(path, array, profile):
    profile.update(dtype="float32", compress="lzw")
    with rasterio.open(path, "w", **profile) as dst:
        dst.write(array.astype("float32"), 1)


# ---------------------------------------------------------
# FSI UPLIFT (with Indo-Floods NaN mask)
# ---------------------------------------------------------

def compute_fsi_uplift(static_fsi, p95, rx2_future):
    # basic uplift ratio
    ratio = np.divide(rx2_future, p95, out=np.zeros_like(rx2_future), where=p95 > 0)
    uplift = static_fsi * ratio

    # enforce Indo-Floods mask: wherever static FSI is NaN, keep NaN
    mask = np.isnan(static_fsi)
    uplift[mask] = np.nan

    return uplift


# ---------------------------------------------------------
# MAIN
# ---------------------------------------------------------

if __name__ == "__main__":

    print("Loading static FSI...")
    fsi_static, profile = load_raster(static_fsi_path)

    print("Loading P95...")
    p95, _ = load_raster(p95_path)

    print("Loading Rx2max SSP370...")
    rx2_370, _ = load_raster(rx2_370_path)

    print("Loading Rx2max SSP585...")
    rx2_585, _ = load_raster(rx2_585_path)

    print("Computing FSI uplift for SSP370...")
    uplift_370 = compute_fsi_uplift(fsi_static, p95, rx2_370)
    save_raster(out_dir / "fsi_uplift_ssp370.tif", uplift_370, profile)

    print("Computing FSI uplift for SSP585...")
    uplift_585 = compute_fsi_uplift(fsi_static, p95, rx2_585)
    save_raster(out_dir / "fsi_uplift_ssp585.tif", uplift_585, profile)

    print("FSI uplift engine complete.")
