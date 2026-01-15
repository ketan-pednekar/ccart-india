from ccart.engine import run_ccart
from climada.engine import Impact
from ccart.viz import ccart_choropleth
import geopandas as gpd
from ccart import engine
print("Engine file:", engine.run_ccart.__code__.co_filename) # dignostic
print("Hazard floor:", engine.HAZARD_FLOOR_MS) #dignostic


# === Run CCART for Cyclone Nisarga ===
gdf = run_ccart(
    cyclone_name="Nisarga",
    storm_id="2020153N13072",   # Confirmed SID from IBTrACS
    ibtracs_path=r"C:\CMIP data\cmip6\Climada\Projects\ccart-india\data\IBTRACS.ALL.v04r01.nc",
    districts_path=r"C:\CMIP data\cmip6\Climada\Projects\ccart-india\data\INDIA_DISTRICTS.geojson",
    dlna_total=803e6,           # Placeholder — update if you have PDRA/official estimate
    state_name="MAHARASHTRA",
    inland_clip_km=150,
    coastline_path=r"C:\CMIP data\cmip6\Climada\Projects\ccart-india\data\coastl_ind.shp"
)

print(gdf.head())
print(gdf.columns)
print("Total impact:", gdf["loss_usd_hwe"].sum())

# === DIAGNOSTICS BEFORE MAP ===
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

# === NOW SHOW THE MAP ===
df_losses = (
    gdf[["District", "loss_usd_hwe"]]
    .rename(columns={"loss_usd_hwe": "loss"})
)

ccart_choropleth(
    gdf,
    df_losses,
    district_col="District",
    loss_col="loss",
    state_filter="MAHARASHTRA",
    title="Cyclone Nisarga – CCART Loss Map (Maharashtra)"
)
