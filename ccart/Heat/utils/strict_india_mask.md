# Strict India Mask Generator

## Purpose

This utility creates a strict India land‑boundary mask aligned exactly to the grid of a given xarray.DataArray.

It ensures:

- Perfect pixel‑level alignment with the template grid
- Correct north‑up affine transform
- Correct handling of ascending or descending latitude
- A clean binary mask (1 = inside India, 0 = outside)

This mask is used throughout CCART‑Heat for clipping hazards, filtering DEMs, and ensuring spatial consistency across modules.

---

## Inputs

- Template DataArray  
    Must contain:
    - 1D lat coordinate
    - 1D lon coordinate
    - Regular grid spacing
- India districts or boundary file  
    Example:
    ```
    INDIA_DISTRICTS_734.gpkg
    ```

Any polygon dataset covering India is acceptable.

---

## Core Logic

### 1. CRS normalization

The shapefile is reprojected to EPSG:4326 to match CMIP6 grids.

### 2. Grid extraction

The function reads:
- `lat (1D)`
- `lon (1D)`
- Computes `dlat`, `dlon`

### 3. North‑up affine transform

Regardless of whether latitude is ascending or descending, the mask is rasterized using a north‑up transform:

```
Affine(
    dlon, 0, lon_min - dlon/2,
    0, -abs(dlat), lat_max + abs(dlat)/2
)
```
This ensures:

- Row 0 = northernmost latitude
- Rasterization aligns with the template grid
- No orientation ambiguity

### 4. Rasterization

The India polygon union is rasterized with:

- `all_touched=True` (captures edge pixels)
- `dtype="uint8"`

### 5. Output

Returns an `xr.DataArray` with:

- Same `lat` and `lon` as the template
- Values: `1 = inside India`, `0 = outside`
-  Name: `"strict_mask"`

---

### How to Use

```python
mask = make_strict_mask(template_da, "INDIA_DISTRICTS_734.gpkg")
```

You can then apply it as:

```python
clipped = template_da.where(mask == 1)
```
---

## Why This Mask Is “Strict”

- Uses full India polygon union
- Uses north‑up transform (no ambiguity)
- Uses `all_touched=True` to avoid missing coastal pixels
- Ensures pixel‑perfect alignment with CMIP6 grids
- Works for both ascending and descending latitude arrays

This avoids common issues like:

- Missing Tamil Nadu
- Missing Northeast India
- Mask shifted by half a pixel
- Mask flipped vertically
- Misalignment with hazard grids

---

## Troubleshooting

### 1. Mask appears shifted

Cause: template grid not regular

Fix: ensure `lat` and `lon` are 1D and evenly spaced.

### 2. Mask appears flipped


Cause: plotting function using `origin="lower"`  

Fix: use `origin="upper"` when visualizing.

### 3. Mask is all zeros

Cause: wrong CRS in shapefile

Fix: ensure shapefile is in EPSG:4326.

---

## Notes

- This mask is the canonical India mask for CCART‑Heat.
- Use it for all hazard clipping, DEM filtering, and district‑level validation.
- This function is stable and should not be modified unless grid conventions change.