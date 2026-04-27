"""
Module: compute_fsi
CCART-Floods Framework (v2)
-------------------------------------------------------------
Unified builder for Flood Susceptibility Index (FSI).

FSI v1.1:
    - Purely empirical IndoFloods geomorphology + soils
FSI v1.2:
    - v1.1 + HydroBASINS hydrological context + proxy mask

The recommended FSI for CCART-Floods is v1.2.
"""

import numpy as np
import pandas as pd
import geopandas as gpd
from shapely.geometry import Point
from pathlib import Path

from ccart.flood.config import load_paths


# ============================================================
# Load config paths
# ============================================================

paths = load_paths()
project_root = Path(paths["project_root"])

CATCHMENT_CSV = project_root / paths["data"]["indofloods"]["catchment"]
EVENTS_CSV    = project_root / paths["data"]["indofloods"]["events"]
META_CSV      = project_root / paths["data"]["indofloods"]["metadata"]
PRECIP_CSV    = project_root / paths["data"]["indofloods"]["precip"]

HYBAS_SHP     = project_root / paths["data"]["hybas"]
INDIA_SHP     = project_root / paths["data"]["india_boundary"]


# ============================================================
# Basin name cleaning + audit
# ============================================================

def clean_basin_names(df):
    """Standardise IndoFloods basin names to avoid duplicates."""
    df["Basin"] = df["Basin"].astype(str).str.strip()

    replacements = {
        # Ganga–Brahmaputra–Meghna system
        "Ganga - Brahmaputra -Meghna/Barak":
            "Ganga - Brahmaputra - Meghna/Barak",

        # Subarnarekha
        "Subernarekha": "Subarnarekha",

        # West-flowing rivers
        "West flowing rivers from Tapi of Tadri":
            "West flowing rivers from Tapi to Tadri",
        "West flowing rivers from  Tapi to Tadri":
            "West flowing rivers from Tapi to Tadri",

        # Brahmani–Baitarni
        "Brahmni - Baitarni": "Brahmani and Baitarni",
        " Brahmni - Baitarni": "Brahmani and Baitarni",
    }

    df["Basin"] = df["Basin"].replace(replacements)
    df["Basin"] = df["Basin"].str.strip()

    return df


def audit_basin_names(df):
    """Print unique basin names and counts for diagnostics."""
    print("\n[IndoFloods] Basin Name Audit")
    print("--------------------------------")
    counts = df["Basin"].value_counts(dropna=False)
    for basin, count in counts.items():
        print(f"{basin:50s}  count={count}")
    print("--------------------------------\n")


# ============================================================
# Helper: Min–max normalisation
# ============================================================

def _normalise(series: pd.Series) -> pd.Series:
    min_val = series.min()
    max_val = series.max()
    if max_val - min_val == 0:
        return pd.Series([0.5] * len(series), index=series.index)
    return (series - min_val) / (max_val - min_val)


# ============================================================
# FSI v1.1 — empirical IndoFloods layer
# ============================================================

def compute_fsi_v1_1() -> gpd.GeoDataFrame:
    """Compute FSI v1.1 using IndoFloods catchment descriptors."""

    df_catch = pd.read_csv(CATCHMENT_CSV)
    df_meta  = pd.read_csv(META_CSV)

    # Clean basin names BEFORE merging
    df_meta = clean_basin_names(df_meta)

    # Optional: audit basin names (can be commented out later)
    audit_basin_names(df_meta)

    num_cols = [
        "Drainage Density",
        "Catchment Relief",
        "Ruggedness Number",
        "Elongation Ratio",
        "Form Factor",
        "Annual Precipitation"
    ]

    df = df_catch.copy()

    # Normalise geomorphology
    for col in num_cols:
        df[col + "_norm"] = _normalise(df[col])

    # Soil encoding
    soil_dummies = pd.get_dummies(df["Soil type"], prefix="Soil")
    df = pd.concat([df, soil_dummies], axis=1)
    soil_cols = [c for c in df.columns if c.startswith("Soil_")]
    df["Soil_block"] = df[soil_cols].mean(axis=1)

    # FSI v1.1
    fsi_cols = [col + "_norm" for col in num_cols] + ["Soil_block"]
    df["FSI_v1_1"] = df[fsi_cols].mean(axis=1).clip(0, 1)

    # Join metadata (now cleaned)
    meta_cols = ["GaugeID", "Latitude", "Longitude", "Basin", "State"]
    df = df.merge(df_meta[meta_cols], on="GaugeID", how="left")

    # Convert to GeoDataFrame
    geometry = [Point(xy) for xy in zip(df["Longitude"], df["Latitude"])]
    gdf = gpd.GeoDataFrame(df, geometry=geometry, crs="EPSG:4326")

    # --------------------------------------------------------
    # NEW: Mask gauges to India (Option A: point-level masking)
    # --------------------------------------------------------
    india = gpd.read_file(INDIA_SHP).to_crs("EPSG:4326")
    gdf = gdf[gdf.within(india.unary_union)]

    return gdf


# ============================================================
# FSI v1.2 — hydrology-enhanced layer
# ============================================================

def compute_fsi_v1_2(gdf_v1_1: gpd.GeoDataFrame) -> gpd.GeoDataFrame:
    """Enhance FSI v1.1 with HydroBASINS hydrological context."""

    gdf_hybas = gpd.read_file(HYBAS_SHP).to_crs("EPSG:4326")
    india = gpd.read_file(INDIA_SHP).to_crs("EPSG:4326")

    # Keep only basins intersecting India (hydrological domain)
    gdf_hybas = gdf_hybas[gdf_hybas.intersects(india.unary_union)]

    # Points are already masked to India in v1.1
    points_in_india = gdf_v1_1  # already within India

    # Identify empirical vs proxy basins
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
    gdf_hybas["Proxy_flag"] = np.where(gdf_hybas["n_gauges"] == 0, 1, 0)

    # Spatial join: assign hydrological attributes to points
    gdf_join = gpd.sjoin(
        gdf_v1_1.reset_index(drop=True),
        gdf_hybas[["HYBAS_ID", "UP_AREA", "SUB_AREA", "ORDER", "Proxy_flag", "geometry"]],
        how="left",
        predicate="within"
    )

    # Normalise hydrological variables
    hydro_cols = ["UP_AREA", "SUB_AREA", "ORDER"]
    for col in hydro_cols:
        gdf_join[col + "_norm"] = _normalise(gdf_join[col])

    # Compute FSI v1.2
    gdf_join["FSI_v1_2"] = (
        gdf_join["FSI_v1_1"] * 0.5 +
        gdf_join["UP_AREA_norm"] * 0.5
    ).clip(0, 1)

    # Apply empirical mask (proxy basins → NaN)
    gdf_join["FSI_masked"] = np.where(
        gdf_join["Proxy_flag"] == 1,
        np.nan,
        gdf_join["FSI_v1_2"]
    )

    # Points are already India-only; no further political masking needed here
    return gdf_join


# ============================================================
# Unified entry point
# ============================================================

def compute_fsi() -> gpd.GeoDataFrame:
    gdf_v1_1 = compute_fsi_v1_1()
    gdf_v1_2 = compute_fsi_v1_2(gdf_v1_1)
    return gdf_v1_2
