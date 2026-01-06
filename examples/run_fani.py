from ccart.engine import run_ccart
from climada.engine import Impact


gdf = run_ccart(
    cyclone_name="Fani",
    storm_id="2019116N02090",
    ibtracs_path="data/IBTRACS.ALL.v04r01.nc",
    districts_path="data/INDIA_DISTRICTS.geojson",
    dlna_total=4.2e9,
    state_name="ODISHA"
)

print(gdf.head())
print(gdf.columns)

print("Total impact:", gdf["loss_usd_hwe"].sum())


