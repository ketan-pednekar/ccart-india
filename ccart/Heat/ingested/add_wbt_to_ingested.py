import xarray as xr
from pathlib import Path
from ccart.Heat.hazard.wbt_engine import compute_wbt

paths = [
    r"C:\CMIP_data\cmip6\Climada\Projects\ccart-india\ccart\Heat\ingested\hist",
    r"C:\CMIP_data\cmip6\Climada\Projects\ccart-india\ccart\Heat\ingested\ssp370",
    r"C:\CMIP_data\cmip6\Climada\Projects\ccart-india\ccart\Heat\ingested\ssp585",
]

for p in paths:
    print(f"\n=== Updating WBT for: {p} ===")
    store = Path(p)

    ds = xr.open_zarr(store)

    if "wbt" in ds:
        print("WBT already exists — skipping.")
        continue

    tas = ds["tasmax"]
    hur = ds["hurs"]

    print("Computing WBT...")
    Tw = compute_wbt(tas, hur)

    print("Writing WBT to Zarr store...")
    ds["wbt"] = Tw
    ds.to_zarr(store, mode="a")

    print("✅ Done.")
