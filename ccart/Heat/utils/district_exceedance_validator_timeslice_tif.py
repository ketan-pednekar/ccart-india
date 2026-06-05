import rasterio
import geopandas as gpd
import numpy as np
import pandas as pd
from rasterio.features import rasterize
from shapely.geometry import Point

# =========================================================
# 1. LOAD TIFF
# =========================================================
tif_path = r"C:\CMIP_data\cmip6\Climada\Projects\ccart-india\ccart\Heat\outputs\timeslices_wbt35\CCART_Hazard_WBT35_EndCentury_2081-2100.tif"

with rasterio.open(tif_path) as src:
    arr_raw = src.read(1).astype("float32")
    transform = src.transform
    crs = src.crs
    ny, nx = arr_raw.shape

print("TIFF loaded. Shape:", arr_raw.shape)
print("Transform:", transform)
print("CRS:", crs)

# =========================================================
# 2. FIX ORIENTATION (TIFF IS UPSIDE-DOWN)
# =========================================================
arr = np.flipud(arr_raw)
print("Applied vertical flip to TIFF array")

# =========================================================
# 3. LOAD DISTRICTS
# =========================================================
districts_path = r"C:\Users\ketan\Downloads\INDIA_DISTRICTS_734.gpkg"
gdf = gpd.read_file(districts_path).to_crs(crs)
gdf = gdf.reset_index(drop=True)
gdf["dist_id"] = gdf.index + 1

# =========================================================
# 4. RASTERIZE DISTRICTS
# =========================================================
shapes = [(geom, dist_id) for geom, dist_id in zip(gdf.geometry, gdf["dist_id"])]

district_raster = rasterize(
    shapes,
    out_shape=(ny, nx),
    transform=transform,
    fill=0,
    dtype="int32"
)

# =========================================================
# 5. DISTRICT‑LEVEL STATS
# =========================================================
records = []
for _, row in gdf.iterrows():
    dist_id = row["dist_id"]
    mask = district_raster == dist_id
    if mask.sum() == 0:
        continue
    vals = arr[mask]
    records.append((
        row["district"],
        row["st_nm"],
        float(np.nanmean(vals)),
        float(np.nanmax(vals))
    ))

df = pd.DataFrame(records, columns=["district", "state", "mean_exceed", "max_exceed"])

top100 = df.sort_values("max_exceed", ascending=False).head(100)
print("\nTOP 100 DISTRICTS (TIFF Time‑Slice, Corrected):")
print(top100)

# =========================================================
# 6. HARD COORDINATE CHECKS
# =========================================================
def hard_check(lat, lon, label):
    row, col = ~transform * (lon, lat)
    row, col = int(row), int(col)
    val = arr[row, col]
    pt = Point(lon, lat)
    hit = gdf[gdf.geometry.contains(pt)]
    print(f"\nHard check: {label}")
    print("Nearest-grid exceedance:", val)
    print(hit[["district", "st_nm"]])

hard_check(26.1, 91.7, "Guwahati (Assam)")
hard_check(20.5, 86.4, "Kendrapara (Odisha)")
hard_check(27.6, 95.8, "Namsai (Arunachal)")
