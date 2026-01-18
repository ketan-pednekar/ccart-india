from ccart.engine import run_ccart
from ccart.viz import ccart_choropleth
from ccart import engine
import geopandas as gpd
import pandas as pd
import os

print("Engine file:", engine.run_ccart.__code__.co_filename)
print("Hazard floor:", engine.HAZARD_FLOOR_MS)

# === Run CCART for Cyclone Vardah ===
gdf = run_ccart(
    cyclone_name="Vardah",
    storm_id="2016341N08092",   # SID for Vardah
    ibtracs_path=r"C:\CMIP data\cmip6\Climada\Projects\ccart-india\data\IBTRACS.ALL.v04r01.nc",
    districts_path=r"C:\CMIP data\cmip6\Climada\Projects\ccart-india\data\INDIA_DISTRICTS.geojson",

    dlna_total=1000e6,          # India DLNA ≈ USD 1.0B
    state_name="TAMIL NADU",
    inland_clip_km=150,
    coastline_path=r"C:\CMIP data\cmip6\Climada\Projects\ccart-india\data\coastl_ind.shp"
)

print(gdf.head())
print(gdf.columns)
print("Total impact:", gdf["loss_usd_hwe"].sum())

# === Diagnostics ===
print("\n=== Top 10 districts by CCART loss ===")
print(
    gdf[["District", "loss_usd_hwe"]]
    .sort_values("loss_usd_hwe", ascending=False)
    .head(10)
)

print("\n=== Top 10 districts by HWE weight ===")
print(
    gdf[["District", "HWE_weight_norm"]]
    .sort_values("HWE_weight_norm", ascending=False)
    .head(10)
)

print("\n=== Top 10 districts by raw CLIMADA loss ===")
print(
    gdf[["District", "loss_usd_raw"]]
    .sort_values("loss_usd_raw", ascending=False)
    .head(10)
)

# === EXPORT TO MASTER RELATIONSHIP CSV ===
import os
import pandas as pd

master_path = r"C:\CMIP data\cmip6\Climada\Projects\ccart-india\data\district_relationships_master.csv"

# === CYCLONE METADATA (EDIT PER CYCLONE) ===
sid = "2016341N08092"
cyclone_name = "Vardah"
year = 2016
dlna_total = 1000e6
calibration_state = "TAMIL NADU"

gdf["sid"] = sid
gdf["cyclone_name"] = cyclone_name
gdf["year"] = year
gdf["dlna_total"] = dlna_total
gdf["calibration_state"] = calibration_state

cols = [
    "sid", "cyclone_name", "year", "state", "District",
    "loss_usd_raw", "HWE_weight_norm", "loss_usd_hwe",
    "dlna_total", "calibration_state",
    "dist_to_coast_km", "is_inland"
]

out = gdf[cols].copy()

# === REMOVE OLD ROWS FOR THIS SID (IF ANY) ===
if os.path.exists(master_path):
    master = pd.read_csv(master_path)
    master = master[master["sid"] != sid]   # keep everything except this cyclone
    master = pd.concat([master, out], ignore_index=True)
    master.to_csv(master_path, index=False)
else:
    out.to_csv(master_path, index=False)

print(f"Saved {len(out)} rows for SID {sid} without duplication.")
