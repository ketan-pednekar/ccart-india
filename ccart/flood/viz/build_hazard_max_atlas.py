import rasterio
import geopandas as gpd
import matplotlib.pyplot as plt
import numpy as np
from rasterio.warp import reproject, Resampling
from pathlib import Path

# ------------------------------------------------------------
# Paths
# ------------------------------------------------------------
project_root = Path("C:/CMIP_data/cmip6/Climada/Projects/ccart-india")

haz_tif = project_root / "ccart/flood/outputs/hazard/hazard_max_ssp370_2027_2100.tif"
fsi_tif = project_root / "ccart/flood/outputs/fsi/ccart_floods_fsi_rescaled.tif"
states_gpkg = project_root / "ccart/data/boundaries/INDIA_STATES.gpkg"

# ------------------------------------------------------------
# Load India boundary
# ------------------------------------------------------------
states = gpd.read_file(states_gpkg).to_crs("EPSG:4326")
states["geometry"] = states["geometry"].buffer(0)

# ------------------------------------------------------------
# Load hazard raster (full grid)
# ------------------------------------------------------------
with rasterio.open(haz_tif) as src:
    haz = src.read(1).astype(float)
    transform = src.transform
    profile = src.profile

# ------------------------------------------------------------
# Load FSI (IndoFloods domain)
# ------------------------------------------------------------
with rasterio.open(fsi_tif) as src:
    fsi = src.read(1).astype(float)
    fsi_transform = src.transform

# ------------------------------------------------------------
# Reproject FSI → hazard grid
# ------------------------------------------------------------
fsi_on_chirps = np.zeros_like(haz, dtype="float32")

reproject(
    source=fsi,
    destination=fsi_on_chirps,
    src_transform=fsi_transform,
    src_crs="EPSG:4326",
    dst_transform=transform,
    dst_crs="EPSG:4326",
    resampling=Resampling.bilinear
)

# Clean FSI mask
fsi_on_chirps = np.where(fsi_on_chirps > 0, fsi_on_chirps, np.nan)

# ------------------------------------------------------------
# IndoFloods-masked hazard (correct logic)
# ------------------------------------------------------------
haz_indofloods = haz * fsi_on_chirps
haz_indofloods = np.where(np.isfinite(fsi_on_chirps), haz_indofloods, np.nan)

# ------------------------------------------------------------
# Compute extent
# ------------------------------------------------------------
left = transform[2]
top = transform[5]
pixel_width = transform[0]
pixel_height = transform[4]

right = left + pixel_width * haz.shape[1]
bottom = top + pixel_height * haz.shape[0]

extent = [left, right, bottom, top]

# ------------------------------------------------------------
# Percentile scaling
# ------------------------------------------------------------
vmin = np.nanpercentile(haz_indofloods, 1)
vmax = np.nanpercentile(haz_indofloods, 99)

# ------------------------------------------------------------
# Plot with white background
# ------------------------------------------------------------
fig, ax = plt.subplots(figsize=(10, 12))
ax.set_facecolor("white")

img = ax.imshow(
    haz_indofloods,
    cmap="viridis",
    vmin=vmin,
    vmax=vmax,
    extent=extent,
    origin="upper"
)

states.boundary.plot(ax=ax, color="black", linewidth=0.7)

cbar = plt.colorbar(img, ax=ax, shrink=0.7)
cbar.set_label("Max Hazard (2027–2100)")

fig.suptitle(
    "CCART Resilience Design Hazard Layer (SSP3‑7.0, 2027–2100)\nIndoFloods‑masked",
    fontsize=16,
    y=0.98
)

ax.set_axis_off()
plt.show()
