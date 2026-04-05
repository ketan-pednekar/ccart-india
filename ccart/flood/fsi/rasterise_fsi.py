"""
Module: rasterise_fsi
CCART-Floods Framework
-------------------------------------------------------------

Purpose
-------
Rasterises FSI v1.2 (point-based GeoDataFrame) to the CHIRPS grid
and prepares the susceptibility raster for hazard modelling.

This module performs:
    1. Rasterisation of FSI_masked (empirical basins only)
    2. Cleaning (keep only 0–1 values, else NaN)
    3. Min–max rescaling to full 0–1 range
    4. Output of a CHIRPS-aligned FSI raster

This produces the canonical susceptibility layer:
    ccart_floods_fsi_v1_2_rescaled.tif

Inputs
------
- gdf_fsi_v1_2 : GeoDataFrame with FSI_masked column
- chirps_transform : affine transform of CHIRPS grid
- shape : (rows, cols) of CHIRPS grid

Outputs
-------
- fsi_rescaled : 2D numpy array (float32, 0–1, NaN outside empirical basins)
"""

import numpy as np
import rasterio
import rasterio.features

# ------------------------------------------------------------
# 1. Rasterise masked FSI to CHIRPS grid
# ------------------------------------------------------------

def rasterise_fsi(gdf_fsi_v1_2, chirps_transform, shape):
    """
    Rasterise FSI_masked to CHIRPS grid.

    Parameters
    ----------
    gdf_fsi_v1_2 : GeoDataFrame
        Must contain column "FSI_masked" (NaN for proxy basins).
    chirps_transform : affine.Affine
        Transform of CHIRPS grid.
    shape : tuple
        (rows, cols) of CHIRPS grid.

    Returns
    -------
    fsi_raster : 2D float32 array
        Raw rasterised FSI (0–1, NaN outside empirical basins).
    """

    shapes = [
        (geom, val)
        for geom, val in zip(gdf_fsi_v1_2.geometry, gdf_fsi_v1_2["FSI_masked"])
        if geom is not None
    ]

    fsi_raster = rasterio.features.rasterize(
        shapes,
        out_shape=shape,
        transform=chirps_transform,
        fill=np.nan,
        dtype="float32"
    )

    return fsi_raster

# ------------------------------------------------------------
# 2. Clean raster (keep only 0–1)
# ------------------------------------------------------------

def clean_fsi(fsi_raster):
    """
    Ensures FSI is strictly within 0–1, else NaN.

    Returns
    -------
    fsi_clean : 2D float32 array
    """
    return np.where(
        (fsi_raster >= 0) & (fsi_raster <= 1.0),
        fsi_raster,
        np.nan
    ).astype("float32")

# ------------------------------------------------------------
# 3. Min–max rescale to full 0–1 range
# ------------------------------------------------------------

def rescale_fsi(fsi_clean):
    """
    Min–max rescales valid FSI values to full 0–1 range.

    Returns
    -------
    fsi_rescaled : 2D float32 array
    """

    valid = np.isfinite(fsi_clean)
    if not valid.any():
        raise ValueError("FSI raster contains no valid values to rescale.")

    fsi_min = float(fsi_clean[valid].min())
    fsi_max = float(fsi_clean[valid].max())

    fsi_rescaled = np.where(
        valid,
        (fsi_clean - fsi_min) / (fsi_max - fsi_min),
        np.nan
    ).astype("float32")

    return fsi_rescaled

# ------------------------------------------------------------
# 4. Full pipeline wrapper
# ------------------------------------------------------------

def rasterise_clean_rescale_fsi(gdf_fsi_v1_2, chirps_transform, shape):
    """
    Full pipeline:
        1. Rasterise
        2. Clean
        3. Rescale

    Returns
    -------
    fsi_rescaled : 2D float32 array
    """

    fsi_raw = rasterise_fsi(gdf_fsi_v1_2, chirps_transform, shape)
    fsi_clean = clean_fsi(fsi_raw)
    fsi_rescaled = rescale_fsi(fsi_clean)

    return fsi_rescaled
