import xarray as xr
import geopandas as gpd
import numpy as np
from rasterio.features import rasterize
from rasterio.transform import Affine
import pandas as pd
import matplotlib.pyplot as plt
from shapely.geometry import Point

# =========================================================
# 1. LOAD INGESTED CUBE
# =========================================================
cube_path = r"C:\CMIP_data\cmip6\Climada\Projects\ccart-india\ccart\Heat\ingested\ssp370"
ds = xr.open_zarr(cube_path)

Tw = ds["wbt"]
lats = Tw.lat.values
lons = Tw.lon.values

dx = float(lons[1] - lons[0])
dy = float(lats[1] - lats[0])

print("Latitude ascending:", np.all(np.diff(lats) > 0))
print("Longitude ascending:", np.all(np.diff(lons) > 0))

# =========================================================
# 2. LOAD DISTRICTS
# =========================================================
districts_path = r"C:\Users\ketan\Downloads\INDIA_DISTRICTS_734.gpkg"
gdf = gpd.read_file(districts_path).to_crs("EPSG:4326")
gdf = gdf.reset_index(drop=True)
gdf["dist_id"] = gdf.index + 1

# =========================================================
# 3. COMPUTE EXCEEDANCE
# =========================================================
exceed = (Tw > 35).groupby("time.year").sum("time")
exceed_max = exceed.max("year").load()
raw_arr = exceed_max.values.astype("float32")

# =========================================================
# 4. ORIENTATION DIAGNOSTIC (OPTIONAL VISUAL CHECK)
# =========================================================
def orientation_diagnostic(arr, lons, lats, gdf):
    extent = [lons.min(), lons.max(), lats.min(), lats.max()]
    fig, axes = plt.subplots(1, 2, figsize=(14, 6))

    axes[0].imshow(arr, origin="upper", extent=extent, cmap="viridis")
    gdf.boundary.plot(ax=axes[0], linewidth=0.3, color="k")
    axes[0].set_title("Orientation A (no flip)")

    axes[1].imshow(np.flipud(arr), origin="upper", extent=extent, cmap="viridis")
    gdf.boundary.plot(ax=axes[1], linewidth=0.3, color="k")
    axes[1].set_title("Orientation B (vertical flip)")

    plt.suptitle("Flip vs No‑Flip Diagnostic", fontsize=14)
    plt.show()

# Uncomment if you want to visually re‑check
# orientation_diagnostic(raw_arr, lons, lats, gdf)

# =========================================================
# 5. USE VALIDATED ORIENTATION (B: FLIPPED)
# =========================================================
arr = np.flipud(raw_arr)

transform = Affine(
    dx, 0, lons.min() - dx/2,
    0, +dy, lats.min() - dy/2
)

print("\nUsing ORIENTATION B (flipped) with positive dy transform:")
print(transform)

ny, nx = arr.shape

# =========================================================
# 6. RASTERIZE DISTRICTS
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
# 7. DISTRICT‑LEVEL STATS
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
print("\nTOP 100 DISTRICTS:")
print(top100)

# =========================================================
# 8. HARD COORDINATE CHECKS (POINT‑LEVEL, FOR SANITY)
# =========================================================
def hard_check(lat, lon, label):
    val = exceed_max.sel(lat=lat, lon=lon, method="nearest").item()
    pt = Point(lon, lat)
    hit = gdf[gdf.geometry.contains(pt)]
    print(f"\nHard check: {label}")
    print("Nearest-grid exceedance:", val)
    print("District containing point:")
    print(hit[["district", "st_nm"]])

hard_check(26.1, 91.7, "Guwahati (Assam)")
hard_check(20.5, 86.4, "Kendrapara (Odisha)")
hard_check(27.6, 95.8, "Namsai (Arunachal)")
