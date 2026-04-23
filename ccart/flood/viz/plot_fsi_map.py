import rasterio
import rasterio.mask
import geopandas as gpd
import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path

# ------------------------------------------------------------
# Paths
# ------------------------------------------------------------
project_root = Path("C:/CMIP_data/cmip6/Climada/Projects/ccart-india")

fsi_tif = project_root / "ccart/flood/outputs/fsi/ccart_floods_fsi_rescaled.tif"
states_gpkg = project_root / "ccart/data/boundaries/INDIA_STATES.gpkg"

# ------------------------------------------------------------
# Load India STATE boundary (cleaner)
# ------------------------------------------------------------
states = gpd.read_file(states_gpkg).to_crs("EPSG:4326")
states["geometry"] = states["geometry"].buffer(0)  # fix invalid geometries

# ------------------------------------------------------------
# Load and mask FSI raster
# ------------------------------------------------------------
with rasterio.open(fsi_tif) as src:
    out_image, out_transform = rasterio.mask.mask(src, states.geometry, crop=True)
    out_meta = src.meta.copy()

fsi = out_image[0].astype(float)
fsi[fsi < 0] = np.nan

# ------------------------------------------------------------
# Compute raster extent in geographic coordinates
# ------------------------------------------------------------
left = out_transform[2]
top = out_transform[5]
pixel_width = out_transform[0]
pixel_height = out_transform[4]

right = left + pixel_width * fsi.shape[1]
bottom = top + pixel_height * fsi.shape[0]

extent = [left, right, bottom, top]

# ------------------------------------------------------------
# Percentile scaling for better contrast
# ------------------------------------------------------------
vmin = np.nanpercentile(fsi, 1)
vmax = np.nanpercentile(fsi, 99)

# ------------------------------------------------------------
# Plot on SAME AXIS
# ------------------------------------------------------------
fig, ax = plt.subplots(figsize=(10, 12))

img = ax.imshow(
    fsi,
    cmap="plasma",          # ⭐ better contrast for 0–1
    vmin=vmin,              # ⭐ percentile scaling
    vmax=vmax,
    extent=extent,
    origin="upper"
)

# India boundary overlay
states.boundary.plot(ax=ax, color="black", linewidth=0.7)

# Colorbar
cbar = plt.colorbar(img, ax=ax, shrink=0.7)
cbar.set_label("Flood Susceptibility Index (0–1)")

fig.suptitle(
    "CCART Flood Susceptibility Index (FSI, 0.05°)",
    fontsize=16,
    y=0.98
)
ax.set_axis_off()
plt.show()
