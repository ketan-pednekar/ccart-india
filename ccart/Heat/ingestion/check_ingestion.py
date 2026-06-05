import xarray as xr
from pathlib import Path
from ccart.Heat.config import load_heat_paths

p = load_heat_paths()

HIST = Path(p["ingested"]["hist"])
SSP370 = Path(p["ingested"]["ssp370"])
SSP585 = Path(p["ingested"]["ssp585"])

def check(ds, name):
    print(f"\n--- Checking {name} ---")
    print("Variables:", list(ds.data_vars))
    print("Time range:", str(ds.time.values[0]), "→", str(ds.time.values[-1]))
    print("Lat range:", float(ds.lat.min()), "→", float(ds.lat.max()))
    print("Lon range:", float(ds.lon.min()), "→", float(ds.lon.max()))
    print("tasmax min/max:", float(ds.tasmax.min()), float(ds.tasmax.max()))
    print("hurs   min/max:", float(ds.hurs.min()), float(ds.hurs.max()))
    print("NaN % tasmax:", float(ds.tasmax.isnull().mean()) * 100)
    print("NaN % hurs:", float(ds.hurs.isnull().mean()) * 100)

# Load datasets
ds_hist = xr.open_zarr(HIST)
ds_370  = xr.open_zarr(SSP370)
ds_585  = xr.open_zarr(SSP585)

check(ds_hist, "Historical")
check(ds_370, "SSP370")
check(ds_585, "SSP585")

print("dlat:", float(ds_hist.lat[1] - ds_hist.lat[0]))
print("dlon:", float(ds_hist.lon[1] - ds_hist.lon[0]))
