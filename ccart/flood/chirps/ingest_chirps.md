# CCART-Floods — CHIRPS Ingestion (`ingest_chirps.py`)

## Purpose
`ingest_chirps.py` provides the ingestion layer for CHIRPS daily rainfall data.
It inventories CHIRPS files, loads each day clipped to India, cleans invalid
values, and establishes the reference CHIRPS grid used across the rainfall and
hazard subsystems.

This module is the entry point for all CHIRPS-based rainfall processing in CCART.

---

## What This Module Does

### **1. Inventories CHIRPS daily files**
- Scans the CHIRPS directory structure (`CHIRPS_DIR/year/*.tif`)
- Extracts year, month, and day from filenames
- Builds a clean, sorted DataFrame of all available daily rasters

### **2. Loads daily rainfall clipped to India**
Using `rasterio.mask.mask`, each daily raster is:
- clipped to the India boundary  
- converted to `float32`  
- cleaned (negative or invalid values → 0 mm/day)

### **3. Establishes the CHIRPS reference grid**
From the first available file, the module extracts:
- raster shape (rows × cols)  
- affine transform  
- CRS (`EPSG:4326`)  

This ensures all downstream rainfall metrics (Rx2day, P95, hazard) are aligned.

### **4. Returns a CHIRPS metadata object**
The `load_chirps()` function returns a dictionary containing:
- `file_df` — inventory of daily files  
- `shape` — CHIRPS clipped grid shape  
- `transform` — affine transform  
- `crs` — coordinate reference system  
- `india_geom` — India boundary geometry  
- `load_day` — pointer to the daily loader function  

This metadata object is used by `compute_metrics.py` and the hazard engine.

---

## Functions in This Module

### **`load_day(fp, india_geom)`**
Loads a single CHIRPS daily raster:
- clips to India  
- cleans invalid values  
- returns `(array, transform)`  

### **`inventory_chirps(chirps_dir, start_year, end_year)`**
Builds a sorted DataFrame of all CHIRPS daily files:
- path  
- year  
- month  
- day  

### **`get_reference_grid(file_df, india_geom)`**
Loads the first CHIRPS file to determine:
- grid shape  
- transform  
- CRS  

### **`load_chirps(start_year=None, end_year=None)`**
Main entry point.  
Returns a metadata dictionary containing everything needed for rainfall metrics.

---

## Usage Example

```python
from ccart_floods.chirps.ingest_chirps import load_chirps

chirps = load_chirps(start_year=1995, end_year=2024)

print(chirps["shape"])
print(chirps["file_df"].head())
```
---

## Notes
- CHIRPS is already at 0.05° resolution, matching CCART’s FSI rasters.
- Negative rainfall values occasionally appear in CHIRPS; these are set to 0.
- India masking ensures clean national boundaries and consistent hazard inputs.
- This module does not compute rainfall metrics — that is handled by `compute_metrics.py`.