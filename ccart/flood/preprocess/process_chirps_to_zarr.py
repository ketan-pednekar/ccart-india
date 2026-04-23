"""
CHIRPS → Zarr (clipped India grid)

Creates a historical rainfall cube aligned with CMIP6 Zarr stores.
Used for:
- RX1day / RX2day diagnostics
- Static FSI baseline
- Exposure alignment
- Historical validation

Output:
    ccart/outputs/chirps_india/chirps.zarr
"""

from pathlib import Path
import xarray as xr
import numpy as np

from ccart.flood.ingest.ingest_chirps import load_chirps
from ccart.flood.config import load_paths

def process_chirps_to_zarr():
    print("DEBUG: process_chirps_to_zarr() started")
    paths = load_paths()
    chirps_cfg = paths["chirps"]

    out_dir = Path("ccart/outputs/chirps_india")
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / "chirps.zarr"

    ch = load_chirps()
    years = ch["years"]
    load_day = ch["load_day"]
    lats = ch["lats"]
    lons = ch["lons"]

    print(f"CHIRPS years: {years}")
    print(f"Output Zarr: {out_path}")

    first = True

    for year in years:
        print(f"[CHIRPS] Processing year {year}")

        # All CHIRPS files for this year
        year_df = ch["file_df"][ch["file_df"]["year"] == year]

        daily_arrays = []
        valid_dates = []

        for _, row in year_df.iterrows():
            fp = row["path"]
            y, m, d = row["year"], row["month"], row["day"]

            try:
                arr, _ = load_day(fp)
                daily_arrays.append(arr)
                valid_dates.append(f"{y:04d}-{m:02d}-{d:02d}")
            except Exception as e:
                print(f"[CHIRPS] WARNING: Could not read {fp} → {e}")
                continue

        if len(daily_arrays) == 0:
            print(f"[CHIRPS] WARNING: No valid days for year {year}, skipping.")
            continue

        # Stack into (time, ny, nx)
        arr = np.stack(daily_arrays, axis=0)

        # Build time coordinate
        time = xr.cftime_range(start=valid_dates[0], periods=len(valid_dates), freq="D")

        # Build Dataset
        ds = xr.Dataset(
            {"pr": (("time", "lat", "lon"), arr.astype("float32"))},
            coords={"time": time, "lat": lats, "lon": lons},
            attrs={
                "description": "CHIRPS daily rainfall (mm/day), clipped to India",
                "source": chirps_cfg["root"],
            },
        )

        if first:
            print(f"[CHIRPS] Writing first year → {out_path}")
            ds.to_zarr(out_path, mode="w")
            first = False
        else:
            print(f"[CHIRPS] Appending year {year}")
            ds.to_zarr(out_path, mode="a", append_dim="time")

    print("CHIRPS → Zarr complete.")

if __name__ == "__main__":
    process_chirps_to_zarr()
