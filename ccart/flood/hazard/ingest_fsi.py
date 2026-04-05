"""
Module: ingest_fsi
CCART-Floods Framework
-------------------------------------------------------------

Purpose
-------
Load the Flood Susceptibility Index (FSI), align it to the CHIRPS grid, and
mask it to the India boundary. This provides a clean, reusable FSI layer for
the hazard engine.

Author
------
CCART Team
"""

from pathlib import Path
import numpy as np
import geopandas as gpd
import rasterio
from rasterio.warp import reproject, Resampling
import rasterio.mask

from ccart.flood.chirps.ingest_chirps import load_chirps  # for grid + india_geom


def load_india_boundary(india_shp: Path):
    """
    Load India boundary in EPSG:4326 and return geometry list.
    """
    india = gpd.read_file(india_shp).to_crs("EPSG:4326")
    india_geom = [india.union_all()]
    return india_geom


def load_fsi_raw(fsi_path: Path):
    """
    Load raw FSI raster.

    Returns
    -------
    fsi_arr : 2D float32 ndarray
    fsi_transform : affine.Affine
    fsi_crs : rasterio.crs.CRS
    """
    with rasterio.open(fsi_path) as src:
        fsi_arr = src.read(1).astype("float32")
        fsi_transform = src.transform
        fsi_crs = src.crs
    return fsi_arr, fsi_transform, fsi_crs


def reproject_fsi_to_chirps(fsi_arr, fsi_transform, fsi_crs,
                            chirps_shape, chirps_transform,
                            max_valid: float = 1.0):
    """
    Reproject FSI to the CHIRPS grid and clean values.

    Parameters
    ----------
    max_valid : float
        Values above this are treated as invalid and set to NaN.

    Returns
    -------
    fsi_on_chirps : 2D float32 ndarray
    """
    fsi_on_chirps = np.zeros(chirps_shape, dtype="float32")

    reproject(
        source=fsi_arr,
        destination=fsi_on_chirps,
        src_transform=fsi_transform,
        src_crs=fsi_crs,
        dst_transform=chirps_transform,
        dst_crs="EPSG:4326",
        resampling=Resampling.bilinear
    )

    # Clean: enforce [0, max_valid], NaN outside
    fsi_on_chirps = np.where(
        (fsi_on_chirps >= 0) & (fsi_on_chirps <= max_valid),
        fsi_on_chirps,
        np.nan
    ).astype("float32")

    return fsi_on_chirps


def ingest_fsi(fsi_path: Path,
               india_shp: Path,
               chirps_start_year: int,
               chirps_end_year: int):
    """
    High-level helper to:
      1) load CHIRPS metadata (grid + India geometry)
      2) load raw FSI
      3) reproject FSI to CHIRPS grid
      4) return FSI on CHIRPS + metadata

    Returns
    -------
    fsi_on_chirps : 2D float32 ndarray
    meta : dict
        {
          "chirps_shape": (rows, cols),
          "chirps_transform": Affine,
          "chirps_crs": "EPSG:4326",
          "india_geom": list[geometry]
        }
    """

    # 1) CHIRPS grid + India geometry
    chirps_meta = load_chirps(
        start_year=chirps_start_year,
        end_year=chirps_end_year
    )
    chirps_shape = chirps_meta["shape"]
    chirps_transform = chirps_meta["transform"]
    india_geom = chirps_meta["india_geom"]  # already EPSG:4326

    # 2) Raw FSI
    fsi_arr, fsi_transform, fsi_crs = load_fsi_raw(fsi_path)

    # 3) Reproject to CHIRPS
    fsi_on_chirps = reproject_fsi_to_chirps(
        fsi_arr=fsi_arr,
        fsi_transform=fsi_transform,
        fsi_crs=fsi_crs,
        chirps_shape=chirps_shape,
        chirps_transform=chirps_transform,
        max_valid=1.0
    )

    meta = {
        "chirps_shape": chirps_shape,
        "chirps_transform": chirps_transform,
        "chirps_crs": "EPSG:4326",
        "india_geom": india_geom,
    }

    return fsi_on_chirps, meta
