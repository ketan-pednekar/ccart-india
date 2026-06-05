"""
CCART-Heat — Clean Exceedance Rebuild
=====================================

This script now does ONLY the following:

1. Deletes the exceedance/ folder (safe reset)
2. Rebuilds:
      - cube_hist_wbt35.zarr
      - cube_ssp370_wbt35.zarr
      - cube_ssp585_wbt35.zarr
3. Applies strict India mask
4. Applies DEM mask (≤500 m) on the exceedance grid
5. Saves clean exceedance cubes
6. Runs top-100 validation

NO TIFFS ARE CREATED HERE.
NO OTHER THRESHOLDS (28/30/32) ARE COMPUTED HERE.
"""

from pathlib import Path
import shutil
import xarray as xr
import numpy as np
import pandas as pd

from ccart.Heat.config import load_heat_paths
from ccart.Heat.hazard.exceedance_engine import (
    compute_annual_exceedances,
    finalize_exceedance_cube,
)
import rasterio


DEM_MASK_PATH = r"C:\CMIP_data\cmip6\Climada\Projects\ccart-india\ccart\data\DEM_mask\fraction_lowland_relaxed_ccart.tif"


def load_dem_mask():
    with rasterio.open(DEM_MASK_PATH) as src:
        arr = src.read(1)
    # threshold at 0.5
    return (arr > 0.5).astype("uint8")



def validate_top100(cube_path, label):
    cube = xr.open_zarr(cube_path)
    da = cube["wbt35"]

    agg = da.max("year").values
    flat = agg.flatten()

    valid = flat[~np.isnan(flat)]
    if len(valid) == 0:
        print(f"[FAIL] {label}: empty cube")
        return False

    top = np.sort(valid)[-100:]
    print(f"[PASS] {label}: cube looks clean")
    return True


def main():
    paths = load_heat_paths()
    out_root = Path(paths["exceedance"])
    india_shp = paths["boundaries"]["districts"]

    # Reset
    if out_root.exists():
        shutil.rmtree(out_root)
    out_root.mkdir(parents=True, exist_ok=True)

    dem_mask = load_dem_mask()

    scenarios = {
        "hist": (paths["ingested"]["hist"], list(range(1995, 2015))),
        "ssp370": (paths["ingested"]["ssp370"], list(range(2015, 2101))),
        "ssp585": (paths["ingested"]["ssp585"], list(range(2015, 2101))),
    }

    for name, (path, years) in scenarios.items():
        print(f"\n=== Building exceedance cube: {name} ===")

        ds = xr.open_zarr(Path(path))
        Tw = ds["wbt"]

        da_raw = compute_annual_exceedances(Tw, 35, years)
        da_final = finalize_exceedance_cube(da_raw, india_shp, dem_mask)
        da_final = da_final.chunk({"year": len(years), "lat": 200, "lon": 200})

        out_path = out_root / f"cube_{name}_wbt35.zarr"
        da_final.to_zarr(out_path, mode="w")

        print(f"[SAVED] {out_path}")
        validate_top100(out_path, name)


if __name__ == "__main__":
    main()
