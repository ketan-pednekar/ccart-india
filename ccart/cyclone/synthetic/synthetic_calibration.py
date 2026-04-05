"""
CCART Synthetic Calibration Module
----------------------------------
Handles:
- DLNA synthetic total computation
- coastal filtering via hazard mask
- calibration of coastal districts
- inland zeroing
- merging calibrated + inland losses
"""

import pandas as pd
from ccart.calibration.calibration import calibrate_to_total


# ------------------------------------------------------------
# 1. Compute DLNA synthetic total
# ------------------------------------------------------------
def compute_dlna_total(raw_district_total, alpha, b):
    """
    Compute synthetic DLNA total using the power-law relationship:

        DLNA_total = alpha * (raw_total ** b)

    Args:
        raw_district_total (float): Sum of raw district losses
        alpha (float): DLNA scaling parameter
        b (float): DLNA exponent

    Returns:
        float: DLNA synthetic total
    """
    return alpha * (raw_district_total ** b)


# ------------------------------------------------------------
# 2. Split coastal vs inland using hazard_mask
# ------------------------------------------------------------
def split_coastal_inland(district_loss_raw, hazard_stats):
    """
    Merge hazard_mask into district losses and split into:
    - coastal (mask = True)
    - inland  (mask = False)

    Returns:
        coastal_df, inland_df
    """
    merged = district_loss_raw.merge(
        hazard_stats[["District", "hazard_mask"]],
        on="District",
        how="left",
    )

    coastal = merged[merged["hazard_mask"] == True].copy()
    inland = merged[merged["hazard_mask"] == False].copy()

    return coastal, inland


# ------------------------------------------------------------
# 3. Calibrate coastal districts to DLNA total
# ------------------------------------------------------------
def calibrate_coastal_losses(coastal_df, dlna_total):
    """
    Calibrate coastal district losses to match DLNA total.

    Args:
        coastal_df (DataFrame): coastal districts with raw losses
        dlna_total (float): DLNA synthetic total

    Returns:
        DataFrame: calibrated coastal losses
    """
    coastal_df = coastal_df.rename(columns={"loss_usd": "loss_usd_raw"})

    calibrated = calibrate_to_total(
        coastal_df,
        dlna_total,
        loss_col="loss_usd_raw",
    )

    return calibrated.rename(columns={"loss_usd_calibrated": "loss_usd_cal"})


# ------------------------------------------------------------
# 4. Zero out inland districts
# ------------------------------------------------------------
def zero_inland_losses(inland_df):
    """
    Inland districts receive:
    - raw loss unchanged
    - calibrated loss = 0
    - calibration_factor = 0
    """
    inland_df = inland_df.rename(columns={"loss_usd": "loss_usd_raw"})
    inland_df["loss_usd_cal"] = 0.0
    inland_df["calibration_factor"] = 0.0
    return inland_df


# ------------------------------------------------------------
# 5. Combine calibrated coastal + inland
# ------------------------------------------------------------
def combine_calibrated_losses(coastal_cal, inland_cal):
    """
    Combine coastal and inland calibrated losses into one table.

    Returns:
        DataFrame
    """
    return pd.concat([coastal_cal, inland_cal], ignore_index=True)
