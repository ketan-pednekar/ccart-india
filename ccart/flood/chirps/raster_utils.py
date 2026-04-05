"""
Module: raster_utils
CCART-Floods Framework
-------------------------------------------------------------

Purpose
-------
Shared raster utilities for CHIRPS ingestion, rainfall metrics, and hazard
computation. This module ensures that all rasters are aligned to the CHIRPS
grid and masked consistently to the India boundary.

Functions
---------
- reproject_to_chirps()
- mask_to_india()
- empty_like_chirps()
- check_alignment()

Author
------
CCART Team
"""

import numpy as np
import rasterio
from rasterio.warp import reproject, Resampling
import rasterio.mask


# ============================================================
# Reproject any raster to the CHIRPS grid
# ============================================================

def reproject_to_chirps(
    src_arr,
    src_transform,
    src_crs,
    chirps_shape,
    chirps_transform,
    resampling=Resampling.bilinear
):
    """
    Reproject a source raster to the CHIRPS grid.

    Parameters
    ----------
    src_arr : 2D ndarray
        Source raster array.
    src_transform : affine.Affine
        Transform of the source raster.
    src_crs : str or CRS
        CRS of the source raster.
    chirps_shape : tuple
        (rows, cols) of the CHIRPS grid.
    chirps_transform : affine.Affine
        Transform of the CHIRPS grid.
    resampling : rasterio.warp.Resampling
        Resampling method (default: bilinear).

    Returns
    -------
    dst : 2D float32 ndarray
        Reprojected raster aligned to CHIRPS.
    """

    dst = np.zeros(chirps_shape, dtype="float32")

    reproject(
        source=src_arr,
        destination=dst,
        src_transform=src_transform,
        src_crs=src_crs,
        dst_transform=chirps_transform,
        dst_crs="EPSG:4326",
        resampling=resampling
    )

    return dst


# ============================================================
# Mask raster to India boundary
# ============================================================

def mask_to_india(arr, transform, india_geom):
    """
    Mask a raster to the India boundary.

    Parameters
    ----------
    arr : 2D ndarray
        Raster to mask.
    transform : affine.Affine
        Raster transform.
    india_geom : list of shapely geometries
        India boundary geometry.

    Returns
    -------
    masked : 2D float32 ndarray
        Array with values outside India set to NaN.
    """

    # Rasterio expects a 3D array for masking
    arr3d = arr[np.newaxis, :, :]

    masked, _ = rasterio.mask.mask(
        {
            "transform": transform,
            "height": arr.shape[0],
            "width": arr.shape[1],
            "crs": "EPSG:4326"
        },
        shapes=india_geom,
        filled=True,
        nodata=np.nan,
        data=arr3d
    )

    return masked[0].astype("float32")


# ============================================================
# Create an empty raster aligned to CHIRPS
# ============================================================

def empty_like_chirps(chirps_shape, fill=np.nan, dtype="float32"):
    """
    Create an empty raster aligned to CHIRPS.

    Parameters
    ----------
    chirps_shape : tuple
        (rows, cols)
    fill : float
        Fill value (default: NaN)
    dtype : str
        Data type (default: float32)

    Returns
    -------
    arr : 2D ndarray
        Empty raster.
    """
    arr = np.full(chirps_shape, fill, dtype=dtype)
    return arr


# ============================================================
# Check alignment between two rasters
# ============================================================

def check_alignment(shape_a, transform_a, shape_b, transform_b):
    """
    Ensure two rasters share the same grid.

    Raises
    ------
    ValueError if shapes or transforms differ.
    """

    if shape_a != shape_b:
        raise ValueError(f"Shape mismatch: {shape_a} vs {shape_b}")

    if transform_a != transform_b:
        raise ValueError("Transform mismatch between rasters.")

    return True
