def run_cyclone_pipeline(
    cyclone_name: str,
    storm_id: str,
    ibtracs_path: str,
    districts_path: str,
    dlna_total: float,
    inland_clip_km: float = 150.0,
    coastline_path: str = None,
    country_code: str = "IND",
):
    """
    State-agnostic, multi-state CCART pipeline.
    Runs cyclone impact for ALL India, then slices by state.

    Returns
    -------
    merged_all : GeoDataFrame
        District-level calibrated + HWE losses for all India.
    outputs_by_state : dict
        {state_name: GeoDataFrame}
    """

    # ------------------------------------------------------------
    # 1. Load ALL India districts
    # ------------------------------------------------------------
    gdf_all = gpd.read_file(districts_path)
    gdf_all["district"] = gdf_all["district"].astype(str)
    gdf_all["state"] = gdf_all["state"].astype(str)

    gdf_all["district_norm"] = _normalize_name(gdf_all["district"])
    gdf_all["state_norm"] = _normalize_name(gdf_all["state"])

    # Canonical key
    gdf_all["District"] = gdf_all["district_norm"]

    # Ensure CRS
    if gdf_all.crs is None or gdf_all.crs.to_string() != "EPSG:4326":
        gdf_all = gdf_all.to_crs("EPSG:4326")

    districts = gdf_all[["District", "geometry"]].copy()

    # ------------------------------------------------------------
    # 2. Optional inland clipping
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
    # 3. Load ALL India LitPop
    # ------------------------------------------------------------
    assets_all, exp_dist = load_litpop_for_state(country_code, districts)

    # ------------------------------------------------------------
    # 4. Build hazard
    # ------------------------------------------------------------
    hazard = build_hazard(storm_id, ibtracs_path)

    # ------------------------------------------------------------
    # 5. District hazard stats
    # ------------------------------------------------------------
    hazard_stats = compute_district_hazard_stats(hazard, districts)

    # Hazard floor
    hazard_stats["hazard_ok"] = hazard_stats["WindSpeed_Max_mps"] >= HAZARD_FLOOR_MS

    # ------------------------------------------------------------
    # 6. Vulnerability curves
    # ------------------------------------------------------------
    impf_set = build_vulnerability_curves()

    # ------------------------------------------------------------
    # 7. Raw CLIMADA impact
    # ------------------------------------------------------------
    impact_raw = compute_raw_impact(assets_all, impf_set, hazard)

    # ------------------------------------------------------------
    # 8. Attach losses to points
    # ------------------------------------------------------------
    exp_with_loss = attach_losses_to_points(assets_all, impact_raw)

    # ------------------------------------------------------------
    # 9. Aggregate to districts
    # ------------------------------------------------------------
    district_loss_raw = aggregate_district_loss(exp_with_loss, districts)

    # ------------------------------------------------------------
    # 10. Inland clipping BEFORE calibration
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
    # 11. Apply hazard floor to calibrated losses
    # ------------------------------------------------------------
    district_loss_cal = district_loss_cal.merge(
        hazard_stats[["District", "hazard_ok"]],
        on="District",
        how="left",
    )
    district_loss_cal.loc[district_loss_cal["hazard_ok"] == False, "loss_usd_cal"] = 0.0
    district_loss_cal = district_loss_cal.drop(columns=["hazard_ok"])

    # ------------------------------------------------------------
    # 12. HWE weights
    # ------------------------------------------------------------
    hwe_weights = build_hwe_weights(hazard_stats, exp_dist)

    # Apply inland clipping to HWE
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

    # Apply hazard floor to HWE
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
    # 13. Merge calibrated + HWE + geometry + original names
    # ------------------------------------------------------------
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

    # HWE losses
    merged["loss_usd_hwe"] = merged["HWE_weight_norm"] * dlna_total
    merged = merged.fillna(0)

    # ------------------------------------------------------------
    # 14. Slice by state
    # ------------------------------------------------------------
    outputs_by_state = {
        st: merged[merged["state"] == st].copy()
        for st in merged["state"].unique()
    }

    return merged, outputs_by_state
