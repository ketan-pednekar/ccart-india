import geopandas as gpd

gdf = gpd.read_file(r"C:\CMIP data\cmip6\Climada\Projects\ccart-india\data\INDIA_DISTRICTS_FIXED.gpkg")
print(gdf[['district','state','statecode','st_code']].head())
