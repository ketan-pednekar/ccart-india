# Ingested Cube District Exceedance Validator

## Purpose

This utility validates annual exceedance (Tw > 35°C) from the ingested CCART‑Heat SSP370 cube against India district boundaries.
It ensures:

- Correct spatial orientation of the ingested cube
- Correct raster alignment with district polygons
- Correct district‑level exceedance statistics
- Correct point‑level hard checks for known locations

This script is used for QA/QC, not for production hazard generation.

---

## Inputs

- Ingested Zarr cube

    ```
    ccart/Heat/ingested/ssp370/
    ```
    Must contain variable `wbt` with dims `(time, lat, lon)`.

- India districts

```
INDIA_DISTRICTS_734.gpkg
```
---

## Exceedance Definition

Annual exceedance is computed as:

```
exceed(year) = count of days where Tw > 35°C
```
Then:

```
max_exceed = maximum exceedance across all years
```
This matches the CCART‑Heat hazard cube definition.

---

## Orientation Logic (Critical)

Ingested SSP370 cube

- `lat` is ascending (south → north)
- But the array is stored upside‑down

Therefore:

- ✔ Flip the array vertically (`np.flipud`)
- ✔ Use positive dy in the transform
- ✔ Anchor at lat.min()

This is Orientation B.

This orientation was validated visually and numerically.

---

## Transform Used

```
Affine(
    dx, 0, lons.min() - dx/2,
    0, +dy, lats.min() - dy/2
)
```
Where:

- `dx = lon[1] - lon[0]`
- `dy = lat[1] - lat[0]` (positive)

---

## Outputs

- District‑level:
    - mean_exceed
    - max_exceed
- Sorted Top‑100 districts
- Hard checks for:
    - Guwahati (Assam)
    - Kendrapara (Odisha)
    - Namsai (Arunachal)

These confirm correct spatial alignment.

---

## How to Run

```
python district_exceedance_validator_ingested.py
```

| Location | Expected Behavior |
| --- | --- |
| **Guwahati** | Moderate exceedance (~40–60) |
| **Kendrapara** | Very high exceedance (~150+) |
| **Namsai** | Low–moderate (~20–60) |

If these values are inverted or zero → orientation is wrong.

---

## Troubleshooting

### 1. Map looks flipped

Cause: wrong orientation

Fix: ensure `np.flipud(raw_arr)` is applied.

### 2. Districts misaligned

Cause: wrong transform

Fix: ensure transform uses positive dy and lat.min() anchor.

### 3. Hard checks wrong but district stats correct

Cause: sampling from unflipped array
Fix: ensure hard checks use exceed_max.sel(...) (not raster indexing).

---

## Notes

- This validator is for ingested cubes only.
- Time‑slice cubes and TIFFs require different orientation logic.
- This script is part of the CCART‑Heat QA suite and should not be used for production hazard generation