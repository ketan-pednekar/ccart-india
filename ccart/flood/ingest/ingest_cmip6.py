"""
CCART-Floods — CMIP6 ingestion (multi-model ready, ACCESS-CM2 configured)

Responsibilities:
- Read CMIP6 daily pr and tasmax from folders defined in paths.yaml
- Inventory files by year for a given model + scenario
- Align CMIP6 to the CHIRPS/FSI 0.05° reference grid
  (global or region-clipped, as defined by chirps_ingest)
- Convert units:
    pr: kg m-2 s-1 → mm/day
    tasmax: K → °C
- Expose simple loaders for year-wise arrays

Usage:

    from ccart.flood.ingest.ingest_cmip6 import load_cmip6

    cmip = load_cmip6(model="ACCESS-CM2", scenario="ssp370",
                      start_year=2027, end_year=2100)

    pr_2030 = cmip["load_pr_year"](cmip["pr_files"].loc[2030, "path"])
"""

from __future__ import annotations

from pathlib import Path
import re
from typing import Dict, Callable, Tuple

import numpy as np
import pandas as pd
import xarray as xr
import rasterio

from ccart.flood.config import load_paths
from ccart.flood.ingest.ingest_chirps import load_chirps

def _get_chirps_grid(paths: Dict) -> Tuple[np.ndarray, np.ndarray, rasterio.Affine, rasterio.crs.CRS]:
    """
    Get CHIRPS reference grid (lat, lon, transform, crs) from chirps_ingest.

    This respects:
    - clip_to_region
    - region_boundary

    so CMIP6 is always regridded to the same grid used by CHIRPS/FSI.
    """
    chirps = load_chirps()

    ny, nx = chirps["shape"]
    transform = chirps["transform"]
    crs = chirps["crs"]

    # Build lon/lat centers from transform and shape
    xs = np.arange(nx)
    ys = np.arange(ny)

    # x = col, y = row
    lons = transform.c + (xs + 0.5) * transform.a
    lats = transform.f + (ys + 0.5) * transform.e

    return lats, lons, transform, crs


def _inventory_nc_files(dir_path: Path) -> pd.DataFrame:
    """
    Inventory NetCDF files in a directory and extract year from filename.

    Expects filenames containing a 4-digit year, e.g.:
        pr_day_ACCESS-CM2_ssp370_2030.nc
        tasmax_day_ACCESS-CM2_ssp585_2075.nc
    """
    if not dir_path.exists():
        raise FileNotFoundError(f"CMIP6 directory not found: {dir_path}")

    records = []
    for fp in sorted(dir_path.glob("*.nc")):
        m = re.search(r"(\d{4})", fp.name)
        if not m:
            continue
        year = int(m.group(1))
        records.append({"year": year, "path": fp})

    if not records:
        raise RuntimeError(f"No NetCDF files with year in name found in {dir_path}")

    df = pd.DataFrame(records).set_index("year").sort_index()
    return df


def load_cmip6(model: str = "ACCESS-CM2",
               scenario: str = "ssp370",
               start_year: int | None = None,
               end_year: int | None = None) -> Dict:
    """
    Main CMIP6 ingestion entrypoint.

    Returns a dict with:
        - model, scenario
        - shape, transform, crs
        - pr_files: DataFrame indexed by year with 'path'
        - tasmax_files: same
        - load_pr_year(path) -> np.ndarray[time, y, x]
        - load_tasmax_year(path) -> np.ndarray[time, y, x]
    """
    paths = load_paths()

    if "cmip6" not in paths or model not in paths["cmip6"]:
        raise KeyError(f"Model {model} not configured in paths.yaml under 'cmip6'")

    model_cfg = paths["cmip6"][model]
    if scenario not in model_cfg:
        raise KeyError(f"Scenario {scenario} not configured for model {model} in paths.yaml")

    scen_cfg = model_cfg[scenario]
    pr_dir = Path(scen_cfg["pr_dir"])
    tasmax_dir = Path(scen_cfg["tasmax_dir"])

    pr_files = _inventory_nc_files(pr_dir)
    tasmax_files = _inventory_nc_files(tasmax_dir)

    if start_year is not None:
        pr_files = pr_files.loc[pr_files.index >= start_year]
        tasmax_files = tasmax_files.loc[tasmax_files.index >= start_year]
    if end_year is not None:
        pr_files = pr_files.loc[pr_files.index <= end_year]
        tasmax_files = tasmax_files.loc[tasmax_files.index <= end_year]

    if pr_files.empty:
        raise RuntimeError(f"No pr files in requested range for {model} {scenario}")
    if tasmax_files.empty:
        raise RuntimeError(f"No tasmax files in requested range for {model} {scenario}")

    lats, lons, transform, crs = _get_chirps_grid(paths)
    ny, nx = len(lats), len(lons)

    def _regrid_to_chirps(ds: xr.Dataset, var: str) -> np.ndarray:
        """
        Regrid CMIP6 data to CHIRPS reference grid using xarray.interp.
        Respects clipped or global grid via lats/lons from _get_chirps_grid.
        """
        # Ensure lat ascending for interp
        if ds.lat.values[0] > ds.lat.values[-1]:
            ds = ds.sortby("lat")

        ds_interp = ds[var].interp(lat=lats, lon=lons, method="linear")
        arr = ds_interp.values.astype("float32")
        return arr  # shape: (time, ny, nx)

    def _load_pr_year(nc_path: Path) -> np.ndarray:
        """
        Load one year of pr, convert units, regrid to CHIRPS grid.
        pr: kg m-2 s-1 → mm/day (multiply by 86400)
        """
        ds = xr.open_dataset(nc_path)
        if "pr" not in ds:
            raise KeyError(f"'pr' variable not found in {nc_path}")

        ds = ds.load()
        ds["pr"] = ds["pr"] * 86400.0  # kg m-2 s-1 → mm/day
        arr = _regrid_to_chirps(ds, "pr")
        ds.close()
        return arr

    def _load_tasmax_year(nc_path: Path) -> np.ndarray:
        """
        Load one year of tasmax, convert units, regrid to CHIRPS grid.
        tasmax: K → °C (subtract 273.15)
        """
        ds = xr.open_dataset(nc_path)
        if "tasmax" not in ds:
            raise KeyError(f"'tasmax' variable not found in {nc_path}")

        ds = ds.load()
        ds["tasmax"] = ds["tasmax"] - 273.15
        arr = _regrid_to_chirps(ds, "tasmax")
        ds.close()
        return arr

    return {
        "model": model,
        "scenario": scenario,
        "shape": (ny, nx),
        "transform": transform,
        "crs": crs,
        "lats": lats,
        "lons": lons,
        "pr_files": pr_files,
        "tasmax_files": tasmax_files,
        "load_pr_year": _load_pr_year,
        "load_tasmax_year": _load_tasmax_year,
    }
