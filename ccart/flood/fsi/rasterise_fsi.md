# CCART‑Floods — FSI Rasterisation (`rasterise_fsi.py`)

## Purpose
`rasterise_fsi.py` converts point‑based **FSI values** into a CHIRPS‑aligned
raster. This module performs **no interpolation** — it rasterises only empirical
values, cleans them, and rescales them to produce the canonical susceptibility
layer used by the CCART‑Floods hazard engine.

This module performs three steps:

1. **Rasterise** `FSI_masked` to the CHIRPS grid  
2. **Clean** values (retain only 0–1, else NaN)  
3. **Rescale** valid values to the full 0–1 range  

The output is a CHIRPS‑aligned susceptibility raster ready for export.

---

## Scientific Background

FSI is computed at gauge locations. To integrate susceptibility with
rainfall hazards (CHIRPS, CMIP6), it must be aligned to the same grid.

Unlike traditional approaches, CCART‑Floods:

- does **not** interpolate susceptibility  
- does **not** smooth across hydrological boundaries  
- does **not** fabricate values in proxy basins  

Instead, CCART uses **direct rasterisation** of empirical values, preserving
hydrological honesty and avoiding artificial surfaces.

---

## Inputs

| Input | Type | Description |
|-------|------|-------------|
| `gdf_fsi` | GeoDataFrame | from `compute_fsi()` containing FSI_masked|
| `chirps_transform` | `affine.Affine` | Spatial transform of the CHIRPS grid |
| `shape` | tuple | `(rows, cols)` of the CHIRPS grid |

---

## Outputs

| Output | Type | Description |
|--------|------|-------------|
| `fsi_rescaled` | 2D `np.ndarray` | Cleaned and min–max rescaled susceptibility raster (0–1, NaN outside empirical basins) |

This raster is passed directly to `export_fsi_raster.py`.

---

## Functions in This Module

### **`rasterise_fsi(gdf_fsi_v1_2, chirps_transform, shape)`**
Rasterises `FSI_masked` values to the CHIRPS grid using point‑to‑grid
burning. No interpolation is performed.

### **`clean_fsi(fsi_raster)`**
Ensures all values lie within the valid **0–1** range.  
Anything outside this range becomes `NaN`.

### **`rescale_fsi(fsi_clean)`**
Min–max rescales valid values to the full **0–1** range.
Rescaling ensures the susceptibility raster spans the full 0–1 range after rasterisation, preserving contrast across basins.

### **`rasterise_clean_rescale_fsi(...)`**
Full pipeline wrapper:

1. Rasterise  
2. Clean  
3. Rescale  

Returns the final susceptibility raster.

---

## Usage Example

```python
from ccart.flood.fsi.compute_fsi import compute_fsi
from ccart.flood.fsi.rasterise_fsi import rasterise_clean_rescale_fsi

fsi_rescaled = rasterise_clean_rescale_fsi(
    gdf_fsi = compute_fsi(),
    chirps_transform=chirps_transform,
    shape=shape
)
```
## Notes

- This module performs no interpolation — only rasterisation.
- Proxy basins remain NaN throughout the pipeline.
- Cleaning and rescaling ensure numerical stability and reproducibility.
- The output raster is consumed directly by `export_fsi_raster.py`.
- All rasters align exactly with the CHIRPS grid (0.05° resolution, EPSG:4326).