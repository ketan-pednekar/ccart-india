"""
CCART — Synthetic Cyclone End-to-End Driver (v2, final)

Pipeline:
    synthetic track → TCTracks → synthetic hazard (v2)
    → exposure → vulnerability → impact → calibration → HWE
    → district + state outputs

Features:
- clean synthetic generator (ccart.synthetic.generator)
- hazard clipping to footprint bounding box
- inland distance masking
- hazard_mask = (wind >= threshold) & coastal & within inland_clip_km
- calibration only on coastal districts
- HWE using hazard_mask
- district + state maps
- full diagnostics (raw, DLNA, calibrated, HWE)
"""

import os
import json
import geopandas as gpd
import pandas as pd
import numpy as np

from climada.hazard import TCTracks
from climada.entity import Exposures

# --- CCART imports ---
from ccart.synthetic.generator import build_synthetic_cyclone
from ccart.hazard_simulated_v2 import build_hazard_from_tc_tracks
from ccart.hazard import compute_district_hazard_stats
from ccart.exposure import load_litpop_for_state
from ccart.vulnerability import build_vulnerability_curves
from ccart.impact import (
    compute_raw_impact,
    attach_losses_to_points,
    aggregate_district_loss,
)
from ccart.calibration import calibrate_to_total
from ccart.hwe import build_hwe_weights
from ccart.viz.viz_v2 import ccart_choropleth_v2

HAZARD_FLOOR_MS = 10.0
INLAND_CLIP_KM = 150.0


def _normalize_name(s):
    return (
        s.astype(str)
         .str.strip()
         .str.upper()
         .str.replace(r"\s+", " ", regex=True)
    )


def main(
    run_dir_override=None,
    save_hazard=False,
    save_track=False,
    save_hazard_gpkg=False,
    save_track_csv=False
):

    """
    Main synthetic cyclone driver.

    If run_dir_override is provided, all outputs (GPKG + PNGs)
    are written inside that directory using the structure:

        run_dir_override/
            impact.gpkg
            maps/
                district/
                state/
    """

    # ------------------------------------------------------------
    # 0. Paths
    # ------------------------------------------------------------
    base_dir = r"C:\CMIP data\cmip6\Climada\Projects\ccart-india"

    cleaned_tracks_path = os.path.join(
        base_dir,
        r"data\ni_tracks_climada_1950_2023_cleaned.h5",
    )
    districts_path = os.path.join(
        base_dir,
        r"data\INDIA_DISTRICTS.geojson",
    )
    coastline_path = os.path.join(
        base_dir,
        r"data\coastl_ind.shp",
    )

    country_code = "IND"

    # If batch mode: prepare subfolders
    maps_district_dir = None
    maps_state_dir = None
    if run_dir_override is not None:
        maps_district_dir = os.path.join(run_dir_override, "maps", "district")
        maps_state_dir = os.path.join(run_dir_override, "maps", "state")
        os.makedirs(maps_district_dir, exist_ok=True)
        os.makedirs(maps_state_dir, exist_ok=True)

    # ------------------------------------------------------------
    # 1. Synthetic track (regenerate until damaging)
    # ------------------------------------------------------------
    print("\n=== STEP 1: Building synthetic cyclone track ===")

    MAX_ATTEMPTS = 10
    hazard = None
    syn_track = None

    for attempt in range(1, MAX_ATTEMPTS + 1):
        print(f"\nAttempt {attempt}/{MAX_ATTEMPTS}...")

        syn_track = build_synthetic_cyclone(
            file_path=cleaned_tracks_path,
            min_wind=35,
            cluster_eps=12.0,
            cluster_min_samples=2,
            top_n=5,
            wind_boost=1.00,
        )

        print("\n--- SYNTHETIC TRACK STRUCTURE ---")
        print(syn_track)
        print(syn_track.data_vars)
        print("-------------------------------")

        # Quick wind check
        peak_kn = float(syn_track["max_sustained_wind"].max())
        print("  Peak wind (kn):", peak_kn)

        if peak_kn < 45:
            print("  ❌ Too weak — regenerating.")
            continue

        # Build hazard to check intensity
        tc_tracks = TCTracks()
        tc_tracks.data = [syn_track]
        hazard_tmp = build_hazard_from_tc_tracks(tc_tracks)

        peak_intensity = float(hazard_tmp.intensity.max())
        print("  Peak hazard intensity (m/s):", peak_intensity)

        if peak_intensity < 30:
            print("  ❌ Hazard too weak — regenerating.")
            continue

        print("  ✅ Storm accepted.")
        hazard = hazard_tmp

        # ------------------------------------------------------------
        # SAVE TRACK CSV (if requested)
        # ------------------------------------------------------------
        if save_track_csv and run_dir_override is not None:
            df_track = syn_track.to_dataframe()
            df_track.to_csv(
                os.path.join(run_dir_override, "track.csv"),
                index=False
            )
            print(f"   → Saved track.csv to {run_dir_override}")

        break  # IMPORTANT: break AFTER saving track

    else:
        raise RuntimeError("Failed to generate a damaging synthetic cyclone after multiple attempts.")

    print("✅ Synthetic track built.")
    print("   SID :", syn_track.attrs.get("sid", "N/A"))
    print("   Name:", syn_track.attrs.get("name", "N/A"))

    # hazard is already built — do NOT rebuild it again
    tc_tracks = TCTracks()
    tc_tracks.data = [syn_track]

    # ------------------------------------------------------------
    # 2. Load districts
    # ------------------------------------------------------------
    print("\n=== STEP 2: Loading districts ===")
    gdf_all = gpd.read_file(districts_path)

    gdf_all["district_norm"] = _normalize_name(gdf_all["district"])
    gdf_all["state_norm"] = _normalize_name(gdf_all["state"])
    gdf_all["District"] = gdf_all["district_norm"]

    if gdf_all.crs is None or gdf_all.crs.to_string() != "EPSG:4326":
        gdf_all = gdf_all.to_crs("EPSG:4326")

    districts = gdf_all[["District", "geometry"]].copy()

    # ------------------------------------------------------------
    # 3. Inland distance mask
    # ------------------------------------------------------------
    print("\n=== STEP 3: Computing distance to coast ===")
    coast = gpd.read_file(coastline_path)
    if coast.crs is None or coast.crs.to_string() != "EPSG:4326":
        coast = coast.to_crs("EPSG:4326")

    districts_proj = districts.to_crs("EPSG:3857")
    coast_proj = coast.to_crs("EPSG:3857")

    centroids_proj = districts_proj.geometry.centroid
    dist_to_coast_m = centroids_proj.distance(coast_proj.unary_union)

    districts["dist_to_coast_km"] = dist_to_coast_m / 1000.0
    districts["is_inland"] = districts["dist_to_coast_km"] > INLAND_CLIP_KM

    print("Example distances (km):")
    print(districts[["District", "dist_to_coast_km", "is_inland"]].head())

    # ------------------------------------------------------------
    # 4. Load exposure
    # ------------------------------------------------------------
    print("\n=== STEP 4: Loading LitPop exposure ===")
    assets_all, exp_dist = load_litpop_for_state(country_code, districts)
    assets_all = Exposures(assets_all)
    print(f"Exposure points (all India): {len(assets_all.gdf)}")

    # ------------------------------------------------------------
    # 5. Build hazard
    # ------------------------------------------------------------
    print("\n=== STEP 5: Building synthetic hazard (v2) ===")
    hazard = build_hazard_from_tc_tracks(tc_tracks)
    print("✅ Synthetic hazard built.")
    print("   Events   :", hazard.event_id.size)
    print("   Centroids:", hazard.centroids.size)
    print("   Max intensity:", float(hazard.intensity.max()))

    if save_hazard_gpkg and run_dir_override is not None:
        
        df = pd.DataFrame({
            "lat": hazard.centroids.lat,
            "lon": hazard.centroids.lon,
            "intensity": hazard.intensity.toarray().ravel()
        })

        gdf = gpd.GeoDataFrame(
            df,
            geometry=gpd.points_from_xy(df.lon, df.lat),
            crs="EPSG:4326"
        )

        out_path = os.path.join(run_dir_override, "hazard.gpkg")
        gdf.to_file(out_path, driver="GPKG")
        print(f"   → Saved hazard.gpkg to {out_path}")


    # ------------------------------------------------------------
    # 6. Clip exposure to hazard bounding box
    # ------------------------------------------------------------
    print("\n=== STEP 6: Exposure–hazard clipping ===")
    haz_lat_min = float(hazard.centroids.lat.min())
    haz_lat_max = float(hazard.centroids.lat.max())
    haz_lon_min = float(hazard.centroids.lon.min())
    haz_lon_max = float(hazard.centroids.lon.max())

    before = len(assets_all.gdf)
    clipped = assets_all.gdf[
        (assets_all.gdf.geometry.y >= haz_lat_min) &
        (assets_all.gdf.geometry.y <= haz_lat_max) &
        (assets_all.gdf.geometry.x >= haz_lon_min) &
        (assets_all.gdf.geometry.x <= haz_lon_max)
    ].copy()

    assets_all = Exposures(clipped)

    print("\n=== DEBUG: Exposure columns ===")
    print(assets_all.gdf.columns.tolist())

    if "impf_TC" in assets_all.gdf:
        print("Unique impf_TC:", assets_all.gdf["impf_TC"].unique())
    else:
        print("impf_TC column is MISSING")

    print(f"Exposure points before: {before}")
    print(f"Exposure points after : {len(clipped)}")

    print("\n=== DEBUG: Exposure vs Hazard centroid count ===")
    print("Exposure points:", len(assets_all.gdf))
    print("Hazard centroids:", hazard.centroids.size)


    # ------------------------------------------------------------
    # 7. District hazard stats + hazard_mask (with inland fix)
    # ------------------------------------------------------------
    print("\n=== STEP 7: Computing district hazard stats ===")
    hazard_stats = compute_district_hazard_stats(hazard, districts)

    # Merge inland distance into hazard_stats by District (CRITICAL FIX)
    hazard_stats = hazard_stats.merge(
        districts[["District", "dist_to_coast_km", "is_inland"]],
        on="District",
        how="left",
    )

    # ------------------------------------------------------------
    # DEBUG: Inspect hazard stats before applying hazard_mask
    # ------------------------------------------------------------
    print("\n=== DEBUG: District wind + distance summary ===")
    print(
        hazard_stats[["District", "WindSpeed_Max_mps",
                    "dist_to_coast_km", "is_inland"]]
        .sort_values("WindSpeed_Max_mps", ascending=False)
        .head(20)
    )

    print("\n=== DEBUG: WindSpeed_Max_mps distribution ===")
    print(hazard_stats["WindSpeed_Max_mps"].describe())

    hazard_stats["hazard_mask"] = (
        (hazard_stats["WindSpeed_Max_mps"] >= HAZARD_FLOOR_MS)
        & (hazard_stats["is_inland"] == False)
        & (hazard_stats["dist_to_coast_km"] <= INLAND_CLIP_KM)
    )

    print("Districts with hazard_mask = True:",
          int(hazard_stats["hazard_mask"].sum()))

    # ------------------------------------------------------------
    # 8. Vulnerability
    # ------------------------------------------------------------
    print("\n=== STEP 8: Building vulnerability curves ===")
    impf_set = build_vulnerability_curves()
    print("✅ Vulnerability curves ready.")

    # ------------------------------------------------------------
    # 9. Raw impact
    # ------------------------------------------------------------
    print("\n=== STEP 9: Computing raw impact ===")
    impact_raw = compute_raw_impact(assets_all, impf_set, hazard)
    exp_with_loss = attach_losses_to_points(assets_all, impact_raw)

    raw_loss_total = float(impact_raw.at_event.sum())
    print("\n=== RAW IMPACT DIAGNOSTICS ===")
    print(f"Raw loss total (USD): {raw_loss_total:,.2f}")
    print("==============================")

    # ------------------------------------------------------------
    # 10. Aggregate to districts
    # ------------------------------------------------------------
    print("\n=== STEP 10: Aggregating to districts ===")
    district_loss_raw = aggregate_district_loss(exp_with_loss, districts)
    print("District-level rows:", len(district_loss_raw))

    raw_district_total = district_loss_raw["loss_usd"].sum()
    print(f"Raw district loss total (USD): {raw_district_total:,.2f}")

    # ------------------------------------------------------------
    # 11. DLNA total
    # ------------------------------------------------------------
    print("\n=== STEP 11: Computing synthetic DLNA total ===")
    alpha = 1.7392153456669906e8
    b = 0.10201685392633236
    dlna_total = alpha * (raw_district_total ** b)
    print(f"Synthetic DLNA_total = {dlna_total:,.0f} USD")

    # ------------------------------------------------------------
    # 12. Calibration (coastal only via hazard_mask)
    # ------------------------------------------------------------
    print("\n=== STEP 12: Calibration ===")

    # Attach hazard_mask to district raw losses
    loss_with_flag = district_loss_raw.merge(
        hazard_stats[["District", "hazard_mask"]],
        on="District",
        how="left",
    )

    coastal = loss_with_flag[loss_with_flag["hazard_mask"] == True].copy()
    inland = loss_with_flag[loss_with_flag["hazard_mask"] == False].copy()

    print("Coastal districts in calibration:", len(coastal))
    print("Inland districts (zeroed)       :", len(inland))

    # Skip calibration if meaningless
    if len(coastal) == 0 or dlna_total == 0 or raw_district_total == 0:
        print("\n*** Calibration skipped: no meaningful coastal impact. Regenerating. ***")
        return "RETRY"

    # 1) rename raw loss for clarity
    coastal = coastal.rename(columns={"loss_usd": "loss_usd_raw"})

    # 2) run calibration
    coastal_cal = calibrate_to_total(
        coastal,
        dlna_total,
        loss_col="loss_usd_raw",
    )

    # 3) rename calibrated column
    coastal_cal = coastal_cal.rename(
        columns={"loss_usd_calibrated": "loss_usd_cal"}
    )

    # 4) inland: keep raw, calibrated = 0
    inland_cal = inland.rename(columns={"loss_usd": "loss_usd_raw"})
    inland_cal["loss_usd_cal"] = 0.0
    inland_cal["calibration_factor"] = 0.0

    # 5) combine
    district_loss_cal = pd.concat(
        [coastal_cal, inland_cal],
        ignore_index=True,
    )

    # ------------------------------------------------------------
    # 13. HWE
    # ------------------------------------------------------------
    print("\n=== STEP 13: Building HWE weights ===")

    hwe_weights = build_hwe_weights(hazard_stats, exp_dist)

    # Attach hazard_mask
    hwe_weights = hwe_weights.merge(
        hazard_stats[["District", "hazard_mask"]],
        on="District",
        how="left",
    )

    # Zero out inland districts
    hwe_weights.loc[hwe_weights["hazard_mask"] == False, "HWE_weight_norm"] = 0.0

    # Normalize weights
    total_w = hwe_weights["HWE_weight_norm"].sum()
    if total_w > 0:
        hwe_weights["HWE_weight_norm"] /= total_w

    # ------------------------------------------------------------
    # 14. Final merge (district-level)
    # ------------------------------------------------------------
    print("\n=== STEP 14: Final merge (district-level) ===")

    merged = districts.merge(district_loss_cal, on="District", how="left")
    merged = merged.merge(
        hwe_weights[["District", "HWE_weight_norm"]],
        on="District",
        how="left",
    )
    # Attach state and a clean district label (optional)
    merged = merged.merge(
        gdf_all[["District", "district_norm", "state"]],
        on="District",
        how="left",
    )

    merged = merged.rename(columns={"district_norm": "District_label"})

    # Compute HWE loss
    merged["loss_usd_hwe"] = merged["HWE_weight_norm"] * dlna_total
    merged = merged.fillna(0)

    # ------------------------------------------------------------
    # 15. State-level aggregation
    # ------------------------------------------------------------
    print("\n=== STEP 15: Aggregating to states ===")

    state_loss = (
        merged.groupby("state", as_index=False)
            .agg({
                "loss_usd_cal": "sum",
                "loss_usd_hwe": "sum",
            })
    )

    print("\nTop states by HWE loss:")
    print(state_loss.head(10))

    # ------------------------------------------------------------
    # 16. Diagnostics summary
    # ------------------------------------------------------------
    print("\n=== SYNTHETIC CYCLONE IMPACT SUMMARY ===")
    print(f"  Raw loss total        : {raw_district_total:,.0f} USD")
    print(f"  Synthetic DLNA target : {dlna_total:,.0f} USD")
    print(f"  Calibrated total loss : {district_loss_cal['loss_usd_cal'].sum():,.0f} USD")
    print(f"  HWE total loss        : {merged['loss_usd_hwe'].sum():,.0f} USD")
    print(f"  Districts with loss   : {(merged['loss_usd_cal'] > 0).sum()}")
    print(f"  States with loss      : {(state_loss['loss_usd_hwe'] > 0).sum()}")

    # ------------------------------------------------------------
    # 16.1 Detailed loss diagnostics (raw, calibrated, HWE)
    # ------------------------------------------------------------
    print("\n=== DETAILED LOSS DIAGNOSTICS ===")

    loss_table = merged[[
        "District",
        "state",
        "loss_usd_raw",
        "loss_usd_cal",
        "loss_usd_hwe"
    ]].copy()

    print("\nTop 10 districts by RAW loss:")
    print(loss_table.sort_values("loss_usd_raw", ascending=False).head(10))

    print("\nTop 10 districts by CALIBRATED loss:")
    print(loss_table.sort_values("loss_usd_cal", ascending=False).head(10))

    print("\nTop 10 districts by HWE loss:")
    print(loss_table.sort_values("loss_usd_hwe", ascending=False).head(10))

    print("\nTotal RAW loss       :", f"{loss_table['loss_usd_raw'].sum():,.0f} USD")
    print("Total CALIBRATED loss:", f"{loss_table['loss_usd_cal'].sum():,.0f} USD")
    print("Total HWE loss       :", f"{loss_table['loss_usd_hwe'].sum():,.0f} USD")

    # ------------------------------------------------------------
    # 17. Save district-level GPKG
    # ------------------------------------------------------------
    print("\n=== STEP 17: Saving GPKG ===")

    merged = gpd.GeoDataFrame(merged, geometry="geometry", crs="EPSG:4326")

    if run_dir_override is None:
        out_path = os.path.join(base_dir, "outputs", "synthetic_cyclone_impact.gpkg")
    else:
        out_path = os.path.join(run_dir_override, "impact.gpkg")

    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    merged.to_file(out_path, driver="GPKG")
    print(f"✅ Saved district-level impact to:\n   {out_path}")

    # ------------------------------------------------------------
    # 18. Build district-based state loss table
    # ------------------------------------------------------------
    print("\n=== STEP 18: Building district-based state loss table ===")

    gdf_all["state"] = gdf_all["state"].astype(str)
    gdf_all["state_norm"] = gdf_all["state_norm"].astype(str)
    state_loss["state"] = state_loss["state"].astype(str)

    districts_with_state_loss = gdf_all.merge(
        state_loss,
        left_on="state_norm",
        right_on="state",
        how="left"
    ).fillna(0)

    districts_with_state_loss = districts_with_state_loss.drop(columns=["state_y"])
    districts_with_state_loss = districts_with_state_loss.rename(columns={"state_x": "state"})

    # ------------------------------------------------------------
    # 19. District-level choropleths (v1.3-style, per affected state)
    # ------------------------------------------------------------
    print("\n=== STEP 19: District-level choropleths (v1.3-style) ===")

    # Identify affected states
    affected_states = (
        state_loss.loc[state_loss["loss_usd_hwe"] > 0, "state"]
        .dropna()
        .unique()
        .tolist()
    )

    print("Affected states:", affected_states)

    for st in affected_states:
        print(f"  → Plotting district map for {st}")

        # Slice district-level GeoDataFrame for this state
        gdf_state = merged[merged["state"] == st].copy()

        # Loss table for this state
        df_loss_state = gdf_state[["District", "loss_usd_hwe"]].copy()

        # Output filename (district-level map)
        if run_dir_override is None:
            out_file = os.path.join(
                base_dir,
                "outputs",
                f"synthetic_cyclone_district_{st.replace(' ', '_').lower()}.png",
            )
        else:
            out_file = os.path.join(
                maps_district_dir,
                f"synthetic_cyclone_district_{st.replace(' ', '_').lower()}.png",
            )

        # Plot district-level map (v1.3 behaviour)
        ccart_choropleth_v2(
            gdf_districts=gdf_state,
            df_losses=df_loss_state,
            district_col="District",
            loss_col="loss_usd_hwe",
            title=f"Synthetic Cyclone Impact – {st} (HWE, district-level)",
            save_path=out_file,
        )

        # --------------------------------------------------------
        # 19A. "State-level" view with district shading (ST2)
        #      (same geometry, different title / future-ready)
        # --------------------------------------------------------
        if run_dir_override is None:
            out_file_state = os.path.join(
                base_dir,
                "outputs",
                f"synthetic_cyclone_state_{st.replace(' ', '_').lower()}.png",
            )
        else:
            out_file_state = os.path.join(
                maps_state_dir,
                f"synthetic_cyclone_state_{st.replace(' ', '_').lower()}.png",
            )

        ccart_choropleth_v2(
            gdf_districts=gdf_state,
            df_losses=df_loss_state,
            district_col="District",
            loss_col="loss_usd_hwe",
            title=f"Synthetic Cyclone Impact – {st} (HWE, state view with districts)",
            save_path=out_file_state,
        )

    # ------------------------------------------------------------
    # Build metadata for batch harness
    # ------------------------------------------------------------
    metadata = {
        "sid": syn_track.attrs.get("sid", "N/A"),
        "storm_name": syn_track.attrs.get("name", "N/A"),
        "raw_loss_total": raw_district_total,
        "dlna_total": dlna_total,
        "calibrated_total": float(district_loss_cal["loss_usd_cal"].sum()),
        "hwe_total": float(merged["loss_usd_hwe"].sum()),
        "n_districts_loss": int((merged["loss_usd_cal"] > 0).sum()),
        "n_states_loss": int((state_loss["loss_usd_hwe"] > 0).sum()),
        "max_intensity": float(hazard.intensity.max()),

        # NEW - jitter metadata
        "genesis_jitter_deg": syn_track.attrs.get("genesis_jitter_deg", 0.0),
        "genesis_lat_original": syn_track.attrs.get("genesis_lat_original", None),
        "genesis_lon_original": syn_track.attrs.get("genesis_lon_original", None),
        "genesis_lat_jittered": syn_track.attrs.get("genesis_lat_jittered", None),
        "genesis_lon_jittered": syn_track.attrs.get("genesis_lon_jittered", None),

        "track_sigma_deg": syn_track.attrs.get("track_sigma_deg", None),
        "track_curvature_index": syn_track.attrs.get("track_curvature_index", None),

        "intensity_peak_scale": syn_track.attrs.get("intensity_peak_scale", None),
        "intensity_decay_scale": syn_track.attrs.get("intensity_decay_scale", None),
        "intensity_timing_shift": syn_track.attrs.get("intensity_timing_shift", None),

        "scenario": syn_track.attrs.get("scenario", "baseline"),
        "scenario_peak_scale": syn_track.attrs.get("scenario_peak_scale", None),
        "scenario_decay_scale": syn_track.attrs.get("scenario_decay_scale", None),
        "scenario_track_sigma": syn_track.attrs.get("scenario_track_sigma", None),

        "rmw_scale": syn_track.attrs.get("rmw_scale", None),
        "translation_speed_scale": syn_track.attrs.get("translation_speed_scale", None),
        "rainfall_scale": syn_track.attrs.get("rainfall_scale", None),

    }

    return merged, state_loss, metadata


def run_single_synthetic(
    run_dir,
    save_hazard=False,
    save_track=False,
    save_hazard_gpkg=False,
    save_track_csv=False
):

    """
    Wrapper that runs ONE synthetic cyclone and returns summary metrics.
    Saves maps + GPKG inside run_dir using the structure:

        run_dir/
            impact.gpkg
            metadata.json
            maps/
                district/
                state/
    """

    result = main(
        run_dir_override=run_dir,
        save_hazard=save_hazard,
        save_track=save_track,
        save_hazard_gpkg=save_hazard_gpkg,
        save_track_csv=save_track_csv
    )


    # If main() signals a retry, run again
    if result == "RETRY":
        return "RETRY"

    merged, state_loss, metadata = result


    summary = {
        "sid": metadata["sid"],
        "storm_name": metadata["storm_name"],
        "raw_loss_total": metadata["raw_loss_total"],
        "dlna_total": metadata["dlna_total"],
        "calibrated_total": metadata["calibrated_total"],
        "hwe_total": metadata["hwe_total"],
        "n_districts_loss": metadata["n_districts_loss"],
        "n_states_loss": metadata["n_states_loss"],
        "max_intensity": metadata["max_intensity"],
        "output_dir": run_dir,
        "genesis_jitter_deg": metadata["genesis_jitter_deg"],
        "genesis_lat_original": metadata["genesis_lat_original"],
        "genesis_lon_original": metadata["genesis_lon_original"],
        "genesis_lat_jittered": metadata["genesis_lat_jittered"],
        "genesis_lon_jittered": metadata["genesis_lon_jittered"],

        "track_sigma_deg": metadata["track_sigma_deg"],
        "track_curvature_index": metadata["track_curvature_index"],

        "intensity_peak_scale": metadata["intensity_peak_scale"],
        "intensity_decay_scale": metadata["intensity_decay_scale"],
        "intensity_timing_shift": metadata["intensity_timing_shift"],
        
        "scenario": metadata["scenario"],
        "scenario_peak_scale": metadata["scenario_peak_scale"],
        "scenario_decay_scale": metadata["scenario_decay_scale"],
        "scenario_track_sigma": metadata["scenario_track_sigma"],

        "rmw_scale": metadata["rmw_scale"],
        "translation_speed_scale": metadata["translation_speed_scale"],
        "rainfall_scale": metadata["rainfall_scale"],
    }

    meta_path = os.path.join(run_dir, "metadata.json")
    os.makedirs(os.path.dirname(meta_path), exist_ok=True)
    with open(meta_path, "w") as f:
        json.dump(summary, f, indent=2)

    return summary


if __name__ == "__main__":
    main()



