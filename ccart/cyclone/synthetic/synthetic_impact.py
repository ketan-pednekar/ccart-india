"""
CCART Synthetic Impact Module
-----------------------------
Handles:
- district-level hazard statistics
- merging inland mask
- raw impact computation
- attaching losses to exposure points
- district-level aggregation
"""

import pandas as pd
from climada.engine import Impact


# ------------------------------------------------------------
# 1. Compute district hazard statistics
# ------------------------------------------------------------
def compute_hazard_stats(hazard, districts_gdf):
    """
    Compute district-level hazard statistics (max and mean intensity),
    compatible with latest CLIMADA (no Centroids.to_gdf()).
    """

    import geopandas as gpd
    import numpy as np

    # 1) Peak wind per centroid from dense matrix
    intensity_dense = hazard.intensity.toarray()          # (n_events, n_centroids)
    wind_max = intensity_dense.max(axis=0).reshape(-1)
    wind_mean = intensity_dense.mean(axis=0).reshape(-1)

    # 2) Raw centroid coordinates
    lons = np.asarray(hazard.centroids.lon).reshape(-1)
    lats = np.asarray(hazard.centroids.lat).reshape(-1)

    if not (len(wind_max) == len(lons) == len(lats)):
        raise ValueError(
            f"Centroid array mismatch: max={len(wind_max)}, lon={len(lons)}, lat={len(lats)}"
        )

    # 3) Geometry + GeoDataFrame
    geom = gpd.points_from_xy(lons, lats)
    cent = gpd.GeoDataFrame(
        {"max_intensity": wind_max, "mean_intensity": wind_mean},
        geometry=geom,
        crs="EPSG:4326"
    )

    # 4) Spatial join (intersects is safer than within)
    joined = cent.sjoin(
        districts_gdf[["District", "geometry"]],
        how="left",
        predicate="intersects"
    )

    # 5) Aggregate to district level
    stats = (
        joined.groupby("District")
        .agg({
            "max_intensity": "max",
            "mean_intensity": "mean",
        })
        .reset_index()
    )

    return stats

# ------------------------------------------------------------
# 2. Merge inland mask into hazard stats
# ------------------------------------------------------------
def merge_inland_mask(hazard_stats, districts_gdf):
    """
    Merge inland distance and inland flag into hazard stats.

    Adds:
        dist_to_coast_km
        is_inland
    """
    return hazard_stats.merge(
        districts_gdf[["District", "dist_to_coast_km", "is_inland"]],
        on="District",
        how="left",
    )


# ------------------------------------------------------------
# 3. Compute raw impact (exposure × vulnerability × hazard)
# ------------------------------------------------------------
def compute_raw_impact_pipeline(exposures, impf_set, hazard):
    """
    Compute raw impact using CLIMADA Impact().

    Returns:
        exp_with_loss (Exposures)
        impact_raw (Impact)
    """
    impact_raw = Impact()
    impact_raw.calc(exposures, impf_set, hazard)

    # Attach losses to exposure points
    exposures.gdf["loss_usd"] = impact_raw.eai_exp

    return exposures, impact_raw


# ------------------------------------------------------------
# 4. Aggregate raw losses to districts
# ------------------------------------------------------------
def aggregate_district_losses(exp_with_loss, districts_gdf):
    exp = exp_with_loss.gdf.copy()

    # SAFETY: remove any leftover join columns
    exp = exp.drop(columns=["index_left", "index_right"], errors="ignore")

    # SAFETY: remove any accidental District column from exposures
    if "District" in exp.columns:
        exp = exp.drop(columns=["District"])

    # Spatial join
    joined = exp.sjoin(
        districts_gdf[["District", "geometry"]],
        how="left",
        predicate="within"
    )

    # If no matches, create District column explicitly
    if "District" not in joined.columns:
        joined["District"] = None

    # Aggregate
    out = (
        joined.groupby("District")["loss_usd"]
        .sum()
        .reset_index()
    )

    return out




