import pandas as pd

def build_hwe_weights(hazard_stats: pd.DataFrame,
                      exp_dist: pd.DataFrame,
                      alpha: float = 1.0,
                      beta: float = 1.0,
                      wind_col: str = "WindSpeed_Max_mps",
                      exp_col: str = "Exposure_Value") -> pd.DataFrame:
    """
    Build hazard–exposure weights for district-level allocation.
    """

    # Merge hazard + exposure
    df = hazard_stats.merge(exp_dist, on="District", how="inner")

    # Extract hazard and exposure terms
    df["H_i"] = df[wind_col].clip(lower=0)
    df["E_i"] = df[exp_col].clip(lower=0)

    # Compute raw weights
    df["HWE_weight"] = (df["H_i"] ** alpha) * (df["E_i"] ** beta)

    # Collapse to district-level weights
    weights = df.groupby("District", as_index=False)[["H_i", "E_i", "HWE_weight"]].sum()

    # Normalize
    total = weights["HWE_weight"].sum()
    if total > 0:
        weights["HWE_weight_norm"] = weights["HWE_weight"] / total
    else:
        weights["HWE_weight_norm"] = 0.0

    return weights
