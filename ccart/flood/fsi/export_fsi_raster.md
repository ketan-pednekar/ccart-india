# CCART‑Floods — FSI Raster Exporter (`export_fsi_raster.py`)

## Purpose

`export_fsi_raster.py` writes the **final Flood Susceptibility Index (FSI)** to a **CHIRPS‑aligned GeoTIFF**.

This module is the final step of the FSI pipeline:

- After FSI is computed (v1.1 + v1.2)
- After proxy basins are masked
- After the FSI is rasterised, cleaned, and rescaled to 0–1
- After alignment to the CHIRPS grid

The exporter produces the **canonical CCART‑Floods susceptibility raster** used by the hazard engine.
This module does not modify values — it only writes the raster to disk.

---

## What This Module Does

- Accepts a 2D float32 FSI array already aligned to the CHIRPS grid
- Writes a **GeoTIFF** with:
  - CHIRPS transform
  - EPSG:4326 CRS
  - `float32` dtype
  - `NaN` nodata
  - LZW compression

This ensures the FSI raster is fully compatible with:

- CHIRPS rainfall Zarr cubes
- Hazard engines
- CCART‑Number
- Future CMIP6 workflows

---

## Inputs

| Input            | Description                                           |
|------------------|-------------------------------------------------------|
| fsi_rescaled     | 2D float32 array (0–1, NaN outside empirical basins)  |
| chirps_transform | Affine transform of the CHIRPS grid                   |
| crs              | Coordinate reference system (default: EPSG:4326)      |
| out_path         | Output GeoTIFF path                                   |

---

## Outputs

| Output   | Description                                                   |
|----------|---------------------------------------------------------------|
| GeoTIFF  | CHIRPS‑aligned FSI raster with float32 dtype and NaN nodata   |

The output raster has:

- **Exact CHIRPS grid alignment**
- **1 band**
- **`float32`** values
- **`NaN`** for ungauged/proxy basins
- **LZW compression**

---

## FSI Raster Characteristics

| Property        | Value / Description                         |
|-----------------|----------------------------------------------|
| Grid            | CHIRPS 0.05° grid                            |
| CRS             | EPSG:4326                                    |
| Data type       | float32                                      |
| Value range     | 0–1 (susceptibility)                         |
| Nodata          | NaN                                          |
| Compression     | LZW                                          |
| Alignment       | Matches CHIRPS transform exactly             |

---

## Function Overview

| Function            | Purpose                                      |
|---------------------|----------------------------------------------|
| export_fsi_raster() | Writes final FSI raster to CHIRPS GeoTIFF    |

---

## Usage Example

```python
from ccart.flood.fsi.export_fsi_raster import export_fsi_raster

export_fsi_raster(
    fsi_rescaled=fsi_array,
    chirps_transform=transform,
    out_path="outputs/fsi/fsi_rescaled.tif"
)
```
---

## Notes

- This module **does not compute** FSI — it only exports the final raster.
- FSI must already be:
  - computed (v1.1 + v1.2)
  - masked for proxy basins
  - rasterised to CHIRPS
  - rescaled to 0–1
- The hazard engine expects this exact GeoTIFF format.
- This raster is the canonical static susceptibility layer for CCART‑Floods.