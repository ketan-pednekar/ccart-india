"""
CCART-Heat Wet Bulb Temperature Engine (0.05° India Grid)
=========================================================

This module implements the Stull (2011) empirical wet bulb temperature
approximation and exposes a Dask-parallelized xarray interface suitable
for large-scale climate hazard computation on the canonical CCART 0.05°
India grid.

Functionality
-------------
- Implements the Stull (2011) wet bulb temperature formula.
- Provides a Dask-compatible WBT computation using xarray.apply_ufunc.
- Ensures safe alignment of temperature and humidity along the *time*
  dimension (lat/lon are already aligned by ingestion).
- Returns a lazily-evaluated DataArray suitable for downstream hazard
  metrics (WBT > 35°C exceedance, time-slice aggregation, CCART Number).

Inputs
------
T_k : xr.DataArray
    Daily maximum temperature in Kelvin (CMIP6 tasmax).
RH  : xr.DataArray
    Daily relative humidity in percent (0–100).

Outputs
-------
xr.DataArray
    Wet bulb temperature in Celsius, aligned with input coordinates.

Notes
-----
- This engine is resolution-agnostic and works directly on the 0.05°
  India grid produced by the ingestion module.
- All heavy lifting (regridding, clipping) is done upstream.
"""

import numpy as np
import xarray as xr

# ---------------------------------------------------------
# Stull (2011) wet bulb temperature approximation
# ---------------------------------------------------------
def wet_bulb_stull(T_c: xr.DataArray,
                   RH: xr.DataArray) -> xr.DataArray:
    return (
        T_c * np.arctan(0.151977 * np.sqrt(RH + 8.313659))
        + np.arctan(T_c + RH)
        - np.arctan(RH - 1.676331)
        + 0.00391838 * RH**1.5 * np.arctan(0.023101 * RH)
        - 4.686035
    )


# ---------------------------------------------------------
# Dask-parallelized WBT computation
# ---------------------------------------------------------
def compute_wbt(T_k: xr.DataArray,
                RH: xr.DataArray) -> xr.DataArray:

    # Align along time (lat/lon already aligned by ingestion)
    T_k, RH = xr.align(T_k, RH, join="inner")

    # Kelvin → Celsius
    T_c = T_k - 273.15

    # Apply Stull formula lazily
    WBT = xr.apply_ufunc(
        wet_bulb_stull,
        T_c,
        RH,
        input_core_dims=[[], []],
        output_core_dims=[[]],
        dask="parallelized",
        output_dtypes=[np.float32],
    )

    WBT.name = "wbt"
    WBT.attrs["units"] = "°C"
    return WBT
