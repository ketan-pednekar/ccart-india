from ccart.engine import run_ccart
from ccart.viz import ccart_choropleth
from ccart import engine
import geopandas as gpd
import pandas as pd
import os

print("Engine file:", engine.run_ccart.__code__.co_filename)
print("Hazard floor:", engine.HAZARD_FLOOR_MS)

# === Run CCART for Cyclone Laila ===
gdf = run_ccart(
    cyclone_name="Laila",
    storm_id="2010137N10090",   # Correct SID for Laila
    ibtracs_path=r"C:\CMIP data\cmip6\Climada\Projects\ccart-india\data\IBTRACS.ALL.v04r01.nc",
    districts_path=r"C:\CMIP data\cmip6\Climada\Projects\ccart-india\data\INDIA_DISTRICTS.geojson",

    dlna_total=600e6,           # India DLNA ≈ USD 0.6B
    state_name="ANDHRA PRADESH",
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
master_path = r"C:\CMIP data\cmip6\Climada\Projects\ccart-india\data\district_relationships_master.csv"

# === CYCLONE METADATA ===
sid = "2010137N10090"
cyclone_name = "Laila"
year = 2010
dlna_total = 600e6
calibration_state = "ANDHRA PRADESH"

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
    master = master[master["sid"] != sid]
    master = pd.concat([master, out], ignore_index=True)
    master.to_csv(master_path, index=False)
else:
    out.to_csv(master_path, index=False)

print(f"Saved {len(out)} rows for SID {sid} without duplication.")

# === MAP ===
df_losses = (
    gdf[["District", "loss_usd_hwe"]]
    .rename(columns={"loss_usd_hwe": "loss"})
)

if gdf["loss_usd_hwe"].sum() > 0:
    ccart_choropleth(
        gdf,
        df_losses,
        district_col="District",
        loss_col="loss",
        state_filter="ANDHRA PRADESH",
        title="Cyclone Laila – CCART Loss Map (Andhra Pradesh)"
    )
else:
    print("No positive losses — skipping choropleth.")
