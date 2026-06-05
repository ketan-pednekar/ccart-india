"""
CCART-Heat — Generate Time-Slice TIFFs (from time-slice cubes)
"""

from pathlib import Path
import numpy as np
import xarray as xr
import geopandas as gpd
from rasterio.features import rasterize
from rasterio.transform import Affine
import rasterio

from ccart.Heat.config import load_heat_paths


def main():

    paths = load_heat_paths()

    cube_dir = Path(paths["outputs"]["timeslice_cubes"])
    tif_dir  = Path(paths["outputs"]["timeslices"])
    tif_dir.mkdir(parents=True, exist_ok=True)

    # Load strict India boundary
    districts = gpd.read_file(paths["boundaries"]["districts"])
    india_poly = districts.dissolve().geometry.iloc[0]

    cubes = sorted(cube_dir.glob("cube_timeslice_wbt35_*.zarr"))

    print("\nFound time-slice cubes:")
    for c in cubes:
        print("  -", c.name)

    for cube_path in cubes:

        label = cube_path.stem.replace("cube_timeslice_wbt35_", "")
        print(f"\n=== Generating TIFF for: {label} ===")

        # 1. Load cube
        da = xr.open_zarr(cube_path)["wbt35"]
        arr = da.values.astype("float32")
        lat = da.lat.values
        lon = da.lon.values

        dx = float(abs(lon[1] - lon[0]))
        dy = float(abs(lat[1] - lat[0]))

        # 2. Center-aligned affine
        transform = Affine(
            dx, 0.0, float(lon.min() - dx/2),
            0.0, -dy, float(lat.max() + dy/2),
        )

        # 3. Flip array FIRST if needed (lat descending)
        if lat[0] < lat[-1]:
            arr = arr[::-1, :]
            lat = lat[::-1]

        # 4. Rasterize mask on the flipped grid
        india_mask = rasterize(
            [(india_poly, 1)],
            out_shape=arr.shape,
            transform=transform,
            fill=0,
            dtype="uint8",
        )

        # 5. Apply mask
        arr[india_mask == 0] = 0.0

        # 6. Write TIFF
        out_tif = tif_dir / f"CCART_Hazard_WBT35_{label}.tif"

        profile = {
            "driver": "GTiff",
            "height": arr.shape[0],
            "width": arr.shape[1],
            "count": 1,
            "dtype": "float32",
            "crs": "EPSG:4326",
            "transform": transform,
            "nodata": np.nan,
            "compress": "lzw",
        }

        with rasterio.open(out_tif, "w", **profile) as dst:
            dst.write(arr, 1)

        print(f"Saved TIFF: {out_tif}")


if __name__ == "__main__":
    main()
