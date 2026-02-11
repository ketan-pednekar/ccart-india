"""
CCART v1.0 — Calibration Module
-------------------------------

This module provides functions to calibrate raw CLIMADA losses to
state-level DLNA/PDNA totals.

Calibration logic:
    k = DLNA_total / raw_total

District-level calibrated losses:
    loss_calibrated_i = loss_raw_i * k

This module keeps calibration transparent, simple, and reproducible.
"""

import pandas as pd


def calibrate_to_total(district_loss: pd.DataFrame,
                       dlna_total: float,
                       loss_col: str = "loss_usd") -> pd.DataFrame:
    """
    Scale district-level raw losses to match a given DLNA/PDNA total.

    Parameters
    ----------
    district_loss : DataFrame
        Must contain:
        - 'District'
        - loss_col (raw CLIMADA loss)
    dlna_total : float
        State-level DLNA/PDNA total loss (USD).
    loss_col : str
        Column name for raw losses.

    Returns
    -------
    DataFrame
        Columns:
        - District
        - loss_usd_raw
        - loss_usd_calibrated
        - calibration_factor
    """
    df = district_loss.copy()
    raw_total = df[loss_col].sum()

    if raw_total <= 0:
        raise ValueError("Raw total loss is zero or negative; cannot calibrate.")

    k = dlna_total / raw_total

    df["loss_usd_raw"] = df[loss_col]
    df["loss_usd_calibrated"] = df[loss_col] * k
    df["calibration_factor"] = k

    return df[["District", "loss_usd_raw", "loss_usd_calibrated", "calibration_factor"]]