"""
Module: utils_fsi
CCART-Floods Framework
-------------------------------------------------------------

Purpose
-------
Shared utility functions for the FSI subsystem:
- Min–max normalisation
- Soil encoding helpers
- Spatial join wrappers
- Boundary masking utilities

These utilities keep the FSI codebase modular, reusable, and clean.
"""

import numpy as np
import pandas as pd
import geopandas as gpd
import rasterio

# ============================================================
# Normalisation utilities
# ============================================================

def normalise(series: pd.Series) -> pd.Series:
    """Min–max normalisation with safe handling of constant columns."""
    min_val = series.min()
    max_val = series.max()
    if max_val - min_val == 0:
        return pd.Series([0.5] * len(series), index=series.index)
    return (series - min_val) / (max_val - min_val)

# ============================================================
# Soil encoding utilities
# ============================================================

def encode_soils(df: pd.DataFrame, col="Soil type") -> pd.DataFrame:
    """One-hot encodes soil categories and computes a soil block score."""
    dummies = pd.get_dummies(df[col], prefix="Soil")
    df = pd.concat([df, dummies], axis=1)
    df["Soil_block"] = dummies.mean(axis=1)
    return df

# ============================================================
# Spatial utilities
# ============================================================

def spatial_join_points_to_polygons(points_gdf, poly_gdf, how="left"):
    """Wrapper for spatial join using 'within'."""
    return gpd.sjoin(points_gdf, poly_gdf, how=how, predicate="within")

# ============================================================
# Masking utilities
# ============================================================

def mask_to_boundary(raster, boundary_gdf, transform):
    """
    Applies a polygon mask to a raster.
    Pixels outside the boundary become NaN.
    """
    mask = rasterio.features.geometry_mask(
        boundary_gdf.geometry,
        out_shape=raster.shape,
        transform=transform,
        invert=True
    )
    raster[~mask] = np.nan
    return raster
