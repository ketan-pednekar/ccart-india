"""
CCART — Synthetic Cyclone End-to-End Driver (v2 draft)

Runs:
    synthetic track -> TCTracks -> synthetic hazard (v2)
    -> exposure -> vulnerability -> impact -> calibration -> HWE
    -> district-level outputs

This is a *test driver* for the synthetic engine.
"""

import geopandas as gpd
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os
import sys

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(PROJECT_ROOT)


from ccart.viz.viz_v2 import ccart_choropleth_v2

from climada.hazard import TCTracks

# --- CCART engine imports (v1.3 + v2 synthetic) ---
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

# --- Synthetic track generator ---
from ccart.synthetic.build_synthetic_cyclone_cleaned import build_synthetic_cyclone_from_clean_file



HAZARD_FLOOR_MS = 12.0


def _normalize_name(s):
    return (
        s.astype(str)
         .str.strip()
         .str.upper()
         .str.replace(r"\s+", " ", regex=True)
    )


def main():
    # ------------------------------------------------------------
    # 0. User-configurable paths / parameters
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

    inland_clip_km = 300.0
    country_code = "IND"

    # ------------------------------------------------------------
    # 1. Generate one synthetic cyclone (track)
    # ------------------------------------------------------------
    print("\n=== STEP 1: Building synthetic cyclone track ===")
    syn_track = build_synthetic_cyclone_from_clean_file(
        file_path=cleaned_tracks_path,
        min_wind=35,
        cluster_eps=8.0,
        cluster_min_samples=3,
        target_cluster=None,
        top_n=5,
        wind_boost=1.00,
    )
    print("✅ Synthetic track built.")
    print("   SID:", syn_track.attrs.get("sid", "N/A"))
    print("   Name:", syn_track.attrs.get("name", "N/A"))

    # Wrap into TCTracks
    tc_tracks = TCTracks()
    tc_tracks.data = [syn_track]
    print("✅ Wrapped into TCTracks (size = 1).")

    # ------------------------------------------------------------
    # 2. Load ALL India districts
    # ------------------------------------------------------------
    print("\n=== STEP 2: Loading districts ===")
    gdf_all = gpd.read_file(districts_path)

    if "district" not in gdf_all.columns or "state" not in gdf_all.columns:
        raise KeyError(
            "Expected columns 'district' and 'state' in districts file, "
            f"found: {list(gdf_all.columns)}"
        )

    gdf_all["district"] = gdf_all["district"].astype(str)
    gdf_all["state"] = gdf_all["state"].astype(str)

    gdf_all["district_norm"] = _normalize_name(gdf_all["district"])
    gdf_all["state_norm"] = _normalize_name(gdf_all["state"])

    gdf_all["District"] = gdf_all["district_norm"]

    if gdf_all.crs is None or gdf_all.crs.to_string() != "EPSG:4326":
        gdf_all = gdf_all.to_crs("EPSG:4326")

    districts = gdf_all[["District", "geometry"]].copy()

    # ------------------------------------------------------------
    # 3. Optional inland distance clipping
    # ------------------------------------------------------------
    print("\n=== STEP 3: Computing distance to coast (optional) ===")
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
    # 4. Load ALL India LitPop exposure
    # ------------------------------------------------------------
    print("\n=== STEP 4: Loading LitPop exposure ===")
    assets_all, exp_dist = load_litpop_for_state(country_code, districts)

    # Convert GeoDataFrame → CLIMADA Exposures
    from climada.entity import Exposures
    assets_all = Exposures(assets_all)

    print(f"Loaded exposure points: {len(assets_all.gdf)}")
    print(type(assets_all))

    # ------------------------------------------------------------
    # 5. Build synthetic hazard (v2)
    # ------------------------------------------------------------
    print("\n=== STEP 5: Building synthetic hazard (v2) ===")
    hazard = build_hazard_from_tc_tracks(tc_tracks)
    print("✅ Synthetic hazard built.")
    print("   Events:", hazard.event_id.size)
    print("   Centroids:", hazard.centroids.size)

    print("Max intensity in hazard (all events, all centroids):",
      float(hazard.intensity.max()))

    # ------------------------------------------------------------
    # CLIP EXPOSURE TO HAZARD BOUNDING BOX (CRITICAL FIX)
    # ------------------------------------------------------------
    print("\n=== EXPOSURE–HAZARD CLIPPING ===")

    haz_lat_min = hazard.centroids.lat.min()
    haz_lat_max = hazard.centroids.lat.max()
    haz_lon_min = hazard.centroids.lon.min()
    haz_lon_max = hazard.centroids.lon.max()

    print(f"Hazard lat range: {haz_lat_min:.2f} → {haz_lat_max:.2f}")
    print(f"Hazard lon range: {haz_lon_min:.2f} → {haz_lon_max:.2f}")

    before = len(assets_all.gdf)

    # Clip the GeoDataFrame
    clipped_gdf = assets_all.gdf[
        (assets_all.gdf.geometry.y >= haz_lat_min) &
        (assets_all.gdf.geometry.y <= haz_lat_max) &
        (assets_all.gdf.geometry.x >= haz_lon_min) &
        (assets_all.gdf.geometry.x <= haz_lon_max)
    ].copy()

    after = len(clipped_gdf)

    # Rebuild Exposures object
    assets_all = Exposures(clipped_gdf)

    print(f"Exposure points before clipping: {before}")
    print(f"Exposure points after clipping:  {after}")
    print(f"Removed {before - after} points outside hazard domain.")
    print("============================================\n")


    # ------------------------------------------------------------
    # 6. District-level hazard statistics
    # ------------------------------------------------------------
    print("\n=== STEP 6: Computing district hazard stats ===")
    hazard_stats = compute_district_hazard_stats(hazard, districts)

    if "WindSpeed_Max_mps" not in hazard_stats.columns:
        raise KeyError(
            "WindSpeed_Max_mps not found in hazard_stats. "
            "Check compute_district_hazard_stats output."
        )

    hazard_stats["hazard_ok"] = hazard_stats["WindSpeed_Max_mps"] >= HAZARD_FLOOR_MS

    if inland_clipping_active:
        hazard_stats = hazard_stats.merge(
            districts[["District", "dist_to_coast_km", "is_inland"]],
            on="District",
            how="left",
        )
    else:
        hazard_stats["dist_to_coast_km"] = None
        hazard_stats["is_inland"] = False

    HAZARD_COAST_KM = inland_clip_km

    hazard_stats["hazard_mask"] = (
        (hazard_stats["WindSpeed_Max_mps"] >= HAZARD_FLOOR_MS)
        & (hazard_stats["is_inland"] == False)
        & (
            (hazard_stats["dist_to_coast_km"].isna())
            | (hazard_stats["dist_to_coast_km"] <= HAZARD_COAST_KM)
        )
    )

    print("✅ Hazard stats computed for", len(hazard_stats), "districts.")

    print("Exposure CRS:", assets_all.gdf.crs)
    print("Hazard CRS:", hazard.centroids.gdf.crs)

    print("\nExposure columns:", assets_all.gdf.columns.tolist())
    print("\nExposure head:")
    print(assets_all.gdf.head())

    print("\nHazard centroid columns:", hazard.centroids.gdf.columns.tolist())
    print("\nHazard centroid head:")
    print(hazard.centroids.gdf.head())


    # ------------------------------------------------------------
    # 7. Vulnerability curves
    # ------------------------------------------------------------
    print("\n=== STEP 7: Building vulnerability curves ===")
    impf_set = build_vulnerability_curves()
    print("✅ Vulnerability curves ready.")

    # ------------------------------------------------------------
    # 8. Raw CLIMADA impact
    # ------------------------------------------------------------
    print("\n=== STEP 8: Computing raw impact ===")
    impact_raw = compute_raw_impact(assets_all, impf_set, hazard)
    print("✅ Raw impact computed.")

    # ------------------------------------------------------------
    # 9. Attach losses to points
    # ------------------------------------------------------------
    print("\n=== STEP 9: Attaching losses to exposure points ===")
    exp_with_loss = attach_losses_to_points(assets_all, impact_raw)

    # ------------------------------------------------------------
    # 10. Aggregate to districts
    # ------------------------------------------------------------
    print("\n=== STEP 10: Aggregating to districts ===")
    district_loss_raw = aggregate_district_loss(exp_with_loss, districts)

    print("\nDEBUG: district_loss_raw columns:", district_loss_raw.columns.tolist())
    print(district_loss_raw.head())

    # Compute synthetic DLNA total using CCART-v2 empirical formula
    alpha = 1.7392153456669906e8
    b = 0.10201685392633236

    raw_loss_total = district_loss_raw["loss_usd"].sum()
    dlna_total = alpha * (raw_loss_total ** b)

    print(f"Computed synthetic DLNA_total = {dlna_total:,.0f} USD")


    # ------------------------------------------------------------
    # 11. Calibrating to synthetic DLNA total (hazard-based inland)
    # ------------------------------------------------------------
    print("\n=== STEP 11: Calibrating to synthetic DLNA total ===")

    # Use hazard_mask as the coastal / inland flag
    loss_with_flag = district_loss_raw.merge(
        hazard_stats[["District", "hazard_mask"]],
        on="District",
        how="left",
    )

    coastal = loss_with_flag[loss_with_flag["hazard_mask"] == True].copy()
    inland  = loss_with_flag[loss_with_flag["hazard_mask"] == False].copy()

    coastal = coastal.drop(columns=["hazard_mask"])
    inland  = inland.drop(columns=["hazard_mask"])

    # Rename raw loss column for clarity
    coastal = coastal.rename(columns={"loss_usd": "loss_usd_raw"})

    # Calibrate using the correct column
    coastal_cal = calibrate_to_total(coastal, dlna_total, loss_col="loss_usd_raw")

    # Inland stays zero
    inland_cal = inland.copy()
    inland_cal["loss_usd_cal"] = 0.0

    district_loss_cal = pd.concat([coastal_cal, inland_cal], ignore_index=True)


    # ------------------------------------------------------------
    # 12. Calibration diagnostic (no extra zeroing here)
    # ------------------------------------------------------------
    print("\n=== CALIBRATION DIAGNOSTIC ===")
    print("Raw district loss total:", district_loss_raw["loss_usd"].sum())
    print("Calibrated loss total  :", district_loss_cal["loss_usd_cal"].sum())


    # ------------------------------------------------------------
    # 13. HWE weights (consistent with calibration mask)
    # ------------------------------------------------------------
    print("\n=== STEP 13: Building HWE weights ===")
    hwe_weights = build_hwe_weights(hazard_stats, exp_dist)

    # Attach hazard_mask
    hwe_weights = hwe_weights.merge(
        hazard_stats[["District", "hazard_mask"]],
        on="District",
        how="left",
    )

    # Zero inland / non-hazard districts
    hwe_weights.loc[hwe_weights["hazard_mask"] == False, "HWE_weight_norm"] = 0.0

    # Renormalize over coastal districts
    total_weight = hwe_weights["HWE_weight_norm"].sum()
    if total_weight > 0:
        hwe_weights["HWE_weight_norm"] /= total_weight

    # Clean up
    hwe_weights = hwe_weights.drop(columns=["hazard_mask"])


    # ------------------------------------------------------------
    # 14. Merge calibrated + HWE with geometry + original names
    # ------------------------------------------------------------
    print("\n=== STEP 14: Final merge and summary ===")

    merged = districts.merge(district_loss_cal, on="District", how="left")
    merged = merged.merge(
        hwe_weights[["District", "HWE_weight_norm"]],
        on="District",
        how="left",
    )
    merged = merged.merge(
        gdf_all[["District", "district", "state"]],
        on="District",
        how="left",
    )

    merged["loss_usd_hwe"] = merged["HWE_weight_norm"] * dlna_total
    merged = merged.fillna(0)
    merged = merged.rename(columns={"district": "District_label"})

    total_cal_loss = merged["loss_usd_cal"].sum()
    total_hwe_loss = merged["loss_usd_hwe"].sum()

    print("\n=== SYNTHETIC CYCLONE IMPACT SUMMARY ===")
    print(f"  Synthetic DLNA target : {dlna_total:,.0f} USD")
    print(f"  Calibrated total loss : {total_cal_loss:,.0f} USD")
    print(f"  HWE total loss        : {total_hwe_loss:,.0f} USD")
    print(f"  Districts with loss   : {(merged['loss_usd_cal'] > 0).sum()}")


    # ------------------------------------------------------------
    # FIX GEOMETRY COLUMN (single clean block)
    # ------------------------------------------------------------
    geom_cols = [c for c in merged.columns if c.startswith("geometry")]

    if "geometry_x" in geom_cols:
        merged = merged.set_geometry("geometry_x")
        merged = merged.drop(columns=[c for c in geom_cols if c != "geometry_x"])
        merged = merged.rename(columns={"geometry_x": "geometry"})

    elif "geometry_y" in geom_cols:
        merged = merged.set_geometry("geometry_y")
        merged = merged.drop(columns=[c for c in geom_cols if c != "geometry_y"])
        merged = merged.rename(columns={"geometry_y": "geometry"})

    merged = gpd.GeoDataFrame(merged, geometry="geometry", crs="EPSG:4326")


    # ------------------------------------------------------------
    # Save to file
    # ------------------------------------------------------------
    out_path = os.path.join(base_dir, "outputs", "synthetic_cyclone_impact.gpkg")
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    merged.to_file(out_path, driver="GPKG")
    print(f"\n✅ Saved synthetic impact to:\n   {out_path}")


    # ------------------------------------------------------------
    # 15. Generate choropleth
    # ------------------------------------------------------------
    ccart_choropleth_v2(
        gdf_districts=gdf_all,
        df_losses=merged,
        district_col="District",
        loss_col="loss_usd_hwe",   # or "loss_usd_cal"
        state_filter=None,
        title="Synthetic Cyclone Impact – District Loss (HWE)",
        save_path=os.path.join(base_dir, "outputs", "synthetic_cyclone_choropleth.png"),
    )


if __name__ == "__main__":
    main()

