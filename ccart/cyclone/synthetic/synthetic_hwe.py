"""
CCART Synthetic HWE Module
--------------------------
Handles:
- preparing HWE inputs (loss + wealth/exposure)
- computing HWE-style indicators
- attaching HWE metrics to district geometries
"""

import pandas as pd


# ------------------------------------------------------------
# 1. Prepare HWE inputs
# ------------------------------------------------------------
def prepare_hwe_inputs(district_loss_cal, wealth_df):
    """
    Merge calibrated district losses with district-level wealth/exposure data.

    Args:
        district_loss_cal (DataFrame): Contains District, loss_usd_cal, etc.
        wealth_df (DataFrame): Contains District, wealth_usd (or similar)

    Returns:
        DataFrame: merged table with calibrated losses + wealth/exposure
    """
    merged = district_loss_cal.merge(
        wealth_df,
        on="District",
        how="left",
        validate="one_to_one"
    )
    return merged


# ------------------------------------------------------------
# 2. Compute HWE metrics
# ------------------------------------------------------------
def compute_hwe_metrics(
    hwe_df,
    loss_col="loss_usd_cal",
    wealth_col="wealth_usd"
):
    """
    Compute HWE-style indicators such as loss share of wealth.

    Adds:
        loss_share = loss_usd_cal / wealth_usd

    Args:
        hwe_df (DataFrame): merged loss + wealth table
        loss_col (str): calibrated loss column
        wealth_col (str): wealth/exposure column

    Returns:
        DataFrame: updated with HWE metrics
    """
    df = hwe_df.copy()

    # Avoid division by zero
    df["loss_share"] = df[loss_col] / df[wealth_col].replace({0: pd.NA})

    return df


# ------------------------------------------------------------
# 3. Attach HWE metrics to district geometries
# ------------------------------------------------------------
def attach_hwe_to_districts(hwe_df, districts_gdf):
    """
    Merge computed HWE metrics back onto district geometries.

    Args:
        hwe_df (DataFrame): contains District + HWE metrics
        districts_gdf (GeoDataFrame): district geometries

    Returns:
        GeoDataFrame: ready for mapping and spatial analysis
    """
    merged = districts_gdf.merge(
        hwe_df,
        on="District",
        how="left",
        validate="one_to_one"
    )
    return merged
