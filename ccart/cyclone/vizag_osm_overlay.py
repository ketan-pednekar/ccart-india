import h5py
import numpy as np
import geopandas as gpd
import matplotlib.pyplot as plt
import contextily as ctx
import rasterio 

from rasterio.transform import from_bounds
from scipy.sparse import csr_matrix
from scipy.interpolate import griddata

# ---------------------------------------------------------
# Step 1 — Load hazard HDF5 manually
# ---------------------------------------------------------
with h5py.File("vizag_design_cyclone_hazard.h5", "r") as f:
    coords = f["centroids/block0_values"][:]   # shape (900, 2)
    lon = coords[:, 0]
    lat = coords[:, 1]

    data = f["intensity/data"][:]
    indices = f["intensity/indices"][:]
    indptr = f["intensity/indptr"][:]

    intensity_sparse = csr_matrix((data, indices, indptr))
    intensity = intensity_sparse.toarray()[0]

haz_gdf = gpd.GeoDataFrame(
    {"intensity": intensity},
    geometry=gpd.points_from_xy(lon, lat),
    crs="EPSG:4326"
)

# ---------------------------------------------------------
# Step 2 — Load OSM buildings
# ---------------------------------------------------------
buildings = gpd.read_file("vizag_port_buildings.geojson")

# ---------------------------------------------------------
# Step 3 — Reproject
# ---------------------------------------------------------
haz_web = haz_gdf.to_crs(epsg=3857)
buildings_web = buildings.to_crs(epsg=3857)

# ---------------------------------------------------------
# Step 4 — Rasterize hazard using HAZARD extent
# ---------------------------------------------------------
minx_h, miny_h, maxx_h, maxy_h = haz_web.total_bounds

grid_x, grid_y = np.mgrid[
    minx_h:maxx_h:300j,
    miny_h:maxy_h:300j
]

points = np.column_stack((haz_web.geometry.x, haz_web.geometry.y))
values = haz_web["intensity"].values

grid_z = griddata(points, values, (grid_x, grid_y), method='cubic')

import rasterio
from rasterio.transform import from_bounds

# ---------------------------------------------------------
# Step 4.1 - Export hazard raster to GeoTIFF for QGIS
# ---------------------------------------------------------

# Define transform using hazard extent
transform = from_bounds(minx_h, miny_h, maxx_h, maxy_h, grid_z.shape[0], grid_z.shape[1])

# Save raster
with rasterio.open(
    "vizag_hazard.tif",
    "w",
    driver="GTiff",
    height=grid_z.shape[1],
    width=grid_z.shape[0],
    count=1,
    dtype=grid_z.dtype,
    crs="EPSG:3857",
    transform=transform,
) as dst:
    dst.write(grid_z.T, 1)

# ---------------------------------------------------------
# Step 5 — Compute LOCAL color scale for the building area
# ---------------------------------------------------------
minx_b, miny_b, maxx_b, maxy_b = buildings_web.total_bounds

mask_x = (points[:,0] >= minx_b) & (points[:,0] <= maxx_b)
mask_y = (points[:,1] >= miny_b) & (points[:,1] <= maxy_b)
mask = mask_x & mask_y

local_min = values[mask].min()
local_max = values[mask].max()

# Optional slight exaggeration for visual clarity
vmin = local_min - 0.1
vmax = local_max + 0.1

# ---------------------------------------------------------
# Step 6 — Plot
# ---------------------------------------------------------
fig, ax = plt.subplots(figsize=(10, 10))

# Zoom to building area
ax.set_xlim(minx_b - 500, maxx_b + 500)
ax.set_ylim(miny_b - 500, maxy_b + 500)

# Basemap
ctx.add_basemap(ax, source=ctx.providers.CartoDB.Positron)

# Raster hazard with LOCAL scaling
im = ax.imshow(
    grid_z.T,
    extent=(minx_h, maxx_h, miny_h, maxy_h),
    origin='lower',
    cmap='inferno',
    alpha=0.6,
    vmin=vmin,
    vmax=vmax
)

# Colorbar
cbar = plt.colorbar(im, ax=ax)
cbar.set_label("Wind speed (m/s) — local scale")

# Buildings on top
# Thick black base stroke
buildings_web.plot(
    ax=ax,
    facecolor="none",
    edgecolor="black",
    linewidth=2.2,
    alpha=1.0
)

# Thin white inner stroke
buildings_web.plot(
    ax=ax,
    facecolor="none",
    edgecolor="white",
    linewidth=0.8,
    alpha=1.0
)


ax.set_axis_off()
plt.title("Vizag Port — Design Cyclone Hazard + OSM Buildings", fontsize=16, pad=25)
plt.subplots_adjust(top=0.92)
plt.show()
