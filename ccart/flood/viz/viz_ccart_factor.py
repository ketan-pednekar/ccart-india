import rasterio
import rasterio.plot
import geopandas as gpd
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap
import numpy as np

# ------------------------------------------------------------
# Paths
# ------------------------------------------------------------
ccart_factor_path = r"C:\CMIP_data\cmip6\Climada\Projects\ccart-india\ccart\flood\outputs\ccart_factor\ccart_factor_ssp585.tif"
states_path = r"C:\CMIP_data\cmip6\Climada\Projects\ccart-india\ccart\data\boundaries\INDIA_STATES.gpkg"

# ------------------------------------------------------------
# Load raster
# ------------------------------------------------------------
with rasterio.open(ccart_factor_path) as src:
    factor = src.read(1).astype(float)
    extent = rasterio.plot.plotting_extent(src)
    raster_crs = src.crs

# Mask invalid values
factor = np.where(np.isfinite(factor), factor, np.nan)

# ------------------------------------------------------------
# Load India states (dissolve → ONE polygon)
# ------------------------------------------------------------
states = gpd.read_file(states_path).to_crs(raster_crs)
states = states.dissolve()                 # ⭐ critical fix
states["geometry"] = states.buffer(0)      # fix geometry

# ------------------------------------------------------------
# CCART color ramp
# ------------------------------------------------------------
colors = [
    "#2166AC",
    "#67A9CF",
    "#D1E5F0",
    "#FDDBC7",
    "#EF8A62",
    "#B2182B"
]
ccart_cmap = LinearSegmentedColormap.from_list("ccart", colors)

# ------------------------------------------------------------
# Plot
# ------------------------------------------------------------
fig, ax = plt.subplots(figsize=(8, 10))

img = ax.imshow(
    factor,
    cmap=ccart_cmap,
    extent=extent,
    origin="upper",
    vmin=1.0,
    vmax=np.nanpercentile(factor, 99)
)

# India outline (clean, aligned)
states.boundary.plot(ax=ax, linewidth=0.6, color="black")

# Title
ax.set_title(
    "CCART Factor (SSP585)\nClimate‑conditioned flood hazard amplification (2027–2100)",
    fontsize=14,
    pad=12
)

# Remove axes
ax.set_xticks([])
ax.set_yticks([])
ax.set_axis_off()

# Colorbar
cbar = fig.colorbar(img, ax=ax, fraction=0.03, pad=0.02)
cbar.set_label("Amplification Factor", fontsize=11)

# Watermark
plt.text(
    0.99, 0.01,
    "CCART • Climate Risk Engine for India",
    fontsize=9,
    color="#555555",
    ha="right",
    va="bottom",
    transform=ax.transAxes
)

plt.tight_layout()
plt.show()
