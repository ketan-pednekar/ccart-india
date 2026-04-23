"""
CCART Dynamic Flood Hazard Engine

For each scenario (SSP370, SSP585):

1. Load daily rainfall (ACCESS-CM2, CHIRPS-aligned, 2027–2100)
2. Compute 2-day rolling rainfall
3. Count exceedances over P95 (2-day)
4. Multiply exceedance counts by FSI uplift (scenario-specific)
5. Save annual hazard rasters:

   hazard_ssp370_YYYY.tif
   hazard_ssp585_YYYY.tif
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

# CMIP6 daily rainfall (CHIRPS-aligned)
pr_370_zarr = project_root / paths["flood"]["inputs"]["pr_370"]
pr_585_zarr = project_root / paths["flood"]["inputs"]["pr_585"]

# P95 (2-day rainfall)
p95_path = project_root / paths["flood"]["inputs"]["p95"]

# FSI uplift rasters
fsi_uplift_370_path = project_root / paths["flood"]["inputs"]["fsi_uplift_370"]
fsi_uplift_585_path = project_root / paths["flood"]["inputs"]["fsi_uplift_585"]

# Output directory for hazard rasters
hazard_out_dir = project_root / paths["flood"]["outputs"]["hazard"]
hazard_out_dir.mkdir(parents=True, exist_ok=True)



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


def load_pr_dataset(zarr_path):
    # Assumes pr is already in mm/day and CHIRPS-aligned
    ds = xr.open_zarr(zarr_path)
    # Standard name: 'pr'; adjust here if different
    if "pr" not in ds:
        raise ValueError(f"'pr' variable not found in {zarr_path}")
    return ds


# ---------------------------------------------------------
# HAZARD COMPUTATION
# ---------------------------------------------------------

def compute_hazard_for_scenario(
    ds_pr,
    p95_arr,
    uplift_arr,
    profile,
    scenario_label,
    start_year=2027,
    end_year=2100,
):
    """
    ds_pr: xarray Dataset with variable 'pr' [time, lat, lon]
    p95_arr: 2D numpy array [lat, lon]
    uplift_arr: 2D numpy array [lat, lon]
    profile: rasterio profile (from P95)
    scenario_label: 'ssp370' or 'ssp585'
    """

    pr = ds_pr["pr"]

    # 2-day rolling sum along time
    pr2 = pr.rolling(time=2).sum().isel(time=slice(1, None))

    # group by year
    pr2_year = pr2.groupby("time.year")

    for year in range(start_year, end_year + 1):
        if year not in pr2_year.groups:
            continue

        print(f"[{scenario_label}] Computing hazard for year {year}...")

        # universal xarray-safe way to extract a group
        indices = pr2_year.groups[year]      # integer positions of that year's timesteps
        pr2_y = pr2.isel(time=indices)       # slice the original pr2 by those indices

        # exceedance count over P95
        # broadcast p95_arr to match pr2_y shape
        exceed = (pr2_y > p95_arr).sum(dim="time")

        # to numpy
        exceed_arr = exceed.values.astype("float32")

        # apply FSI uplift (already carries Indo-Floods NaN mask)
        hazard = exceed_arr * uplift_arr

        # enforce NaN where uplift is NaN
        mask_nan = np.isnan(uplift_arr)
        hazard[mask_nan] = np.nan

        out_path = hazard_out_dir / f"hazard_{scenario_label}_{year}.tif"
        save_raster(out_path, hazard, profile)


# ---------------------------------------------------------
# MAIN
# ---------------------------------------------------------

if __name__ == "__main__":

    print("Loading P95 raster...")
    p95_arr, profile = load_raster(p95_path)

    print("Loading FSI uplift SSP370...")
    fsi_uplift_370, _ = load_raster(fsi_uplift_370_path)

    print("Loading FSI uplift SSP585...")
    fsi_uplift_585, _ = load_raster(fsi_uplift_585_path)

    print("Loading CMIP6 pr.zarr for SSP370...")
    ds_370 = load_pr_dataset(pr_370_zarr)

    print("Loading CMIP6 pr.zarr for SSP585...")
    ds_585 = load_pr_dataset(pr_585_zarr)

    # Ensure shapes match
    if p95_arr.shape != fsi_uplift_370.shape:
        raise ValueError(f"P95 and FSI uplift 370 shapes differ: {p95_arr.shape} vs {fsi_uplift_370.shape}")
    if p95_arr.shape != fsi_uplift_585.shape:
        raise ValueError(f"P95 and FSI uplift 585 shapes differ: {p95_arr.shape} vs {fsi_uplift_585.shape}")

    # SSP370
    compute_hazard_for_scenario(
        ds_pr=ds_370,
        p95_arr=p95_arr,
        uplift_arr=fsi_uplift_370,
        profile=profile,
        scenario_label="ssp370",
        start_year=2027,
        end_year=2100,
    )

    # SSP585
    compute_hazard_for_scenario(
        ds_pr=ds_585,
        p95_arr=p95_arr,
        uplift_arr=fsi_uplift_585,
        profile=profile,
        scenario_label="ssp585",
        start_year=2027,
        end_year=2100,
    )

    print("Dynamic hazard engine complete.")
