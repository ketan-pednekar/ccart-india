"""
Module: rasterise_fsi
CCART-Floods Framework
-------------------------------------------------------------

Leak-proof version:
    - HYBAS polygons are clipped to India BEFORE rasterisation
    - Ensures no leakage in Siliguri Corridor, Bangladesh, Nepal, Bhutan
    - Guarantees FSI raster is India-only by geometry and by value
"""

from typing import Tuple
import numpy as np
import geopandas as gpd
from rasterio.features import rasterize


def rasterise_clean_rescale_fsi(
    gdf_fsi: gpd.GeoDataFrame,
    chirps_transform,
    shape: Tuple[int, int],
    hybas_path,
    india_path=None,
):
    """
    Basin-wise rasterisation of FSI:
    1. Join gauge FSI to HYBAS basins
    2. CLIP HYBAS polygons to India (critical fix)
    3. Rasterise HYBAS polygons onto CHIRPS grid
    4. Rescale to 0–1
    """

    # ---------------------------------------------------------
    # 1. Load HYBAS + India boundary
    # ---------------------------------------------------------
    hybas = gpd.read_file(hybas_path)

    if india_path is None:
        raise ValueError("india_path must be provided for leak-proof rasterisation.")

    india = gpd.read_file(india_path)

    # CRS safety
    if hybas.crs != india.crs:
        india = india.to_crs(hybas.crs)

    if gdf_fsi.crs != hybas.crs:
        gdf_fsi = gdf_fsi.to_crs(hybas.crs)

    # Remove leftover join artifacts
    for df in (hybas, gdf_fsi):
        if "index_right" in df.columns:
            df.drop(columns=["index_right"], inplace=True)

    # ---------------------------------------------------------
    # 2. CLIP HYBAS polygons to India (THE FIX)
    # ---------------------------------------------------------
    hybas = gpd.overlay(hybas, india, how="intersection")

    # ---------------------------------------------------------
    # 3. Spatial join: assign each gauge to its HYBAS basin
    # ---------------------------------------------------------
    gdf_joined = gpd.sjoin(
        gdf_fsi,
        hybas,
        how="left",
        predicate="intersects"
    )

    # ---------------------------------------------------------
    # 4. Detect basin ID column
    # ---------------------------------------------------------
    possible_cols = [
        "HYBAS_ID", "HYBAS_ID_1", "HYBAS_ID_12", "HYBAS_ID_6",
        "MAIN_BAS", "PFAF_ID"
    ]

    basin_id = None
    for col in possible_cols:
        if col in hybas.columns:
            basin_id = col
            break

    if basin_id is None:
        raise ValueError(
            f"No basin ID column found in HYBAS. "
            f"Available columns: {list(hybas.columns)}"
        )

    joined_basin_col = basin_id + "_left"

    if joined_basin_col not in gdf_joined.columns:
        raise ValueError(
            f"Expected basin column '{joined_basin_col}' not found after join. "
            f"Available columns: {list(gdf_joined.columns)}"
        )

    # ---------------------------------------------------------
    # 5. Aggregate FSI per basin
    # ---------------------------------------------------------
    basin_fsi = (
        gdf_joined
        .groupby(joined_basin_col)["FSI_masked"]
        .mean()
        .reset_index()
    )

    # ---------------------------------------------------------
    # 6. Merge FSI back into clipped HYBAS polygons
    # ---------------------------------------------------------
    hybas_fsi = hybas.merge(
        basin_fsi,
        left_on=basin_id,
        right_on=joined_basin_col,
        how="left"
    )

    if "FSI_masked" not in hybas_fsi.columns:
        raise ValueError(
            f"'FSI_masked' column missing after merge. "
            f"Available columns: {list(hybas_fsi.columns)}"
        )

    # ---------------------------------------------------------
    # 7. Build shapes list for rasterisation
    # ---------------------------------------------------------
    shapes = [
        (geom, val)
        for geom, val in zip(hybas_fsi.geometry, hybas_fsi["FSI_masked"])
        if val is not None and not np.isnan(val)
    ]

    # ---------------------------------------------------------
    # 8. Rasterise to CHIRPS grid
    # ---------------------------------------------------------
    fsi_raster = rasterize(
        shapes=shapes,
        out_shape=shape,
        transform=chirps_transform,
        fill=np.nan,
        dtype="float32",
    )

    # ---------------------------------------------------------
    # 9. Rescale 0–1
    # ---------------------------------------------------------
    valid = ~np.isnan(fsi_raster)
    if not np.any(valid):
        raise ValueError("FSI rasterisation produced no valid pixels.")

    minv = np.nanmin(fsi_raster)
    maxv = np.nanmax(fsi_raster)

    fsi_rescaled = np.full_like(fsi_raster, np.nan, dtype="float32")
    fsi_rescaled[valid] = (fsi_raster[valid] - minv) / (maxv - minv)

    return fsi_rescaled
