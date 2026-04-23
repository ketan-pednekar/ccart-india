"""
CCART Flood Module
Static Flood Risk Visualization (Final)
---------------------------------------

- Uses India STATE boundaries (clean, uncluttered)
- Uses a perceptually uniform color ramp (viridis)
- Applies percentile-based scaling to reveal structure
- Shows ONLY the India ∩ Indo-Floods domain (no debug tile)
"""

from pathlib import Path
import rasterio
import numpy as np
import geopandas as gpd
import matplotlib.pyplot as plt
from rasterio.plot import plotting_extent
from rasterio.features import geometry_mask

def viz_static_flood_risk():
    project_root = Path("C:/CMIP_data/cmip6/Climada/Projects/ccart-india")

    risk_tif = project_root / "ccart/flood/outputs/risk/ccart_floods_static_risk_005deg_v1.tif"
    states_gpkg = project_root / "ccart/data/boundaries/INDIA_STATES.gpkg"

    # Load risk raster
    with rasterio.open(risk_tif) as src:
        risk = src.read(1).astype(float)
        risk[risk == src.nodata] = np.nan

        extent = plotting_extent(src)
        raster_crs = src.crs
        transform = src.transform
        shape = (src.height, src.width)

    # Load and clean state boundaries
    states = gpd.read_file(states_gpkg).to_crs(raster_crs)
    states["geometry"] = states["geometry"].buffer(0)
    states_union = states.union_all()

    # Mask to India
    mask = geometry_mask(
        [states_union],
        transform=transform,
        invert=True,
        out_shape=shape
    )

    risk_masked = np.where(mask, risk, np.nan)

    # Plot
    fig, ax = plt.subplots(figsize=(9, 10))

    img = ax.imshow(
        risk_masked,
        extent=extent,
        origin="upper",
        cmap="viridis",
        vmin=0,
        vmax=np.nanpercentile(risk_masked, 99)
    )

    states.boundary.plot(ax=ax, color="black", linewidth=1.0, zorder=10)

    ax.set_title("Static Flood Risk (Indo-Floods Domain Only)", fontsize=13)
    ax.set_axis_off()

    cbar = plt.colorbar(img, ax=ax, shrink=0.7)
    cbar.set_label("Static Flood Risk")

    plt.show()


if __name__ == "__main__":
    viz_static_flood_risk()
