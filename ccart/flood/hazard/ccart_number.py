"""
CCART Number Engine

Definition:
    CCART_Number = H_max_future / H_max_historical

Inputs:
    hazard_max_hist_1995_2024.tif
    hazard_max_ssp370_2027_2100.tif
    hazard_max_ssp585_2027_2100.tif
    fsi_static.tif  (Indo-Floods domain mask)

Outputs:
    ccart_number_ssp370.tif
    ccart_number_ssp585.tif
"""

import numpy as np
import rasterio
from pathlib import Path
from ccart.flood.config import load_paths


# ---------------------------------------------------------
# UTILITIES
# ---------------------------------------------------------

def load_raster(path):
    with rasterio.open(path) as src:
        arr = src.read(1).astype("float32")
        profile = src.profile
    return arr, profile


def save_raster(path, array, profile, min_hist=None, max_ratio=None):
    profile = profile.copy()
    profile.update(dtype="float32", compress="lzw")

    # Optional CCART metadata
    if min_hist is not None:
        profile["CCART_MIN_HIST"] = float(min_hist)
    if max_ratio is not None:
        profile["CCART_MAX_RATIO"] = float(max_ratio)

    with rasterio.open(path, "w", **profile) as dst:
        dst.write(array.astype("float32"), 1)


# ---------------------------------------------------------
# MAIN
# ---------------------------------------------------------

if __name__ == "__main__":

    paths = load_paths()
    project_root = Path(paths["project_root"])

    # Inputs
    hist_max_path = project_root / paths["flood"]["outputs"]["hazard_hist_max"] / "hazard_max_hist_1995_2024.tif"
    fut370_max_path = project_root / paths["flood"]["outputs"]["hazard_max"] / "hazard_max_ssp370_2027_2100.tif"
    fut585_max_path = project_root / paths["flood"]["outputs"]["hazard_max"] / "hazard_max_ssp585_2027_2100.tif"
    fsi_path = project_root / paths["flood"]["inputs"]["fsi"]

    print("Loading historical hazard-max...")
    hist_max, profile = load_raster(hist_max_path)

    print("Loading future hazard-max (SSP370)...")
    fut370_max, _ = load_raster(fut370_max_path)

    print("Loading future hazard-max (SSP585)...")
    fut585_max, _ = load_raster(fut585_max_path)

    print("Loading FSI static mask...")
    fsi_arr, _ = load_raster(fsi_path)
    nan_mask = np.isnan(fsi_arr)

    # ---------------------------------------------------------
    # CCART NUMBER COMPUTATION (clean + stable)
    # ---------------------------------------------------------

    MIN_HIST = 0.01     # minimum historical hazard threshold
    MAX_RATIO = 50.0    # cap extreme ratios

    def compute_ccart_number(fut_max, hist_max, nan_mask):
        # 1. Start with NaNs everywhere
        out = np.full_like(hist_max, np.nan, dtype="float32")

        # 2. Valid where historical hazard is meaningful
        valid = (hist_max > MIN_HIST) & (~nan_mask)

        # 3. Compute ratio only on valid pixels
        out[valid] = fut_max[valid] / hist_max[valid]

        # 4. Cap extreme values
        out = np.clip(out, 0, MAX_RATIO)

        return out


    print("Computing CCART Number (SSP370)...")
    ccart_370 = compute_ccart_number(fut370_max, hist_max, nan_mask)

    print("Computing CCART Number (SSP585)...")
    ccart_585 = compute_ccart_number(fut585_max, hist_max, nan_mask)


    # ---------------------------------------------------------
    # SAVE OUTPUTS
    # ---------------------------------------------------------

    out_dir = project_root / paths["flood"]["outputs"]["hazard_max"]
    out_370 = out_dir / "ccart_number_ssp370.tif"
    out_585 = out_dir / "ccart_number_ssp585.tif"

    print("Saving CCART Number rasters...")
    save_raster(out_370, ccart_370, profile, MIN_HIST, MAX_RATIO)
    save_raster(out_585, ccart_585, profile, MIN_HIST, MAX_RATIO)

    print("CCART Number computation complete.")
