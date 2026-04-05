# CCART‑Floods — Exporting the Final FSI Raster (`export_fsi_raster.py`)

## Purpose
`export_fsi_raster.py` writes the final Flood Susceptibility Index (FSI) raster  
to a CHIRPS‑aligned GeoTIFF. This raster is the canonical susceptibility layer
used throughout the CCART‑Floods hazard engine.

The input raster must already be:
- rasterised to the CHIRPS grid  
- cleaned (invalid values removed)  
- min–max rescaled to the full **0–1** range  

This module performs **only the export step**, ensuring consistent metadata,
alignment, and reproducibility.

---

## What This Module Produces

The output is the official CCART‑Floods susceptibility raster:

`ccart_floods_fsi_v1_2_rescaled.tif`

This raster has:
- **float32** precision  
- **NaN** nodata  
- **EPSG:4326** CRS  
- **CHIRPS grid alignment**  
- **LZW compression**  

It is the exact file consumed by the dynamic hazard pipeline.

---

## Function in This Module

### **`export_fsi_raster(fsi_rescaled, chirps_transform, out_path, crs="EPSG:4326")`**

Writes a 2D FSI raster to GeoTIFF with correct metadata.

#### **Parameters**
| Name | Type | Description |
|------|------|-------------|
| `fsi_rescaled` | `np.ndarray` | 2D float32 array (0–1, NaN outside empirical basins) |
| `chirps_transform` | `affine.Affine` | Spatial transform of the CHIRPS grid |
| `out_path` | `str` or `Path` | Output GeoTIFF path |
| `crs` | `str` | Coordinate reference system (default: EPSG:4326) |

#### **Output**
A GeoTIFF written to disk with:
- correct spatial alignment  
- correct CRS  
- correct nodata handling  
- correct compression  

---

## Usage Example

```python
from ccart_floods.fsi.rasterise_fsi import rasterise_clean_rescale_fsi
from ccart_floods.fsi.export_fsi_raster import export_fsi_raster

# fsi_rescaled = rasterise_clean_rescale_fsi(...)
# chirps_transform = ...

export_fsi_raster(
    fsi_rescaled=fsi_rescaled,
    chirps_transform=chirps_transform,
    out_path="ccart_floods_fsi_v1_2_rescaled.tif"
)
```
---

## Notes

- This module does not rasterise, clean, or rescale FSI.
- Those steps are handled in `rasterise_fsi.py`.
- This module ensures that the final raster is written with consistent metadata
  across all CCART‑Floods runs.
- The output file is directly consumed by the dynamic hazard pipeline (`compute_hazard()` in the notebook).