"""
CCART P95 Engine (India-only CHIRPS grid)

1. Load CHIRPS India-only clipped grid
2. Compute 2-day rolling rainfall
3. Compute P95 over entire CHIRPS period
4. Save as GeoTIFF on CHIRPS grid
"""

import xarray as xr
import numpy as np
from pathlib import Path
import rasterio
from rasterio.transform import from_bounds
from ccart.flood.config import load_paths

# ---------------------------------------------------------
# PATHS
# ---------------------------------------------------------


paths = load_paths()
project_root = Path(paths["project_root"])

chirps_zarr = project_root / paths["flood"]["inputs"]["chirps_india_zarr"]

p95_dir = project_root / paths["flood"]["outputs"]["p95"]
p95_dir.mkdir(parents=True, exist_ok=True)



# ---------------------------------------------------------
# GRID + UTILITIES
# ---------------------------------------------------------

def load_chirps_grid():
    ds = xr.open_zarr(chirps_zarr, consolidated=False)
    ds = xr.decode_cf(ds)

    # pick main variable
    if "precip" in ds:
        da = ds["precip"]
    else:
        da = list(ds.data_vars.values())[0]

    lats = da["lat"].values
    lons = da["lon"].values

    min_lon, max_lon = float(lons.min()), float(lons.max())
    min_lat, max_lat = float(lats.min()), float(lats.max())

    transform = from_bounds(min_lon, min_lat, max_lon, max_lat,
                            len(lons), len(lats))

    return lats, lons, transform


def save_tif(path, array, transform):
    profile = {
        "driver": "GTiff",
        "height": array.shape[0],
        "width": array.shape[1],
        "count": 1,
        "dtype": "float32",
        "crs": "EPSG:4326",
        "transform": transform,
        "compress": "lzw",
    }
    with rasterio.open(path, "w", **profile) as dst:
        dst.write(array.astype("float32"), 1)


# ---------------------------------------------------------
# P95 ENGINE
# ---------------------------------------------------------

def compute_p95(transform):
    ds = xr.open_zarr(chirps_zarr, consolidated=False)
    ds = xr.decode_cf(ds)

    # CHIRPS variable
    if "precip" in ds:
        da = ds["precip"]
    else:
        da = list(ds.data_vars.values())[0]

    # 2-day rolling rainfall
    r2 = da.rolling(time=2).sum()

    # 95th percentile across entire time dimension
    p95 = r2.quantile(0.95, dim="time")

    arr = p95.values.astype("float32")

    out_path = p95_dir / "p95_chirps_2day.tif"
    save_tif(out_path, arr, transform)

    print(f"[P95] → {out_path}")


# ---------------------------------------------------------
# MAIN
# ---------------------------------------------------------

if __name__ == "__main__":

    print("Loading CHIRPS India grid...")
    lats, lons, transform = load_chirps_grid()

    print("Computing P95 (2-day rainfall)...")
    compute_p95(transform)

    print("P95 Engine complete.")
