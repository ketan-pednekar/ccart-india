"""
synthetic_core.py
-----------------
Core logic for CCART synthetic cyclone runs.

- simulate_storm(): runs the entire pipeline in memory, no file writes.
- write_outputs(): writes all outputs only after storm is validated.

This prevents partial folders (track only, track+hazard only).
"""

import os
import json
from datetime import datetime

from climada.hazard import TCTracks
from ccart.cyclone.synthetic.hazard_from_tracks import build_hazard_from_tc_tracks

from ccart.cyclone.synthetic.synthetic_generator import build_synthetic_cyclone
from ccart.cyclone.synthetic.synthetic_exposure import (
    compute_distance_to_coast,
    clip_exposure_to_hazard,
)
from ccart.cyclone.synthetic.synthetic_impact import (
    compute_hazard_stats,
    merge_inland_mask,
    compute_raw_impact_pipeline,
    aggregate_district_losses,
)
from ccart.cyclone.synthetic.synthetic_calibration import (
    compute_dlna_total,
    split_coastal_inland,
    calibrate_coastal_losses,
    zero_inland_losses,
    combine_calibrated_losses,
)
from ccart.cyclone.synthetic.synthetic_hwe import (
    prepare_hwe_inputs,
    compute_hwe_metrics,
    attach_hwe_to_districts,
)


# ============================================================
# 1. SIMULATE STORM (NO FILE WRITING)
# ============================================================
def simulate_storm(
    exposures,
    districts_gdf,
    coastline_gdf,
    wealth_df,
    impf_set,
    cleaned_tracks_path,
    coastline_path_for_generator,
    scenario="baseline",
    alpha=0.9,
    b=0.85,
    inland_clip_km=100,
):
    """
    Run the entire synthetic cyclone pipeline in memory.
    Returns:
        - "RETRY" if storm is invalid
        - dict with all results if valid
    """

    # ------------------------------------------------------------
    # 1. Generate synthetic track
    # ------------------------------------------------------------
    track = build_synthetic_cyclone(
        file_path=cleaned_tracks_path,
        coastline_path=coastline_path_for_generator,
        scenario=scenario,
    )

    peak_kn = float(track["max_sustained_wind"].max())
    if peak_kn < 45:
        return "RETRY"

    # ------------------------------------------------------------
    # 2. Build hazard
    # ------------------------------------------------------------
    tc = TCTracks()
    tc.data = [track]

    try:
        hazard = build_hazard_from_tc_tracks(tc)
    except Exception:
        return "RETRY"

    peak_intensity = float(hazard.intensity.max())
    if peak_intensity < 30:
        return "RETRY"

    # ------------------------------------------------------------
    # 3. Clip exposure
    # ------------------------------------------------------------
    exposure_clipped = clip_exposure_to_hazard(exposures, hazard)

    # ------------------------------------------------------------
    # 4. Hazard stats + inland mask
    # ------------------------------------------------------------
    districts_gdf = compute_distance_to_coast(
        districts_gdf,
        coastline_gdf,
        inland_clip_km,
    )

    if "district" in districts_gdf.columns and "District" not in districts_gdf.columns:
        districts_gdf = districts_gdf.rename(columns={"district": "District"})

    districts_gdf = (
        districts_gdf
        .dissolve(by="District", as_index=False)
        .reset_index(drop=True)
    )

    hazard_stats = compute_hazard_stats(hazard, districts_gdf)
    hazard_stats = merge_inland_mask(hazard_stats, districts_gdf)

    hazard_stats["hazard_mask"] = (
        (hazard_stats["max_intensity"] >= 10.0)
        & (hazard_stats["is_inland"] == False)
        & (hazard_stats["dist_to_coast_km"] <= inland_clip_km)
    )

    hazard_stats = (
        hazard_stats.groupby("District", as_index=False)
        .agg({
            "max_intensity": "max",
            "dist_to_coast_km": "first",
            "is_inland": "first",
            "hazard_mask": "max",
        })
    )

    # ------------------------------------------------------------
    # 5. Raw impact
    # ------------------------------------------------------------
    exp_with_loss, impact_raw = compute_raw_impact_pipeline(
        exposure_clipped,
        impf_set,
        hazard,
    )

    district_loss_raw = aggregate_district_losses(exp_with_loss, districts_gdf)
    raw_total = float(district_loss_raw["loss_usd"].sum())
    if raw_total <= 0:
        return "RETRY"

    # ------------------------------------------------------------
    # 6. DLNA calibration
    # ------------------------------------------------------------
    dlna_total = compute_dlna_total(raw_total, alpha, b)
    if dlna_total <= 0:
        return "RETRY"

    coastal_df, inland_df = split_coastal_inland(district_loss_raw, hazard_stats)
    if len(coastal_df) == 0:
        return "RETRY"

    coastal_cal = calibrate_coastal_losses(coastal_df, dlna_total)
    inland_cal = zero_inland_losses(inland_df)
    district_loss_cal = combine_calibrated_losses(coastal_cal, inland_cal)

    # ------------------------------------------------------------
    # 7. HWE computation
    # ------------------------------------------------------------
    if "Wealth" in wealth_df.columns and "wealth_usd" not in wealth_df.columns:
        wealth_df = wealth_df.rename(columns={"Wealth": "wealth_usd"})

    hwe_input = prepare_hwe_inputs(district_loss_cal, wealth_df)
    hwe_metrics = compute_hwe_metrics(hwe_input)

    districts_gdf = districts_gdf[[
        "District",
        "geometry",
        "dist_to_coast_km",
        "is_inland"
    ]].copy()

    districts_hwe = attach_hwe_to_districts(hwe_metrics, districts_gdf)

    # ------------------------------------------------------------
    # Return everything for writing
    # ------------------------------------------------------------
    return {
        "track": track,
        "hazard": hazard,
        "district_loss_raw": district_loss_raw,
        "district_loss_cal": district_loss_cal,
        "district_hwe": hwe_metrics,
        "metadata": {
            "scenario": scenario,
            "alpha": alpha,
            "b": b,
            "raw_total": raw_total,
            "dlna_total": dlna_total,
            "n_districts": int(len(district_loss_cal)),
            "timestamp": datetime.now().isoformat(),
            "max_intensity": peak_intensity,
        },
    }


# ============================================================
# 2. WRITE OUTPUTS (ONLY AFTER VALIDATION)
# ============================================================
def write_outputs(run_dir, results):
    """
    Writes all outputs for a validated storm.
    """

    os.makedirs(run_dir, exist_ok=True)

    # Track
    df_track = results["track"].to_dataframe()
    df_track.to_csv(os.path.join(run_dir, "track.csv"), index=False)

    # Hazard
    results["hazard"].write_hdf5(os.path.join(run_dir, "hazard.hdf5"))

    # District losses
    results["district_loss_raw"].to_csv(
        os.path.join(run_dir, "district_loss_raw.csv"), index=False
    )
    results["district_loss_cal"].to_csv(
        os.path.join(run_dir, "district_loss_calibrated.csv"), index=False
    )
    results["district_hwe"].to_csv(
        os.path.join(run_dir, "district_hwe.csv"), index=False
    )

    # Metadata
    with open(os.path.join(run_dir, "metadata.json"), "w") as f:
        json.dump(results["metadata"], f, indent=4)
