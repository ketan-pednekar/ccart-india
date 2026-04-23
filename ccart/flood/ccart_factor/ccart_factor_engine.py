import numpy as np
import rasterio
import rasterio.features
import geopandas as gpd
from pathlib import Path

project_root = Path(r"C:\CMIP_data\cmip6\Climada\Projects\ccart-india")

# ------------------------------------------------------------
# Input rasters
# ------------------------------------------------------------
fsi_path      = project_root / "ccart/flood/outputs/fsi/static_fsi_on_chirps.tif"
haz370_path   = project_root / "ccart/flood/outputs/hazard/hazard_max_ssp370_2027_2100.tif"
haz585_path   = project_root / "ccart/flood/outputs/hazard/hazard_max_ssp585_2027_2100.tif"

# ------------------------------------------------------------
# Domain masks
# ------------------------------------------------------------
india_path       = project_root / "ccart/data/boundaries/INDIA_STATES.gpkg"
indofloods_path  = project_root / "ccart/data/boundaries/INDOFLOODS_DOMAIN.gpkg"

# ------------------------------------------------------------
# Output directory
# ------------------------------------------------------------
out_dir = project_root / "ccart/flood/outputs/ccart_factor"
out_dir.mkdir(parents=True, exist_ok=True)

# ------------------------------------------------------------
# Helper functions
# ------------------------------------------------------------
def load_raster(path):
    with rasterio.open(path) as src:
        arr = src.read(1).astype("float32")
        profile = src.profile
        transform = src.transform
        shape = (src.height, src.width)
        crs = src.crs
    return arr, profile, transform, shape, crs

def save_raster(path, array, profile):
    profile = profile.copy()
    profile.update(dtype="float32", compress="lzw")
    with rasterio.open(path, "w", **profile) as dst:
        dst.write(array.astype("float32"), 1)

# ------------------------------------------------------------
# Load rasters
# ------------------------------------------------------------
fsi, profile, transform, shape, raster_crs = load_raster(fsi_path)
haz370, _, _, _, _ = load_raster(haz370_path)
haz585, _, _, _, _ = load_raster(haz585_path)

# ------------------------------------------------------------
# Load and prepare masks
# ------------------------------------------------------------
india = gpd.read_file(india_path).to_crs(raster_crs).dissolve()
india["geometry"] = india.buffer(0)

indofloods = gpd.read_file(indofloods_path).to_crs(raster_crs).dissolve()
indofloods["geometry"] = indofloods.buffer(0)

mask_india = rasterio.features.geometry_mask(
    [india.geometry.iloc[0]],
    transform=transform,
    invert=True,
    out_shape=shape
)

mask_indofloods = rasterio.features.geometry_mask(
    [indofloods.geometry.iloc[0]],
    transform=transform,
    invert=True,
    out_shape=shape
)

# Combined domain mask
mask_domain = mask_india & mask_indofloods

# ------------------------------------------------------------
# Compute CCART Factors safely
# ------------------------------------------------------------
eps = 1e-6  # avoid division by zero

factor370 = np.where(mask_domain, haz370 / (fsi + eps), np.nan)
factor585 = np.where(mask_domain, haz585 / (fsi + eps), np.nan)

# ------------------------------------------------------------
# Save corrected rasters
# ------------------------------------------------------------
save_raster(out_dir / "ccart_factor_ssp370.tif", factor370, profile)
save_raster(out_dir / "ccart_factor_ssp585.tif", factor585, profile)

print("Corrected CCART Factor TIFFs generated successfully.")
