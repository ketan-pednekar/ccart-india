"""
Module: export_fsi_raster
CCART-Floods Framework
-------------------------------------------------------------

Purpose
-------
Exports the final FSI v1.2 susceptibility raster (already rasterised,
cleaned, and rescaled) to a CHIRPS-aligned GeoTIFF.

This module writes the canonical CCART-Floods susceptibility layer:

    ccart_floods_fsi_v1_2_rescaled.tif

Inputs
------
- fsi_rescaled : 2D numpy array (float32)
    Output of rasterise_clean_rescale_fsi()
- chirps_transform : affine.Affine
    Transform of CHIRPS grid
- crs : str
    Coordinate reference system (default: EPSG:4326)
- out_path : str or Path
    Output GeoTIFF path

Outputs
-------
- GeoTIFF written to disk with:
    - float32 dtype
    - NaN nodata
    - CHIRPS grid alignment
"""

import numpy as np
import rasterio
from rasterio.transform import Affine

# ------------------------------------------------------------
# Export function
# ------------------------------------------------------------

def export_fsi_raster(
    fsi_rescaled: np.ndarray,
    chirps_transform: Affine,
    out_path,
    crs: str = "EPSG:4326"
):
    """
    Writes the final FSI raster to GeoTIFF.

    Parameters
    ----------
    fsi_rescaled : np.ndarray
        2D float32 array (0–1, NaN outside empirical basins)
    chirps_transform : affine.Affine
        CHIRPS grid transform
    out_path : str or Path
        Output GeoTIFF path
    crs : str
        Coordinate reference system (default EPSG:4326)
    """

    rows, cols = fsi_rescaled.shape

    profile = {
        "driver": "GTiff",
        "height": rows,
        "width": cols,
        "count": 1,
        "dtype": "float32",
        "crs": crs,
        "transform": chirps_transform,
        "nodata": np.nan,
        "compress": "lzw"
    }

    with rasterio.open(out_path, "w", **profile) as dst:
        dst.write(fsi_rescaled.astype("float32"), 1)

    print(f"FSI raster saved → {out_path}")
