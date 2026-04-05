"""
Module: build_fsi_v1_2
CCART-Floods Framework
-------------------------------------------------------------

Purpose
-------
Enhances FSI v1.1 with hydrological context from HydroBASINS
to produce FSI v1.2 — the recommended susceptibility layer.

FSI v1.2 includes:
    - FSI_v1_1 (empirical geomorphology + soils)
    - Hydrological descriptors (UP_AREA, SUB_AREA, ORDER)
    - Proxy basin identification
    - Strict 0–1 scaling
    - Empirical mask (proxy basins → NaN)

This module outputs a GeoDataFrame ready for rasterisation.
"""

import numpy as np
import geopandas as gpd
import pandas as pd

from ccart.flood.config import (
    HYBAS_SHP,
    INDIA_SHP
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

def build_fsi_v1_2(gdf_v1_1: gpd.GeoDataFrame) -> gpd.GeoDataFrame:
    """
    Enhances FSI v1.1 with HydroBASINS hydrological context.

    Parameters
    ----------
    gdf_v1_1 : GeoDataFrame
        Output of build_fsi_v1_1(), containing FSI_v1_1 and coordinates.

    Returns
    -------
    gdf : GeoDataFrame
        Points with FSI_v1_2, hydrological attributes, and empirical mask.
    """

    # --------------------------------------------------------
    # 1. Load HydroBASINS + India boundary
    # --------------------------------------------------------
    gdf_hybas = gpd.read_file(HYBAS_SHP).to_crs("EPSG:4326")
    india = gpd.read_file(INDIA_SHP).to_crs("EPSG:4326")

    # Keep only basins intersecting India
    gdf_hybas = gdf_hybas[gdf_hybas.intersects(india.unary_union)]

    # --------------------------------------------------------
    # 2. Identify empirical vs proxy basins
    # --------------------------------------------------------
    points_in_india = gdf_v1_1[gdf_v1_1.within(india.unary_union)]

    join = gpd.sjoin(
        gdf_hybas[["HYBAS_ID", "geometry"]].reset_index(drop=True),
        points_in_india[["GaugeID", "geometry"]].reset_index(drop=True),
        how="left",
        predicate="contains"
    )

    counts = (
        join.groupby("HYBAS_ID")["GaugeID"]
            .nunique()
            .reset_index(name="n_gauges")
    )

    gdf_hybas = gdf_hybas.merge(counts, on="HYBAS_ID", how="left")
    gdf_hybas["n_gauges"] = gdf_hybas["n_gauges"].fillna(0)

    # Proxy_flag = 1 → no empirical gauges
    gdf_hybas["Proxy_flag"] = np.where(gdf_hybas["n_gauges"] == 0, 1, 0)

    # --------------------------------------------------------
    # 3. Spatial join: assign HydroBASINS attributes to gauges
    # --------------------------------------------------------
    gdf_join = gpd.sjoin(
        gdf_v1_1.reset_index(drop=True),
        gdf_hybas[["HYBAS_ID", "UP_AREA", "SUB_AREA", "ORDER", "Proxy_flag", "geometry"]],
        how="left",
        predicate="within"
    )

    # --------------------------------------------------------
    # 4. Normalise hydrological variables
    # --------------------------------------------------------
    hydro_cols = ["UP_AREA", "SUB_AREA", "ORDER"]

    for col in hydro_cols:
        gdf_join[col + "_norm"] = _normalise(gdf_join[col])

    # --------------------------------------------------------
    # 5. Compute FSI v1.2 (strict 0–1)
    # --------------------------------------------------------
    gdf_join["FSI_v1_2"] = (
        gdf_join["FSI_v1_1"] * 0.5 +
        gdf_join["UP_AREA_norm"] * 0.5
    ).clip(0, 1)

    # --------------------------------------------------------
    # 6. Apply empirical mask (proxy basins → NaN)
    # --------------------------------------------------------
    gdf_join["FSI_masked"] = np.where(
        gdf_join["Proxy_flag"] == 1,
        np.nan,
        gdf_join["FSI_v1_2"]
    )

    return gdf_join


if __name__ == "__main__":
    print("FSI v1.2 builder loaded. Use build_fsi_v1_1() first.")
