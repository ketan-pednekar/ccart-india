"""
CCART v1.0 — Hazard–Exposure Weighting Engine (HWE)
---------------------------------------------------

This module implements CCART's transparent spatial allocation engine.

HWE allocates calibrated state-level losses across districts using:

    w_i = (H_i ** alpha) * (E_i ** beta)

where:
- H_i = hazard severity (e.g., max wind speed)
- E_i = exposure magnitude (LitPop)
- alpha, beta = weighting exponents

Normalized weights:
    w_norm_i = w_i / sum_j w_j

District-level HWE losses:
    loss_hwe_i = w_norm_i * StateTotal

This module is reusable across states, cyclones, and scenarios.
"""

import pandas as pd


def build_hwe_weights(hazard_stats: pd.DataFrame,
                      exp_dist: pd.DataFrame,
                      alpha: float = 1.0,
                      beta: float = 1.0,
                      wind_col: str = "WindSpeed_Max_mps",
                      exp_col: str = "Exposure_Value") -> pd.DataFrame:
    """
    Build hazard–exposure weights for district-level allocation.

    Parameters
    ----------
    hazard_stats : DataFrame
        Must contain:
        - 'District'
        - wind_col (hazard metric)
    exp_dist : DataFrame
        Must contain:
        - 'District'
        - exp_col (exposure metric)
    alpha : float
        Exponent for hazard severity.
    beta : float
        Exponent for exposure magnitude.
    wind_col : str
        Column name for hazard metric.
    exp_col : str
        Column name for exposure metric.

    Returns
    -------
    DataFrame
        Columns:
        - District
        - H_i (hazard term)
        - E_i (exposure term)
        - HWE_weight
        - HWE_weight_norm
    """

    # Merge hazard + exposure
    df = hazard_stats.merge(exp_dist, on="District", how="inner")

    # Extract hazard and exposure terms
    df["H_i"] = df[wind_col].clip(lower=0)
    df["E_i"] = df[exp_col].clip(lower=0)

    # Compute raw weights
    df["HWE_weight"] = (df["H_i"] ** alpha) * (df["E_i"] ** beta)

    # Normalize
    total = df["HWE_weight"].sum()
    if total <= 0:
        raise ValueError("HWE weights sum to zero; check hazard/exposure inputs.")

    df["HWE_weight_norm"] = df["HWE_weight"] / total

    return df[["District", "H_i", "E_i", "HWE_weight", "HWE_weight_norm"]]