"""
CCART v1.0 — Engine Orchestrator (India-ready)
----------------------------------------------

This module ties together all CCART components into a single
end-to-end workflow using a full-India district GeoJSON.

Steps:
1. Load full-India districts
2. Filter to target state
3. Load LitPop exposure
4. Build hazard (IBTrACS → CLIMADA)
5. Compute district-level hazard statistics
6. Compute raw CLIMADA impact
7. Aggregate losses to districts
8. Calibrate to DLNA/PDNA totals
9. Apply Hazard–Exposure Weighting Engine (HWE)
10. Return final district-level GeoDataFrame
"""

import geopandas as gpd

from .hazard import build_hazard, compute_district_hazard_stats
from .exposure import load_litpop_for_state
from .vulnerability import build_vulnerability_curves
from .impact import compute_raw_impact, attach_losses_to_points, aggregate_district_loss
from .calibration import calibrate_to_total
from .hwe import build_hwe_weights


def run_ccart(cyclone_name: str,
              storm_id: str,
              ibtracs_path: str,
              districts_path: str,
              dlna_total: float,
              state_name: str,
              country_code: str = "IND"):
    """
    Run the full CCART v1.0 engine for a single cyclone and state,
    using a full-India district GeoJSON.

    Parameters
    ----------
    cyclone_name : str
        Human-readable cyclone name (e.g., "Fani").
    storm_id : str
        IBTrACS storm identifier.
    ibtracs_path : str
        Path to IBTrACS NetCDF file.
    districts_path : str
        Path to full-India district boundary GeoJSON.
    dlna_total : float
        State-level DLNA/PDNA total loss (USD).
    state_name : str
        Target state name (case-insensitive, e.g., "ODISHA").
    country_code : str
        ISO country code for LitPop (default: "IND").

    Returns
    -------
    GeoDataFrame
        District-level calibrated and HWE losses with geometry.
    """

    # ------------------------------------------------------------
    # 1. Load full-India districts
    # ------------------------------------------------------------
    gdf_all = gpd.read_file(districts_path)

    # Standardize names
    gdf_all["district"] = gdf_all["district"].astype(str).str.strip()
    gdf_all["state"] = gdf_all["state"].astype(str).str.strip()

    # Filter to target state
    mask = gdf_all["state"].str.upper() == state_name.strip().upper()
    gdf_state = gdf_all[mask].copy()

    if len(gdf_state) == 0:
        raise ValueError(f"No districts found for state: {state_name}")

    # Ensure CRS is EPSG:4326
    if gdf_state.crs is None or gdf_state.crs.to_string() != "EPSG:4326":
        gdf_state = gdf_state.to_crs("EPSG:4326")

    # Standardize district column for CCART modules
    gdf_state["District"] = gdf_state["district"].astype(str).str.strip()
    districts = gdf_state[["District", "geometry"]].copy()

    # ------------------------------------------------------------
    # 2. Load LitPop exposure for the state
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
    # 9. Calibration
    # ------------------------------------------------------------
    district_loss_cal = calibrate_to_total(district_loss_raw, dlna_total)

    # ------------------------------------------------------------
    # 10. HWE weights
    # ------------------------------------------------------------
    hwe_weights = build_hwe_weights(hazard_stats, exp_dist)

    # ------------------------------------------------------------
    # 11. Merge calibrated + HWE with geometry
    # ------------------------------------------------------------
    merged = districts.merge(district_loss_cal, on="District", how="left")
    merged = merged.merge(
        hwe_weights[["District", "HWE_weight_norm"]],
        on="District",
        how="left"
    )

    # Add state column back
    merged = merged.merge(
        gdf_state[["District", "state"]],
        on="District",
        how="left"
    )

    # ------------------------------------------------------------
    # 12. Compute HWE losses
    # ------------------------------------------------------------
    merged["loss_usd_hwe"] = merged["HWE_weight_norm"] * dlna_total

    # Fill missing values
    merged = merged.fillna(0)

    return merged