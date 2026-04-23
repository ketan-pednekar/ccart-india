"""
Module: rasterise_fsi
CCART-Floods Framework
-------------------------------------------------------------

Purpose
-------
Rasterises the Flood Susceptibility Index (FSI) onto the CHIRPS India
0.05° grid using **basin-wise assignment** based on HYBAS L06 polygons.

This is the canonical CCART-Floods method for generating a continuous,
hydrologically meaningful susceptibility surface. IndoFloods gauge-level
FSI values are first joined to their corresponding HYBAS basins, then
each basin's FSI is rasterised across all pixels within that basin.

This replaces point burn-in rasterisation and ensures:
    - complete India-wide coverage (no gaps inside India)
    - hydrologically consistent susceptibility fields
    - perfect alignment with the CHIRPS India grid
    - suitability for downstream hazard and risk modelling

Pipeline
--------
1. Spatially join IndoFloods gauge FSI to HYBAS basins
2. Aggregate FSI per basin (mean of gauges within basin)
3. Rasterise HYBAS polygons onto CHIRPS grid
4. Clean and rescale raster to 0–1
5. Return CHIRPS-aligned susceptibility raster

Inputs
------
gdf_fsi : GeoDataFrame
    Output of compute_fsi(), containing gauge locations and FSI_masked.
chirps_transform : affine.Affine
    Transform of the CHIRPS India 0.05° grid.
shape : (rows, cols)
    Shape of the CHIRPS India grid.
hybas_path : str or Path
    Path to HYBAS L06 polygon file.

Outputs
-------
fsi_rescaled : 2D numpy array (float32)
    Basin-wise susceptibility raster aligned to CHIRPS grid,
    with values in the range 0–1 and NaN outside India.

Notes
-----
- HYBAS L06 is required for hydrologically meaningful basin assignment.
- FSI_masked must contain NaN for ungauged basins.
- Rasterisation uses rasterio.features.rasterize().
- This module produces the canonical CCART-Floods static FSI layer.
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
):
    """
    Basin-wise rasterisation of FSI:
    1. Join gauge FSI to HYBAS basins
    2. Rasterise HYBAS polygons onto CHIRPS grid
    3. Rescale to 0–1
    """
    # 1. Load HYBAS
    hybas = gpd.read_file(hybas_path)

    # FIX: remove leftover index_right columns
    for df in (hybas, gdf_fsi):
        if "index_right" in df.columns:
            df.drop(columns=["index_right"], inplace=True)

    # FIX: ensure CRS match
    if gdf_fsi.crs != hybas.crs:
        gdf_fsi = gdf_fsi.to_crs(hybas.crs)

    # 2. Spatial join: assign each gauge to its HYBAS basin
    gdf_joined = gpd.sjoin(gdf_fsi, hybas, how="left", predicate="intersects")

    # ---------------------------------------------------------
    # Robust HYBAS basin-ID detection (CCART standard)
    # ---------------------------------------------------------

    # Step 1 — detect basin ID column from HYBAS polygons
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

    # Step 2 — after spatial join, GeoPandas appends '_left'
    joined_basin_col = basin_id + "_left"

    if joined_basin_col not in gdf_joined.columns:
        raise ValueError(
            f"Expected basin column '{joined_basin_col}' not found after join. "
            f"Available columns: {list(gdf_joined.columns)}"
        )

    # Use this consistently
    basin_col = joined_basin_col

    # 3. Aggregate FSI per basin
    basin_fsi = (
        gdf_joined
        .groupby(basin_col)["FSI_masked"]
        .mean()
        .reset_index()
    )

    # 4. Merge back into HYBAS polygons
    hybas_fsi = hybas.merge(
        basin_fsi,
        left_on=basin_id,
        right_on=basin_col,
        how="left"
    )


    # 5. Build shapes list: (geometry, FSI value)
    # Ensure FSI column exists after merge
    if "FSI_masked" not in hybas_fsi.columns:
        raise ValueError(
            f"'FSI_masked' column missing after merge. "
            f"Available columns: {list(hybas_fsi.columns)}"
        )

    shapes = [
        (geom, val)
        for geom, val in zip(hybas_fsi.geometry, hybas_fsi["FSI_masked"])
        if val is not None and not np.isnan(val)
    ]

    # 6. Rasterise to CHIRPS grid
    fsi_raster = rasterize(
        shapes=shapes,
        out_shape=shape,
        transform=chirps_transform,
        fill=np.nan,
        dtype="float32",
    )

    # 7. Rescale 0–1
    valid = ~np.isnan(fsi_raster)
    if not np.any(valid):
        raise ValueError("FSI rasterisation produced no valid pixels.")

    minv = np.nanmin(fsi_raster)
    maxv = np.nanmax(fsi_raster)

    fsi_rescaled = np.full_like(fsi_raster, np.nan, dtype="float32")
    fsi_rescaled[valid] = (fsi_raster[valid] - minv) / (maxv - minv)

    return fsi_rescaled
