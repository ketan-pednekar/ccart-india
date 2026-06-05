"""
CCART-Heat Exceedance Engine (0.05° India Grid, wbt35, center-aligned)
=====================================================================

- Computes annual exceedance counts for wet bulb temperature thresholds
  (28°C, 30°C, 32°C, 35°C) on the canonical CCART 0.05° India grid.
- Fully aligned with ingestion grid and Zarr cubes.
- GeoTIFF writer uses center-aligned transform:
    x0 = lon.min() - dx/2
    y0 = lat.max() + dy/2
"""

# ccart/Heat/hazard/exceedance_engine.py

import numpy as np
import xarray as xr
from ccart.Heat.utils.strict_india_mask import make_strict_mask


def compute_annual_exceedances(Tw: xr.DataArray, threshold: float, years):
    """
    Compute annual exceedance counts for WBT > threshold.
    Tw: DataArray [time, lat, lon] with 'time' coordinate.
    """
    da = (Tw > threshold).groupby("time.year").sum("time")
    da = da.sel(year=years)
    return da


def apply_dem_mask(da: xr.DataArray, dem_mask: np.ndarray) -> xr.DataArray:
    """
    Apply DEM mask (0 = masked, 1 = keep) to an exceedance DataArray [year, lat, lon].
    """
    arr = da.values.astype("float32")
    if arr.shape[1:] != dem_mask.shape:
        raise ValueError(f"DEM mask shape {dem_mask.shape} != data shape {arr.shape[1:]}")
    arr[:, dem_mask == 0] = 0.0
    da.values[:] = arr
    return da


def finalize_exceedance_cube(
    da_raw: xr.DataArray,
    india_shp_path,
    dem_mask: np.ndarray,
) -> xr.DataArray:
    """
    Take raw annual exceedance [year, lat, lon] and:
    - ensure lat is north→south
    - apply strict India mask
    - apply DEM mask
    - rename to 'wbt35'
    """

    # 1. Ensure lat is north→south
    lat = da_raw.lat.values
    if lat[0] < lat[-1]:
        da_raw = da_raw.isel(lat=slice(None, None, -1))
        lat = lat[::-1]
        da_raw = da_raw.assign_coords(lat=lat)

    # 2. Strict India mask on this grid
    strict_mask = make_strict_mask(da_raw, india_shp_path).astype(bool)
    da = da_raw.where(strict_mask)

    # 3. DEM mask
    da = apply_dem_mask(da, dem_mask)

    # 4. Rename variable
    da = da.rename("wbt35")

    return da
