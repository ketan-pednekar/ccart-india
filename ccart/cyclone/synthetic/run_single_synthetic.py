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

def run_single_synthetic(
    run_dir,
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
    save_hazard=True,
    save_track=True,
    save_track_csv=True,
):
    """
    Run a complete CCART synthetic cyclone workflow for a single generated storm.
    """

    # ------------------------------------------------------------
    # FIX: DO NOT create run_dir here — batch runner handles it
    # ------------------------------------------------------------

    # ------------------------------------------------------------
    # Standardize district column name
    # ------------------------------------------------------------
    if "district" in districts_gdf.columns and "District" not in districts_gdf.columns:
        districts_gdf = districts_gdf.rename(columns={"district": "District"})

    # ------------------------------------------------------------
    # 1. Generate synthetic track
    # ------------------------------------------------------------
    track = build_synthetic_cyclone(
        file_path=cleaned_tracks_path,
        coastline_path=coastline_path_for_generator,
        scenario=scenario,
    )

    # Save track only if run_dir exists (valid storm)
    if run_dir and save_track and save_track_csv:
        df_track = track.to_dataframe()
        df_track.to_csv(os.path.join(run_dir, "track.csv"), index=False)

    # ------------------------------------------------------------
    # 2. Build synthetic hazard
    # ------------------------------------------------------------
    tc = TCTracks()
    tc.data = [track]
    hazard = build_hazard_from_tc_tracks(tc)

    peak_kn = float(track["max_sustained_wind"].max())
    if peak_kn < 45:
        return "RETRY"

    peak_intensity = float(hazard.intensity.max())
    if peak_intensity < 30:
        return "RETRY"

    if run_dir and save_hazard:
        hazard.write_hdf5(os.path.join(run_dir, "hazard.hdf5"))

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

    # ------------------------------------------------------------
    # 6. District aggregation
    # ------------------------------------------------------------
    district_loss_raw = aggregate_district_losses(exp_with_loss, districts_gdf)

    raw_total = float(district_loss_raw["loss_usd"].sum())
    if raw_total <= 0:
        return "RETRY"

    # ------------------------------------------------------------
    # 7. DLNA calibration
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
    # 8. HWE computation
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
    # 9. Save outputs (only if run_dir exists)
    # ------------------------------------------------------------
    if run_dir:
        district_loss_raw.to_csv(os.path.join(run_dir, "district_loss_raw.csv"), index=False)
        district_loss_cal.to_csv(os.path.join(run_dir, "district_loss_calibrated.csv"), index=False)
        hwe_metrics.to_csv(os.path.join(run_dir, "district_hwe.csv"), index=False)

    # ------------------------------------------------------------
    # 10. Metadata
    # ------------------------------------------------------------
    metadata = {
        "scenario": scenario,
        "alpha": alpha,
        "b": b,
        "raw_total": float(raw_total),
        "dlna_total": float(dlna_total),
        "n_districts": int(len(district_loss_cal)),
        "timestamp": datetime.now().isoformat(),
        "max_intensity": float(hazard.intensity.max()),
    }

    if run_dir:
        with open(os.path.join(run_dir, "metadata.json"), "w") as f:
            json.dump(metadata, f, indent=4)

    print(
        f"[✓] Synthetic run complete | Scenario={scenario} | "
        f"PeakWind={peak_kn:.1f} kn | DLNA={dlna_total:.2e}"
    )

    return metadata
