# Time‑Slice TIFF District Exceedance Validator

## Purpose

This utility validates TIFF‑exported time‑slice exceedance fields (e.g., WBT35) from CCART‑Heat against India district boundaries.

It ensures:

- Correct spatial orientation of the TIFF
- Correct raster alignment with district polygons
- Correct district‑level exceedance statistics
- Correct point‑level hard checks

This script is used for QA/QC, not for production hazard generation.

---

## Inputs

- Time‑slice TIFF hazard file  
    Example:
    ```
    CCART_Hazard_WBT35_EndCentury_2081-2100.tif
    ```
- India districts
    ```
    INDIA_DISTRICTS_734.gpkg
    ```
---

## Orientation Logic (Critical)
TIFF time‑slice exports have:

- A correct geotransform
- A correct CRS
- BUT the pixel array is stored upside‑down relative to the transform

Therefore:

- ✔ Always flip the TIFF array vertically (`np.flipud`)
- ✔ Keep the TIFF’s original transform unchanged
- ✔ Rasterize districts normally (no flip)
- ✔ Hard‑check sampling uses the flipped array

This combination produces correct spatial alignment.

---

## Transform Used

The TIFF’s own transform is used directly:

```
| dx,   0,  x_min |
|  0,  dy,  y_max |
|  0,   0,     1  |
```

Where:

- `dx > 0`
- `dy < 0` (north‑up raster)

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
python district_exceedance_validator_timeslice_tif.py
```
---

## Expected Hard‑Check Behavior

| Location | Expected Behavior |
| --- | --- |
| **Guwahati** | Moderate exceedance (~40–60) |
| **Kendrapara** | Very high exceedance (~150+) |
| **Namsai** | Low–moderate (~20–60) |


If these values are inverted or zero → orientation or sampling is wrong.

---

## Troubleshooting

### 1. Map looks flipped

Cause: TIFF array stored upside‑down

Fix: ensure `np.flipud(arr_raw)` is applied.

### 2. Districts misaligned

Cause: incorrect transform

Fix: use the TIFF’s native transform (do not modify).

### 3. Hard checks wrong but district stats correct

Cause: sampling from unflipped array

Fix: ensure hard checks read from the flipped array.

---

## Notes

- This validator is for TIFF time‑slice hazard files only.
- Zarr time‑slice cubes require different orientation logic.
- This script is part of the CCART‑Heat QA suite.