import geopandas as gpd
import xarray as xr
import rasterio.features
from affine import Affine
import numpy as np


def make_strict_mask(template_da: xr.DataArray, india_shp_path: str) -> xr.DataArray:
    """
    Create a strict India mask aligned to the grid of template_da.

    - Assumes template_da has 2D lat/lon grid with dims ("lat", "lon")
    - Handles both ascending and descending latitude
    - Uses EPSG:4326 for the India shapefile
    - Returns uint8 mask with 1 = inside India, 0 = outside
    """

    # 1. Read India boundaries and ensure CRS = EPSG:4326
    india = gpd.read_file(india_shp_path)
    if india.crs is not None and india.crs.to_epsg() != 4326:
        india = india.to_crs("EPSG:4326")
    india_union = india.unary_union

    # 2. Extract grid
    lat = np.asarray(template_da["lat"].values)
    lon = np.asarray(template_da["lon"].values)

    if lat.ndim != 1 or lon.ndim != 1:
        raise ValueError("Expected 1D lat/lon coordinates")

    if len(lat) < 2 or len(lon) < 2:
        raise ValueError("Need at least 2 points in each dimension to build affine")

    dlat = float(lat[1] - lat[0])
    dlon = float(lon[1] - lon[0])

    # 3. Build north-up affine
    # Row 0 should correspond to the northernmost latitude
    lat_max = float(lat.max())
    lon_min = float(lon.min())

    transform = Affine(
        dlon, 0.0, lon_min - dlon / 2.0,
        0.0, -abs(dlat), lat_max + abs(dlat) / 2.0,
    )

    out_shape = (len(lat), len(lon))

    # 4. Rasterize India polygon onto this grid
    mask = rasterio.features.rasterize(
        [(india_union, 1)],
        out_shape=out_shape,
        transform=transform,
        fill=0,
        all_touched=True,
        dtype="uint8",
    )

    da_mask = xr.DataArray(
        mask,
        coords={"lat": lat, "lon": lon},
        dims=("lat", "lon"),
        name="strict_mask",
    )

    return da_mask
