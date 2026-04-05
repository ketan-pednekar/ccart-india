# CCART-Floods — FSI Ingestion (`ingest_fsi.py`)

## Purpose
`ingest_fsi.py` loads the Flood Susceptibility Index (FSI), aligns it to the
CHIRPS rainfall grid, and prepares it for use in the CCART hazard engine.

FSI is a static layer representing terrain-driven flood susceptibility.  
To combine it with rainfall-based metrics (Rx2day, P95), it must be:

- reprojected to the CHIRPS grid  
- masked to the India boundary  
- cleaned and normalised  
- returned as a CHIRPS‑aligned 2D array  

This module performs all of these steps in a clean, reusable way.

---

## What This Module Does

### **1. Loads the India boundary**
`load_india_boundary()`:
- reads the India shapefile  
- converts it to EPSG:4326  
- unions all polygons  
- returns a geometry list suitable for raster masking  

### **2. Loads the raw FSI raster**
`load_fsi_raw()`:
- reads the FSI GeoTIFF  
- extracts the array, transform, and CRS  
- returns them without modification  

### **3. Reprojects FSI to the CHIRPS grid**
`reproject_fsi_to_chirps()`:
- takes the raw FSI  
- reprojects it to the CHIRPS grid using bilinear resampling  
- enforces valid range `[0, 1]`  
- sets invalid or out‑of‑range values to NaN  

This ensures perfect pixel‑level alignment with CHIRPS rainfall metrics.

### **4. High‑level ingestion wrapper**
`ingest_fsi()`:
- loads CHIRPS metadata (shape, transform, CRS, India geometry)  
- loads raw FSI  
- reprojects FSI to CHIRPS  
- returns:

```Python
fsi_on_chirps : 2D float32 array
meta : {
"chirps_shape": (rows, cols),
"chirps_transform": Affine,
"chirps_crs": "EPSG:4326",
"india_geom": [...]
}
```
This is the FSI layer used by the hazard engine.

---

## Functions in This Module

### **`load_india_boundary(india_shp)`**
Loads India boundary and returns a geometry list.

### **`load_fsi_raw(fsi_path)`**
Loads the raw FSI raster and returns:
- array  
- transform  
- CRS  

### **`reproject_fsi_to_chirps(fsi_arr, fsi_transform, fsi_crs, chirps_shape, chirps_transform)`**
Reprojects FSI to the CHIRPS grid and cleans invalid values.

### **`ingest_fsi(fsi_path, india_shp, chirps_start_year, chirps_end_year)`**
High‑level wrapper that:
1. loads CHIRPS metadata  
2. loads raw FSI  
3. reprojects FSI to CHIRPS  
4. returns aligned FSI + metadata  

---

## Usage Example

```python
from pathlib import Path
from ccart_floods.hazard.ingest_fsi import ingest_fsi

fsi_path   = Path("data/fsi/fsi_v1_2.tif")
india_shp  = Path("data/shapes/india.shp")

fsi_on_chirps, meta = ingest_fsi(
    fsi_path=fsi_path,
    india_shp=india_shp,
    chirps_start_year=1995,
    chirps_end_year=2024
)

print("FSI shape:", fsi_on_chirps.shape)
```
---

## Notes

- FSI is treated as a static layer (no year‑to‑year variation).
- CHIRPS defines the master grid for all hazard computations.
- Bilinear resampling is used because FSI is a continuous susceptibility field.
- Values outside the valid range [0, 1] are set to NaN.
- This module does not compute hazard — that is handled by `hazard_engine.py`.