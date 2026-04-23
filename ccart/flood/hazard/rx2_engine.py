"""
CCART Rx2 Engine (India-only CHIRPS grid, CMIP6 already on CHIRPS grid)

1. Load CHIRPS India-only clipped grid
2. Compute CHIRPS Rx2max per year
3. Compute CMIP6 Rx2max per year (SSP370, SSP585) directly on CHIRPS grid
4. Compute period-max for SSP370 and SSP585 on CHIRPS grid
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

# CHIRPS clipped grid
chirps_zarr = project_root / paths["flood"]["inputs"]["chirps_india_zarr"]

# CMIP6 daily rainfall already on CHIRPS grid
ssp370_pr_zarr = project_root / paths["flood"]["inputs"]["pr_370"]
ssp585_pr_zarr = project_root / paths["flood"]["inputs"]["pr_585"]

# Rx2 outputs
chirps_rx2_dir = project_root / paths["flood"]["outputs"]["rx2_chirps"]
ssp370_rx2_dir = project_root / paths["flood"]["outputs"]["rx2_ssp370"]
ssp585_rx2_dir = project_root / paths["flood"]["outputs"]["rx2_ssp585"]
period_max_dir = project_root / paths["flood"]["outputs"]["rx2_period_max"]

for d in [chirps_rx2_dir, ssp370_rx2_dir, ssp585_rx2_dir, period_max_dir]:
    d.mkdir(parents=True, exist_ok=True)


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
# GENERIC RX2 FROM ZARR
# ---------------------------------------------------------

def compute_rx2_per_year_from_zarr(zarr_path, out_dir, transform, var_name):
    ds = xr.open_zarr(zarr_path, consolidated=False)
    ds = xr.decode_cf(ds)

    da = ds[var_name]

    years = np.unique(da["time"].dt.year.values)

    for year in years:
        da_y = da.sel(time=str(year))
        if da_y.time.size < 2:
            continue

        rx2 = da_y.rolling(time=2).sum().max(dim="time")
        arr = rx2.values.astype("float32")

        out_path = out_dir / f"rx2max_{year}.tif"
        save_tif(out_path, arr, transform)
        print(f"[RX2] {zarr_path.name} {year} → {out_path.name}")


# ---------------------------------------------------------
# PERIOD MAX
# ---------------------------------------------------------

def compute_period_max(src_dir, out_path, transform):
    files = sorted(src_dir.glob("rx2max_*.tif"))
    if not files:
        print(f"[PERIOD MAX] No files in {src_dir}")
        return

    arrays = [rasterio.open(f).read(1) for f in files]
    period_max = np.max(arrays, axis=0)
    save_tif(out_path, period_max, transform)
    print(f"[PERIOD MAX] → {out_path}")


# ---------------------------------------------------------
# MAIN
# ---------------------------------------------------------

if __name__ == "__main__":

    print("Loading CHIRPS India grid...")
    lats, lons, transform = load_chirps_grid()

    # 1. CHIRPS Rx2max per year (variable likely 'precip' or first var)
    print("Computing CHIRPS Rx2max per year...")
    ds_ch = xr.open_zarr(chirps_zarr, consolidated=False)
    ds_ch = xr.decode_cf(ds_ch)
    chirps_var = "precip" if "precip" in ds_ch else list(ds_ch.data_vars.keys())[0]
    compute_rx2_per_year_from_zarr(chirps_zarr, chirps_rx2_dir, transform, chirps_var)

    # 2. CMIP6 SSP370 Rx2max per year (variable 'pr')
    print("Computing SSP370 Rx2max per year on CHIRPS grid...")
    compute_rx2_per_year_from_zarr(ssp370_pr_zarr, ssp370_rx2_dir, transform, "pr")

    # 3. CMIP6 SSP585 Rx2max per year (variable 'pr')
    print("Computing SSP585 Rx2max per year on CHIRPS grid...")
    compute_rx2_per_year_from_zarr(ssp585_pr_zarr, ssp585_rx2_dir, transform, "pr")

    # 4. Period max on CHIRPS grid
    print("Computing period-max for SSP370...")
    compute_period_max(
        ssp370_rx2_dir,
        period_max_dir / "rx2max_ssp370_2027_2100_chirps.tif",
        transform,
    )

    print("Computing period-max for SSP585...")
    compute_period_max(
        ssp585_rx2_dir,
        period_max_dir / "rx2max_ssp585_2027_2100_chirps.tif",
        transform,
    )

    print("Rx2 Engine complete.")
