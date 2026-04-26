"""
CCART Historical Hazard Engine (1995–2024)

Computes annual historical flood hazard layers using:
    - CHIRPS daily rainfall (pr_hist)
    - 2-day rolling rainfall exceedance over P95
    - Indo-Floods FSI static mask

Output:
    hazard_hist_YYYY.tif  for 1995–2024
"""

import numpy as np
import xarray as xr
import rasterio
from pathlib import Path
from ccart.flood.config import load_paths


# ---------------------------------------------------------
# PATHS
# ---------------------------------------------------------

paths = load_paths()
project_root = Path(paths["project_root"])

# Historical rainfall (CHIRPS India clipped)
pr_hist_path = project_root / paths["flood"]["inputs"]["pr_hist"]

# P95 (2-day rainfall threshold)
p95_path = project_root / paths["flood"]["inputs"]["p95"]

# FSI static (Indo-Floods mask)
fsi_path = project_root / paths["flood"]["inputs"]["fsi"]

# Output directory for annual historical hazard
hazard_hist_dir = project_root / paths["flood"]["outputs"]["hazard_hist_annual"]
hazard_hist_dir.mkdir(parents=True, exist_ok=True)


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
# MAIN
# ---------------------------------------------------------

if __name__ == "__main__":

    print("Loading historical CHIRPS rainfall...")
    ds = xr.open_zarr(pr_hist_path)
    pr = ds["pr"]  # mm/day

    print("Loading P95 threshold...")
    p95_arr, profile = load_raster(p95_path)

    print("Loading FSI static mask...")
    fsi_arr, _ = load_raster(fsi_path)

    # 2-day rolling rainfall
    print("Computing 2-day rolling rainfall...")
    pr2 = pr.rolling(time=2).sum().isel(time=slice(1, None))

    # Group by year
    pr2_year = pr2.groupby("time.year")

    for year in range(1995, 2025):

        if year not in pr2_year.groups:
            print(f"Skipping {year} (no data)")
            continue

        print(f"Processing year {year}...")

        # Robust indexing using group indices
        indices = pr2_year.groups[year]
        pr2_y = pr2.isel(time=indices)

        # Exceedance count
        exceed = (pr2_y > p95_arr).sum(dim="time")
        exceed_arr = exceed.values.astype("float32")

        # Apply FSI static
        hazard = exceed_arr * fsi_arr
        hazard[np.isnan(fsi_arr)] = np.nan

        # Save output
        out_path = hazard_hist_dir / f"hazard_hist_{year}.tif"
        save_raster(out_path, hazard, profile)

        print(f"Saved: {out_path}")


    print("Historical hazard engine complete.")
