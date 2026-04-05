"""
Module: build_fsi_v1_1
CCART-Floods Framework
-------------------------------------------------------------

Purpose
-------
Computes Flood Susceptibility Index (FSI) v1.1 using only
INDOFLOODS catchment descriptors and soil information.

FSI v1.1 is the purely empirical susceptibility layer before
introducing hydrological context (FSI v1.2).

Outputs
-------
GeoDataFrame with:
    - Normalised geomorphological variables
    - Soil dummy encodings
    - FSI_v1_1 (strict 0–1 range)
"""

import pandas as pd
import numpy as np
import geopandas as gpd
from shapely.geometry import Point

from ccart.flood.config import (
    CATCHMENT_CSV,
    META_CSV
)

# ------------------------------------------------------------
# Helper: Min–max normalisation
# ------------------------------------------------------------

def _normalise(series: pd.Series) -> pd.Series:
    """Min–max normalisation with safe handling of constant columns."""
    min_val = series.min()
    max_val = series.max()
    if max_val - min_val == 0:
        return pd.Series([0.5] * len(series), index=series.index)
    return (series - min_val) / (max_val - min_val)

# ------------------------------------------------------------
# Main function
# ------------------------------------------------------------

def build_fsi_v1_1() -> gpd.GeoDataFrame:
    """Computes FSI v1.1 using INDOFLOODS catchment descriptors."""

    # 1. Load datasets
    df_catch = pd.read_csv(CATCHMENT_CSV)
    df_meta  = pd.read_csv(META_CSV)

    # 2. Select numerical variables
    num_cols = [
        "Drainage Density",
        "Catchment Relief",
        "Ruggedness Number",
        "Elongation Ratio",
        "Form Factor",
        "Annual Precipitation"
    ]

    df = df_catch.copy()

    # Normalise each variable
    for col in num_cols:
        df[col + "_norm"] = _normalise(df[col])

    # 3. Encode soil types
    soil_dummies = pd.get_dummies(df["Soil type"], prefix="Soil")
    df = pd.concat([df, soil_dummies], axis=1)

    soil_cols = [c for c in df.columns if c.startswith("Soil_")]
    df["Soil_block"] = df[soil_cols].mean(axis=1)

    # 4. Compute FSI v1.1
    fsi_cols = [col + "_norm" for col in num_cols] + ["Soil_block"]
    df["FSI_v1_1"] = df[fsi_cols].mean(axis=1).clip(0, 1)

    # 5. Join metadata
    meta_cols = ["GaugeID", "Latitude", "Longitude", "Basin", "State"]
    df = df.merge(df_meta[meta_cols], on="GaugeID", how="left")

    # 6. Convert to GeoDataFrame
    geometry = [Point(xy) for xy in zip(df["Longitude"], df["Latitude"])]
    gdf = gpd.GeoDataFrame(df, geometry=geometry, crs="EPSG:4326")

    return gdf

if __name__ == "__main__":
    gdf = build_fsi_v1_1()
    print("FSI v1.1 computed for", len(gdf), "gauges.")
