# 📘 CCART‑Floods — CHIRPS Ingestion (ingest_chirps.py)

***Config‑driven, global‑or‑regional ingestion of CHIRPS daily rainfall rasters***

## 1. Purpose

`ingest_chirps.py` is the ingestion layer for CHIRPS daily rainfall data in the CCART‑Floods Framework (v2).
It inventories CHIRPS rasters, optionally clips them to a region (e.g., India), cleans invalid values, and establishes the **canonical CHIRPS reference grid** used across rainfall metrics and hazard subsystems.

This module is fully **config‑driven** and supports:

- **Global mode** (no clipping)
- **Regional mode** (clip to any polygon via paths.yaml)
- **Flexible filename patterns**
- **Baseline‑aware ingestion**

It is the first step in the CCART rainfall pipeline.

---

## 2. What This Module Does

### 2.1 Inventories CHIRPS daily files

- Scans the CHIRPS directory structure:
    `CHIRPS_DIR/<year>/*.tif*`
- Extracts year, month, day using a flexible regex:
    `YYYY.MM.DD`, `YYYY-MM-DD`, `YYYY_MM_DD`
- Builds a clean, sorted DataFrame of all available daily rasters
- Respects baseline years defined in `flood_params.yaml`  
    (*used automatically if start/end years are not provided*)

### 2.2 Loads daily rainfall (global or region‑clipped)

Each CHIRPS raster is:

- optionally clipped to a region boundary (`clip_to_region: true/false`)
- converted to `float32`
- cleaned:
    - negative rainfall → 0
    - non‑finite values → 0
    - extreme artefacts (>500 mm/day) → 0

This produces a **clean, analysis‑ready rainfall dataset** for metrics and hazard.

## 2.3 Establishes the CHIRPS reference grid

From the first available file, the module extracts:

- raster shape (rows × cols)
- affine transform
- CRS (`EPSG:4326`)
- latitude and longitude center arrays

*CHIRPS is natively provided in geographic coordinates (EPSG:4326), and CCART preserves this CRS without modification.*

This reference grid becomes the spatial backbone for:

- Rx2day
- P95
- Historical hazard
- Future hazard
- Delta hazard
- Exposure alignment
- CMIP6 regridding

## 2.4 Returns a CHIRPS metadata object

`load_chirps()` returns:

- `file_df` — inventory of daily files
- `years` — sorted list of available years
- `shape` — grid shape
- `lats`, `lons` — coordinate arrays
- `transform` — affine transform
- `crs` — coordinate reference system
- `region_geom` — clipping geometry (or None)
- `clip` — whether clipping is enabled
    - When clipping is enabled, CCART merges all polygons in the region boundary using union_all() to ensure a single clean geometry for masking.
- `load_day` — callable for loading a single raster

This metadata object is consumed by:

- rainfall metrics (`compute_metrics.py`)
- flood hazard engines
- CMIP6 ingestion (for grid alignment)

---

## 3. Functions in This Module

`load_day(fp, region_geom, clip)`

Loads a single CHIRPS raster:

- clips to region if enabled
- cleans invalid values
- returns (`array`, `transform`)

`inventory_chirps(start_year, end_year)`

Builds a sorted DataFrame of all CHIRPS daily files:

- path
- year
- month
- day

Automatically respects baseline years if none are provided.

`get_reference_grid(file_df, region_geom, clip)`

Loads the first CHIRPS file to determine:

- grid shape
- transform
- CRS

`load_chirps(start_year=None, end_year=None)`

Main entry point.

Returns a metadata dictionary containing everything needed for rainfall metrics and hazard computation.

---

## 4. Usage Example

```python
from ccart.flood.ingest.ingest_chirps import load_chirps

chirps = load_chirps(start_year=1995, end_year=2024)

print(chirps["shape"])
print(chirps["file_df"].head())
```
---

## 5. Notes

- CHIRPS is already at **0.05° resolution**, matching CCART’s FSI rasters.
- Negative rainfall values occasionally appear in CHIRPS; these are set to 0.
- Clipping is fully config‑driven via `paths.yaml`.
- Region boundaries can be any polygon (India, state, basin, etc.).
- This module only ingests CHIRPS.
    Rainfall metrics (Rx2day, P95) are computed in `compute_metrics.py`.
- **Baseline period:**  
    If no years are provided, CCART automatically uses the baseline period from `flood_params.yaml`.