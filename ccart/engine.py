"""
CCART v1.4 — Engine Orchestrator (India-ready, with hazard floor + robust district handling)

- Uses a canonical 'district_norm' key internally for all merges.
- Normalizes 'district' and 'state' from the input GeoJSON.
- Keeps original 'district' and 'state' columns for readability.
"""

from typing import Optional

import geopandas as gpd
import pandas as pd

from .hazard import build_hazard, compute_district_hazard_stats
from .exposure import load_litpop_for_state
from .vulnerability import build_vulnerability_curves
from .impact import (
    compute_raw_impact,
    attach_losses_to_points,
    aggregate_district_loss,
)
from .calibration import calibrate_to_total
from .hwe import build_hwe_weights


# Simple, physically motivated hazard floor (m/s)
HAZARD_FLOOR_MS = 25.0   # adjust as needed


def _normalize_name(s: pd.Series) -> pd.Series:
    """Normalize district/state names to a canonical form."""
    return (
        s.astype(str)
         .str.strip()
         .str.upper()
         .str.replace(r"\s+", " ", regex=True)
    )


def run_ccart(
    cyclone_name: str,
    storm_id: str,
    ibtracs_path: str,
    districts_path: str,
    dlna_total: float,
    state_name: str,
    country_code: str = "IND",
    inland_clip_km: Optional[float] = None,
    coastline_path: Optional[str] = None,
):

    # ------------------------------------------------------------
    # 1. Load full-India districts
    # ------------------------------------------------------------
    gdf_all = gpd.read_file(districts_path)

    # Ensure required columns exist
    if "district" not in gdf_all.columns or "state" not in gdf_all.columns:
        raise KeyError(
            "Expected columns 'district' and 'state' in districts file, "
            f"found: {list(gdf_all.columns)}"
        )

    # Normalize names
    gdf_all["district"] = gdf_all["district"].astype(str)
    gdf_all["state"] = gdf_all["state"].astype(str)

    gdf_all["district_norm"] = _normalize_name(gdf_all["district"])
    gdf_all["state_norm"] = _normalize_name(gdf_all["state"])

    state_norm = _normalize_name(pd.Series([state_name])).iloc[0]
    mask_state = gdf_all["state_norm"] == state_norm
    gdf_state = gdf_all[mask_state].copy()

    if gdf_state.empty:
        raise ValueError(
            f"No districts found for state: {state_name} "
            f"(normalized: {state_norm})"
        )

    # Ensure CRS is WGS84
    if gdf_state.crs is None or gdf_state.crs.to_string() != "EPSG:4326":
        gdf_state = gdf_state.to_crs("EPSG:4326")

    # Canonical district key for all merges
    gdf_state["District"] = gdf_state["district_norm"]

    districts = gdf_state[["District", "geometry"]].copy()

    # ------------------------------------------------------------
    # 1B. Optional inland distance clipping
    # ------------------------------------------------------------
    inland_clipping_active = inland_clip_km is not None and coastline_path is not None

    if inland_clipping_active:
        coast = gpd.read_file(coastline_path)
        if coast.crs is None or coast.crs.to_string() != "EPSG:4326":
            coast = coast.to_crs("EPSG:4326")

        districts_proj = districts.to_crs("EPSG:3857")
        coast_proj = coast.to_crs("EPSG:3857")

        centroids_proj = districts_proj.geometry.centroid
        dist_to_coast_m = centroids_proj.distance(coast_proj.unary_union)

        districts["dist_to_coast_km"] = dist_to_coast_m / 1000.0
        districts["is_inland"] = districts["dist_to_coast_km"] > inland_clip_km
    else:
        districts["dist_to_coast_km"] = None
        districts["is_inland"] = False

    # ------------------------------------------------------------
    # 2. Load LitPop exposure
    # ------------------------------------------------------------
    assets_state, exp_dist = load_litpop_for_state(country_code, districts)

    # ------------------------------------------------------------
    # 3. Build hazard
    # ------------------------------------------------------------
    hazard = build_hazard(storm_id, ibtracs_path)

    # ------------------------------------------------------------
    # 4. District-level hazard statistics
    # ------------------------------------------------------------
    hazard_stats = compute_district_hazard_stats(hazard, districts)

    # ------------------------------------------------------------
    # 4B. Apply hazard floor (corrected column name)
    # ------------------------------------------------------------
    if "WindSpeed_Max_mps" in hazard_stats.columns:
        hazard_stats["hazard_ok"] = (
            hazard_stats["WindSpeed_Max_mps"] >= HAZARD_FLOOR_MS
        )
    else:
        raise KeyError(
            "WindSpeed_Max_mps not found in hazard_stats. "
            "Check compute_district_hazard_stats output."
        )

    # ------------------------------------------------------------
    # 5. Vulnerability curves
    # ------------------------------------------------------------
    impf_set = build_vulnerability_curves()

    # ------------------------------------------------------------
    # 6. Raw CLIMADA impact
    # ------------------------------------------------------------
    impact_raw = compute_raw_impact(assets_state, impf_set, hazard)

    # ------------------------------------------------------------
    # 7. Attach losses to points
    # ------------------------------------------------------------
    exp_with_loss = attach_losses_to_points(assets_state, impact_raw)

    # ------------------------------------------------------------
    # 8. Aggregate to districts
    # ------------------------------------------------------------
    district_loss_raw = aggregate_district_loss(exp_with_loss, districts)

    # ------------------------------------------------------------
    # 8B. Inland clipping BEFORE calibration
    # ------------------------------------------------------------
    if inland_clipping_active:
        loss_with_flag = district_loss_raw.merge(
            districts[["District", "is_inland"]],
            on="District",
            how="left",
        )

        coastal = loss_with_flag[loss_with_flag["is_inland"] == False].copy()
        inland = loss_with_flag[loss_with_flag["is_inland"] == True].copy()

        coastal = coastal.drop(columns=["is_inland"])
        inland = inland.drop(columns=["is_inland"])

        coastal_cal = calibrate_to_total(coastal, dlna_total)

        inland_cal = inland.copy()
        inland_cal["loss_usd_cal"] = 0.0

        district_loss_cal = pd.concat([coastal_cal, inland_cal], ignore_index=True)

    else:
        district_loss_cal = calibrate_to_total(district_loss_raw, dlna_total)

    # ------------------------------------------------------------
    # 8C. Apply hazard floor to calibrated losses
    # ------------------------------------------------------------
    district_loss_cal = district_loss_cal.merge(
        hazard_stats[["District", "hazard_ok"]],
        on="District",
        how="left",
    )
    district_loss_cal.loc[district_loss_cal["hazard_ok"] == False, "loss_usd_cal"] = 0.0
    district_loss_cal = district_loss_cal.drop(columns=["hazard_ok"])

    # ------------------------------------------------------------
    # 9. HWE weights
    # ------------------------------------------------------------
    hwe_weights = build_hwe_weights(hazard_stats, exp_dist)

    # ------------------------------------------------------------
    # 9B. Inland clipping for HWE
    # ------------------------------------------------------------
    if inland_clipping_active:
        hwe_with_flag = hwe_weights.merge(
            districts[["District", "is_inland"]],
            on="District",
            how="left",
        )

        hwe_with_flag.loc[hwe_with_flag["is_inland"] == True, "HWE_weight_norm"] = 0.0

        total_coastal_weight = hwe_with_flag["HWE_weight_norm"].sum()
        if total_coastal_weight > 0:
            hwe_with_flag["HWE_weight_norm"] /= total_coastal_weight

        hwe_weights = hwe_with_flag.drop(columns=["is_inland"])

    # ------------------------------------------------------------
    # 9C. Apply hazard floor to HWE weights
    # ------------------------------------------------------------
    hwe_weights = hwe_weights.merge(
        hazard_stats[["District", "hazard_ok"]],
        on="District",
        how="left",
    )
    hwe_weights.loc[hwe_weights["hazard_ok"] == False, "HWE_weight_norm"] = 0.0

    total_weight = hwe_weights["HWE_weight_norm"].sum()
    if total_weight > 0:
        hwe_weights["HWE_weight_norm"] /= total_weight

    hwe_weights = hwe_weights.drop(columns=["hazard_ok"])

    # ------------------------------------------------------------
    # 10. Merge calibrated + HWE with geometry + original names
    # ------------------------------------------------------------
    merged = districts.merge(district_loss_cal, on="District", how="left")
    merged = merged.merge(
        hwe_weights[["District", "HWE_weight_norm"]],
        on="District",
        how="left",
    )
    merged = merged.merge(
        gdf_state[["District", "district", "state"]],
        on="District",
        how="left",
    )

    # ------------------------------------------------------------
    # 11. Compute HWE losses
    # ------------------------------------------------------------
    merged["loss_usd_hwe"] = merged["HWE_weight_norm"] * dlna_total

    merged = merged.fillna(0)

    # For convenience, expose a nice 'District' label column
    merged = merged.rename(columns={"district": "District_label"})

    return merged
