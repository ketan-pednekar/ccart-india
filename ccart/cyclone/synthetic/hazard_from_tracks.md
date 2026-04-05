# CCART Synthetic Cyclone Hazard Module

This module provides tools for generating synthetic tropical cyclone
hazards using CLIMADA’s `TropCyclone` engine and pre‑processed
`TCTracks` objects. It includes robust preprocessing steps to ensure
track variables are well‑formed, physically reasonable, and compatible
with CLIMADA’s windfield model.

---

## Overview

The functions in this module support the following tasks:

1. Cleaning and standardizing TCTracks variables
2. Applying fallback logic for missing or unrealistic parameters
3. Constructing a centroid grid around the storm track
4. Generating CLIMADA-compatible synthetic cyclone hazard footprints
5. Handling weak storms by producing zero-intensity hazards
6. Producing diagnostics for debugging and validation

These functions are country‑agnostic and can be applied to any synthetic
or perturbed cyclone track dataset.

---

## 🔧 Functions

`build_hazard_from_tc_tracks(tc_tracks, corridor_deg=1.5, grid_res_deg=0.02, min_peak_wind_kn=25.0, verbose=True)`

**Builds a CLIMADA-compatible synthetic cyclone hazard from a single track**.

Generates a synthetic CLIMADA `TropCyclone` hazard object from a single `TCTracks` storm.

This includes:

- Ensuring all track variables are 1D time series
- Applying fallback values for missing or zero radii
- Correcting unrealistic pressure deltas
- Building a centroid grid around the track
- Running CLIMADA’s windfield model
- Cleaning negative intensities
- Producing a zero‑intensity hazard for weak storms
- Printing diagnostics for debugging

---

## Notes

- This module is intended for **synthetic or perturbed cyclone tracks**, not historical IBTrACS data.
- The function expects exactly one storm in the `TCTracks` object.
- Weak storms (below `min_peak_wind_kn`) return a **zero‑intensity hazard**.
- The centroid grid resolution is typically finer than historical mode.
- Outputs are compatible with CCART exposure, vulnerability, and impact modules.

---
## Dependencies

- `numpy`
- `scipy.sparse`
- `climada.hazard (Centroids, TropCyclone)`

---

## 🌱 Function-Level Documentation (Expanded)

`build_hazard_from_tc_tracks`

```python
def build_hazard_from_tc_tracks(
    tc_tracks,
    corridor_deg: float = 1.5,
    grid_res_deg: float = 0.02,
    min_peak_wind_kn: float = 25.0,
    verbose: bool = True,
)
```

Builds a synthetic CLIMADA tropical cyclone hazard from a single
`TCTracks` object.

This function performs extensive preprocessing to ensure that all track
variables are physically reasonable and compatible with CLIMADA’s
windfield model. It then constructs a centroid grid around the storm
track and generates a synthetic hazard footprint.

### Parameters

| Parameter          | Type     | Description                                                                                                           |
|--------------------|----------|-----------------------------------------------------------------------------------------------------------------------|
| `tc_tracks`        | TCTracks | A CLIMADA TCTracks object containing exactly one storm.                                                               |
| `corridor_deg`     | float    | Half‑width of the corridor around the storm track (degrees). Controls the spatial extent of the centroid grid.        |
| `grid_res_deg`     | float    | Resolution of the centroid grid (degrees). Typically finer for synthetic hazards (e.g., 0.02°).                       |
| `min_peak_wind_kn` | float    | Minimum peak wind speed (knots) required to generate a non‑zero hazard. Weak storms return a zero‑intensity hazard.   |
| `verbose`          | bool     | If True, prints diagnostics and variable shapes.                             |


### Returns

`TropCyclone`
A CLIMADA hazard object containing:

- centroids (lat/lon)
- intensity matrix (wind speeds)
- fraction matrix
- metadata and validation flags

For weak storms, the intensity matrix is all zeros.

### Raises

`ValueError`  
If the TCTracks object does not contain exactly one storm.

---

### Notes

- All track variables are reshaped to 1D arrays for safety.
- Missing or zero radii are replaced with fallback values.
- Pressure deltas are corrected to avoid negative or unrealistic values.
- Negative intensities are set to zero.
- Matrices are converted to CSR sparse format.
- The hazard object is validated using `haz.check()`.