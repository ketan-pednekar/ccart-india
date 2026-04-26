"""
Compute historical hazard-max for CCART-Floods
Period: 1995–2024

Input:
    hazard_hist_annual/hazard_hist_YYYY.tif

Output:
    hazard_hist_max/hazard_max_hist_1995_2024.tif
"""

import numpy as np
import rasterio
from pathlib import Path
from ccart.flood.config import load_paths


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


if __name__ == "__main__":

    paths = load_paths()
    project_root = Path(paths["project_root"])

    annual_dir = project_root / paths["flood"]["outputs"]["hazard_hist_annual"]
    out_dir = project_root / paths["flood"]["outputs"]["hazard_hist_max"]
    out_dir.mkdir(parents=True, exist_ok=True)

    # FSI mask (canonical Indo-Floods domain)
    fsi_path = project_root / paths["flood"]["inputs"]["fsi"]
    fsi_arr, _ = load_raster(fsi_path)
    nan_mask = np.isnan(fsi_arr)

    print("Scanning annual historical hazard files...")
    files = sorted(annual_dir.glob("hazard_hist_*.tif"))

    if len(files) == 0:
        raise RuntimeError("No historical hazard files found.")

    # Load first raster to initialize max array
    first_arr, profile = load_raster(files[0])
    max_arr = first_arr.copy()

    print(f"Found {len(files)} annual hazard rasters.")

    # Pixel-wise nanmax across all years
    for f in files[1:]:
        arr, _ = load_raster(f)
        max_arr = np.nanmax(np.stack([max_arr, arr]), axis=0)

    # Enforce Indo-Floods NaN mask
    max_arr[nan_mask] = np.nan

    out_path = out_dir / "hazard_max_hist_1995_2024.tif"
    print(f"Saving historical hazard-max to: {out_path}")

    save_raster(out_path, max_arr, profile)

    print("Historical hazard-max complete.")
