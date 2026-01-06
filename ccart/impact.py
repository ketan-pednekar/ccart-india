"""
CCART v1.0 — Impact Module
--------------------------

This module computes cyclone impacts using CLIMADA:

- Point-level raw impact using LitPop exposure and vulnerability curves
- District-level aggregation of losses
- Clean, reusable functions for any state or cyclone

These functions form the core of the CCART loss engine.
"""

import numpy as np
import geopandas as gpd
from climada.entity import Exposures
from climada.engine.impact_calc import ImpactCalc


def compute_raw_impact(assets_state: gpd.GeoDataFrame,
                       impf_set,
                       hazard):
    """
    Compute raw CLIMADA impact at the exposure-point level.

    Parameters
    ----------
    assets_state : GeoDataFrame
        LitPop exposure points for the state.
        Must include:
        - geometry
        - value (USD exposure)
    impf_set : ImpactFuncSet
        Vulnerability curves.
    hazard : TropCyclone
        CLIMADA hazard object.

    Returns
    -------
    impact_raw : Impact
        CLIMADA Impact object.
    """
    exp = Exposures(assets_state.copy())
    exp.gdf["value"] = exp.gdf["value"]
    exp.gdf["impf_TC"] = 1  # Housing curve by default

    impact_raw = ImpactCalc(exp, impf_set, hazard).impact()
    return impact_raw


def attach_losses_to_points(assets_state: gpd.GeoDataFrame,
                            impact_raw):
    """
    Attach raw CLIMADA losses to exposure points.

    Parameters
    ----------
    assets_state : GeoDataFrame
        Exposure points.
    impact_raw : Impact
        CLIMADA Impact object.

    Returns
    -------
    GeoDataFrame
        Exposure points with a new column 'loss_usd'.
    """
    loss_array = np.asarray(impact_raw.imp_mat.todense())[0, :]
    gdf = assets_state.copy()
    gdf["loss_usd"] = loss_array
    return gdf


def aggregate_district_loss(exp_with_loss: gpd.GeoDataFrame,
                            districts: gpd.GeoDataFrame):
    """
    Aggregate point-level losses to district-level totals.

    Parameters
    ----------
    exp_with_loss : GeoDataFrame
        Exposure points with 'loss_usd'.
    districts : GeoDataFrame
        District polygons with 'District' column.

    Returns
    -------
    DataFrame
        Columns:
        - District
        - loss_usd
    """
    exp_clean = exp_with_loss.drop(
        columns=["index_left", "index_right"], errors="ignore"
    )

    joined = gpd.sjoin(
        exp_clean,
        districts[["District", "geometry"]],
        how="inner",
        predicate="within"
    )

    if "District_right" in joined.columns:
        joined = joined.rename(columns={"District_right": "District"})

    district_loss = (
        joined.groupby("District")["loss_usd"]
        .sum()
        .reset_index()
    )

    return district_loss