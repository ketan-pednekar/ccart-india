"""
ingest_chirps_hist.py

Purpose:
    Provide historical rainfall dataset (pr_hist) for CCART-Floods
    using the existing CHIRPS India clipped Zarr dataset.

Input:
    chirps_india_clipped.zarr
        Daily CHIRPS rainfall (mm/day)
        Already clipped to India
        Already aligned to CHIRPS grid
        Already CF-compliant

Output:
    Xarray Dataset with variable 'pr'
    Ready for:
        - Historical hazard engine
        - Historical hazard-max
        - CCART Number
"""

import xarray as xr
from pathlib import Path
from ccart.flood.config import load_paths


def load_pr_hist():
    """
    Load historical CHIRPS rainfall dataset as pr_hist.

    Returns:
        xarray.Dataset with variable 'pr'
    """
    paths = load_paths()
    project_root = Path(paths["project_root"])

    pr_hist_path = project_root / paths["flood"]["inputs"]["pr_hist"]

    print(f"[CHIRPS-HIST] Loading historical rainfall from:\n  {pr_hist_path}")

    ds = xr.open_zarr(pr_hist_path)

    if "pr" not in ds:
        raise ValueError(
            f"'pr' variable not found in {pr_hist_path}. "
            "Expected CHIRPS dataset with variable name 'pr'."
        )

    print("[CHIRPS-HIST] Loaded successfully.")
    print(f"[CHIRPS-HIST] Time range: {str(ds.time.values[0])} → {str(ds.time.values[-1])}")
    print(f"[CHIRPS-HIST] Shape: {ds.pr.shape}")

    return ds


if __name__ == "__main__":
    # Simple test load
    ds = load_pr_hist()
    print(ds)
