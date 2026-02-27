import osmnx as ox
import geopandas as gpd

north = 17.7200
south = 17.6800
west  = 83.2600
east  = 83.3100

buildings = ox.features.features_from_bbox(
    north=north,
    south=south,
    west=west,
    east=east,
    tags={"building": True}
)

# keep only polygons
buildings = buildings[buildings.geometry.type.isin(["Polygon", "MultiPolygon"])]

buildings = buildings.reset_index(drop=True)

print(buildings.head())
print(len(buildings), "buildings extracted")

buildings.to_file("vizag_port_buildings.geojson", driver="GeoJSON")
