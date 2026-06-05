import xarray as xr
import geopandas as gpd
import numpy as np
from rasterio.features import rasterize
from rasterio.transform import Affine
import pandas as pd
from shapely.geometry import Point

# =========================================================
# ORIENTATION HELPER (FINAL)
# =========================================================
def orient_array_and_transform(arr_raw, lats, lons):
    dx = float(lons[1] - lons[0])
    dy = float(lats[1] - lats[0])   # may be + or -

    # CASE 1 — Latitude ASCENDING (South → North)
    if np.all(np.diff(lats) > 0):
        arr = np.flipud(arr_raw)
        transform = Affine(
            dx, 0, lons.min() - dx/2,
            0, +abs(dy), lats.min() - abs(dy)/2
        )
        print("Orientation: ASCENDING → FLIPPED (Orientation B)")

    # CASE 2 — Latitude DESCENDING (North → South)
    else:
        # IMPORTANT:
        # Time-slice cubes have descending lat BUT array stored upside-down.
        # So we MUST flip the array.
        arr = np.flipud(arr_raw)
        transform = Affine(
            dx, 0, lons.min() - dx/2,
            0, dy, lats.max() + dy/2
        )
        print("Orientation: DESCENDING → ARRAY FLIPPED (Corrected A*)")

    return arr, transform

# =========================================================
# 1. LOAD TIME-SLICE CUBE
# =========================================================
cube_path = r"C:\CMIP_data\cmip6\Climada\Projects\ccart-india\ccart\Heat\outputs\timeslice_cubes\cube_timeslice_wbt35_EndCentury_2081-2100.zarr"
ds = xr.open_zarr(cube_path)

varname = list(ds.data_vars)[0]
arr_raw = ds[varname].values

lats = ds.lat.values
lons = ds.lon.values

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
# 3. APPLY CORRECT ORIENTATION
# =========================================================
arr, transform = orient_array_and_transform(arr_raw, lats, lons)
print("Transform:\n", transform)

ny, nx = arr.shape

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
    vals = np.array(arr[mask])
    records.append((
        row["district"],
        row["st_nm"],
        float(np.nanmean(vals)),
        float(np.nanmax(vals))
    ))

df = pd.DataFrame(records, columns=["district", "state", "mean_exceed", "max_exceed"])

top100 = df.sort_values("max_exceed", ascending=False).head(100)
print("\nTOP 100 DISTRICTS (Time‑Slice):")
print(top100)

# =========================================================
# 6. HARD COORDINATE CHECKS
# =========================================================
def hard_check(lat, lon, label):
    val = float(ds[varname].sel(lat=lat, lon=lon, method="nearest").compute())
    pt = Point(lon, lat)
    hit = gdf[gdf.geometry.contains(pt)]
    print(f"\nHard check: {label}")
    print("Nearest-grid exceedance:", val)
    print("District containing point:")
    print(hit[["district", "st_nm"]])

hard_check(26.1, 91.7, "Guwahati (Assam)")
hard_check(20.5, 86.4, "Kendrapara (Odisha)")
hard_check(27.6, 95.8, "Namsai (Arunachal)")
