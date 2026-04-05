# CCART-Floods — Raster Utilities (`raster_utils.py`)

## Purpose
`raster_utils.py` provides shared geospatial utilities used across the CHIRPS,
FSI, and hazard subsystems. These functions ensure that all rasters in the
CCART-Floods framework are perfectly aligned to the CHIRPS grid, masked to the
India boundary, and safe for downstream metric computation and hazard modelling.

This module centralises raster operations so that ingestion, metrics, and hazard
code remain clean, modular, and scientifically consistent.

---

## What This Module Does

### **1. Reprojects rasters to the CHIRPS grid**
CHIRPS defines the **master grid** for CCART-Floods (0.05° resolution,
EPSG:4326). All rainfall metrics, susceptibility layers, and hazard maps must
align to this grid.

`reproject_to_chirps()`:
- takes any source raster (e.g., CMIP6, FSI, auxiliary layers)  
- reprojects it to the CHIRPS grid  
- uses bilinear resampling for smooth continuous fields  
- returns a clean, aligned 2D array  

### **2. Masks rasters to the India boundary**
`mask_to_india()`:
- clips any raster to the India polygon  
- sets values outside India to NaN  
- preserves the CHIRPS grid  

This ensures clean national boundaries and prevents artefacts in hazard maps.

### **3. Creates empty rasters aligned to CHIRPS**
`empty_like_chirps()`:
- returns a zero‑filled or NaN‑filled array  
- matches CHIRPS shape and dtype  
- useful for initialising metric arrays  

### **4. Checks grid compatibility**
`check_alignment()`:
- verifies that two rasters share the same shape and transform  
- prevents silent misalignment errors  
- ensures reproducibility and scientific defensibility  

---

## Functions in This Module

### **`reproject_to_chirps(src_arr, src_transform, src_crs, chirps_shape, chirps_transform)`**
Reprojects a source raster to the CHIRPS grid using bilinear resampling.

Returns a 2D float32 array.

### **`mask_to_india(arr, transform, india_geom)`**
Masks a raster to the India boundary.

Returns a masked array with NaNs outside India.

### **`empty_like_chirps(chirps_shape, fill=np.nan, dtype="float32")`**
Creates an empty raster aligned to CHIRPS.

### **`check_alignment(shape_a, transform_a, shape_b, transform_b)`**
Raises an error if two rasters are not aligned.

---

## Usage Example

```python
from ccart_floods.chirps.raster_utils import reproject_to_chirps

aligned = reproject_to_chirps(
    src_arr=cmip_array,
    src_transform=cmip_transform,
    src_crs="EPSG:4326",
    chirps_shape=chirps_meta["shape"],
    chirps_transform=chirps_meta["transform"]
)
```
---

## Notes
- CHIRPS defines the master grid for all CCART rainfall and hazard layers.
- All reprojected rasters use bilinear resampling for smooth, continuous fields.
- Masking uses the same India boundary as CHIRPS ingestion and FSI processing.
- This module does not load data — ingestion is handled by `ingest_chirps.py`.
- This module does not compute rainfall metrics — that is handled by `compute_metrics.py`.

