"""
Module: raster_utils
CCART-Floods Framework (v2)
-------------------------------------------------------------
Shared raster utilities for ingestion, rainfall metrics, FSI
computation, and hazard generation.

This version is:
- config-driven
- CRS-safe
- geometry-agnostic
- modular and reusable
"""

from pathlib import Path
from typing import Tuple, List

import numpy as np
import rasterio
import rasterio.mask
from rasterio.warp import reproject, Resampling

from ccart.flood.config import load_flood_params


# ============================================================
# Load config
# ============================================================

params = load_flood_params()
DEFAULT_CRS = "EPSG:4326"


# ============================================================
# Reproject any raster to a target grid
# ============================================================

def reproject_to_grid(
    src_arr: np.ndarray,
    src_transform,
    src_crs: str,
    dst_shape: Tuple[int, int],
    dst_transform,
    dst_crs: str = DEFAULT_CRS,
    resampling: Resampling = Resampling.bilinear
) -> np.ndarray:
    """
    Reproject a raster array to a target grid.

    Parameters
    ----------
    src_arr : 2D ndarray
        Source raster.
    src_transform : Affine
        Source transform.
    src_crs : str
        Source CRS.
    dst_shape : tuple
        (rows, cols) of target grid.
    dst_transform : Affine
        Target transform.
    dst_crs : str
        Target CRS.
    resampling : Resampling
        Resampling method.

    Returns
    -------
    dst : 2D float32 ndarray
        Reprojected raster.
    """

    dst = np.zeros(dst_shape, dtype="float32")

    reproject(
        source=src_arr,
        destination=dst,
        src_transform=src_transform,
        src_crs=src_crs,
        dst_transform=dst_transform,
        dst_crs=dst_crs,
        resampling=resampling
    )

    return dst


# ============================================================
# Mask raster to any geometry
# ============================================================

def mask_to_geometry(
    arr: np.ndarray,
    transform,
    geom_list: List,
    crs: str = DEFAULT_CRS,
    nodata: float = np.nan
) -> np.ndarray:
    """
    Mask a raster to an arbitrary geometry.

    Parameters
    ----------
    arr : 2D ndarray
        Raster to mask.
    transform : Affine
        Raster transform.
    geom_list : list
        List of shapely geometries.
    crs : str
        CRS of raster.
    nodata : float
        Fill value outside geometry.

    Returns
    -------
    masked : 2D ndarray
        Masked raster.
    """

    arr3d = arr[np.newaxis, :, :]

    masked, _ = rasterio.mask.mask(
        {
            "transform": transform,
            "height": arr.shape[0],
            "width": arr.shape[1],
            "crs": crs
        },
        shapes=geom_list,
        filled=True,
        nodata=nodata,
        data=arr3d
    )

    return masked[0].astype("float32")


# ============================================================
# Create an empty raster aligned to a target grid
# ============================================================

def empty_like(
    shape: Tuple[int, int],
    fill: float = np.nan,
    dtype: str = "float32"
) -> np.ndarray:
    """
    Create an empty raster with given shape.

    Parameters
    ----------
    shape : tuple
        (rows, cols)
    fill : float
        Fill value.
    dtype : str
        Data type.

    Returns
    -------
    arr : 2D ndarray
        Empty raster.
    """
    return np.full(shape, fill, dtype=dtype)


# ============================================================
# Check alignment between two rasters
# ============================================================

def check_alignment(
    shape_a: Tuple[int, int],
    transform_a,
    shape_b: Tuple[int, int],
    transform_b
) -> bool:
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
