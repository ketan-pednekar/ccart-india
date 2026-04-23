"""
CCART-Floods v2 — CMIP6 → Zarr Processor (Append-by-time, no preallocation)
---------------------------------------------------------------------------
- Loads CMIP6 daily data (pr, tasmax)
- Resamples to CHIRPS reference grid (global or clipped)
- Writes year-by-year into Zarr using append_dim="time"
- No full (time, lat, lon) array is ever allocated
"""

from pathlib import Path
import numpy as np
import pandas as pd
import xarray as xr

from ccart.flood.config import load_paths, load_flood_params
from ccart.flood.ingest.ingest_cmip6 import load_cmip6


def ensure_output_dir(paths, model: str, scenario: str) -> Path:
    base = Path(paths["cmip6"]["processed_dir"])
    out = base / model / scenario
    out.mkdir(parents=True, exist_ok=True)
    return out


def process_variable_to_zarr(model: str, scenario: str, var: str):
    paths = load_paths()
    params = load_flood_params()

    start_year = params["future"]["start"]
    end_year = params["future"]["end"]

    cmip = load_cmip6(
        model=model,
        scenario=scenario,
        start_year=start_year,
        end_year=end_year,
    )

    if var == "pr":
        files = cmip["pr_files"]
        loader = cmip["load_pr_year"]
        units = "mm/day"
        long_name = "Daily precipitation"
    elif var == "tasmax":
        files = cmip["tasmax_files"]
        loader = cmip["load_tasmax_year"]
        units = "degC"
        long_name = "Daily maximum temperature"
    else:
        raise ValueError(f"Unsupported variable: {var}")

    ny, nx = cmip["shape"]
    lats = cmip["lats"]
    lons = cmip["lons"]
    crs = cmip["crs"]

    out_root = ensure_output_dir(paths, model, scenario)
    out_path = out_root / f"{var}.zarr"

    first = True

    for yr, row in files.iterrows():
        fp = row["path"]
        print(f"[{model} {scenario} {var}] Processing year {yr} → {fp.name}")

        arr = loader(fp)  # (time, ny, nx)
        tlen = arr.shape[0]

        time = pd.date_range(f"{yr}-01-01", periods=tlen, freq="D")

        ds_year = xr.Dataset(
            {
                var: (("time", "lat", "lon"), arr.astype("float32")),
            },
            coords={
                "time": time,
                "lat": lats,
                "lon": lons,
            },
            attrs={
                "model": model,
                "scenario": scenario,
                "crs": str(crs),
                "grid_mapping": "EPSG:4326",
                "description": f"CCART-processed CMIP6 {var} for {model} {scenario}",
            },
        )

        ds_year[var].attrs["units"] = units
        ds_year[var].attrs["long_name"] = long_name

        ds_year = ds_year.chunk({"time": tlen})

        if first:
            print(f"[{model} {scenario} {var}] Writing first year → {out_path}")
            ds_year.to_zarr(out_path, mode="w")
            first = False
        else:
            print(f"[{model} {scenario} {var}] Appending year {yr}")
            ds_year.to_zarr(out_path, mode="a", append_dim="time")

    print(f"[{model} {scenario} {var}] Completed Zarr store at {out_path}")


def main():
    model = "ACCESS-CM2"
    scenarios = ["ssp370", "ssp585"]

    for scenario in scenarios:
        for var in ["pr", "tasmax"]:
            process_variable_to_zarr(model, scenario, var)


if __name__ == "__main__":
    main()
