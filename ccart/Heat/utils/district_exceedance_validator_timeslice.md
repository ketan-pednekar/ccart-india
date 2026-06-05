# Time‑Slice Cube District Exceedance Validator (Zarr)

## Purpose

This utility validates time‑slice exceedance fields (e.g., WBT35) from CCART‑Heat Zarr time‑slice cubes against India district boundaries.

It ensures:

- Correct spatial orientation of the time‑slice cube
- Correct raster alignment with district polygons
- Correct district‑level exceedance statistics
- Correct point‑level hard checks

This script is used for QA/QC, not for production hazard generation.

---

## Inputs

- Time‑slice Zarr cube  
    Example:
    ```
    cube_timeslice_wbt35_EndCentury_2081-2100.zarr
    ```
- India districts
    ```
    INDIA_DISTRICTS_734.gpkg
    ```
---

## Orientation Logic (Critical)

Time‑slice cubes have:

- `lat descending` (north → south)
- BUT the array is stored upside‑down

Therefore:

- ✔ Always flip the array vertically (`np.flipud`)
- ✔ Use the cube’s native negative dy
- ✔ Anchor at lat.max()

This is Corrected Orientation A*.

The script uses a universal helper:

- If lat ascending → flip (Orientation B)
- If lat descending → flip (Corrected A*)

Both cases require `np.flipud`.

---

## Transform Used

For descending‑lat cubes:

```
Affine(
    dx, 0, lons.min() - dx/2,
    0, dy, lats.max() + dy/2
)
```

Where:

- `dx = lon[1] - lon[0]`
- `dy = lat[1] - lat[0]` (negative)

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

Run the validator from the project root:

```
python district_exceedance_validator_timeslice.py
```
---

## Expected Hard‑Check Behavior

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

Fix: ensure `np.flipud(arr_raw)` is applied.

### 2. Districts misaligned

Cause: incorrect transform

Fix: ensure transform uses negative dy and lat.max() anchor.

### 3. Hard checks wrong but district stats correct

Cause: sampling from unflipped array

Fix: ensure hard checks use `ds[var].sel(...)` (not raster indexing).

---

### Notes

- This validator is for time‑slice Zarr cubes only.
- TIFF time‑slices require a different sampling fix.
- This script is part of the CCART‑Heat QA suite.
- This validator assumes the time‑slice cube contains exceedance counts (e.g., WBT35).
