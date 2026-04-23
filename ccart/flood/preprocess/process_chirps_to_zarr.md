# 📘 CCART‑Floods — CHIRPS → Zarr Conversion (`process_chirps_to_zarr.py`)

***Builds the canonical historical rainfall cube for CCART‑Floods (aligned with CHIRPS + CMIP6 grids)***

# 1. Purpose

`process_chirps_to_zarr.py` converts daily CHIRPS rainfall rasters into a **single, continuous Zarr rainfall cube** aligned with the CHIRPS/FSI reference grid.

This Zarr store becomes the **historical rainfall backbone** for all CCART‑Floods diagnostics and hazard modules.

The output is used for:

- **RX1day / RX2day** rainfall diagnostics
- **Static FSI baseline** (flood susceptibility)
- **Exposure alignment**
- **Historical hazard validation**
- **Climate uplift calculations**
- **CMIP6 comparison and delta‑hazard workflows**

The final dataset is written to:

```python
ccart/outputs/chirps_india/chirps.zarr
```

# 2. What This Module Does

### 2.1 Loads CHIRPS metadata and grid

The script calls:

```python
ch = load_chirps()
```
This provides:

- `file_df` — inventory of all daily CHIRPS rasters
- `years` — sorted list of available years
- `lats`, `lons` — CHIRPS grid coordinates
- `load_day` — callable to load + clean + clip each raster
- `transform`, `crs` — reference grid metadata

This ensures the Zarr cube is **perfectly aligned** with:

- CHIRPS baseline
- FSI rasters
- CMIP6 regridded rainfall
- all downstream hazard modules

### 2.2 Iterates year‑by‑year (memory‑safe)

For each year:

1. All daily rasters are loaded
2. Invalid days are skipped with warnings
3. Cleaned arrays are stacked into a (`time`, `lat`, `lon`) cube
4. A proper daily time coordinate is constructed using `cftime_range`

This avoids loading the entire CHIRPS archive into memory.

### 2.3 Builds a clean xarray Dataset

Each year is converted into:

```python
Dataset({
    "pr": (("time", "lat", "lon"), arr)
})
```
with coordinates:

- `time` — daily timestamps
- `lat`, `lon` — CHIRPS grid centers

and metadata:

- description
- CHIRPS source directory

All arrays are stored as `float32` to reduce disk footprint and maintain consistency with CMIP6 Zarr stores.

### 2.4 Writes to Zarr (append‑safe)

The first year is written with:

```python
mode="w"
```
Subsequent years are appended with:

```python
mode="a", append_dim="time"
```
This produces a **single continuous rainfall cube** from baseline start → baseline end.

---

## 3. Output Structure

The final Zarr store contains:

```python
chirps.zarr/
    pr/          # daily rainfall (mm/day)
    time/        # daily timestamps
    lat/         # CHIRPS latitude centers
    lon/         # CHIRPS longitude centers
    .zmetadata   # consolidated metadata
```
All arrays are:

- `float32`
- cleaned
- clipped (if enabled in `paths.yaml`)
- aligned to the CHIRPS/FSI grid

---

## 4. Usage

**Command‑line**

```bash
python ccart/flood/preprocess/process_chirps_to_zarr.py
```

**Inside Python**

```python
from ccart.flood.preprocess.process_chirps_to_zarr import process_chirps_to_zarr

process_chirps_to_zarr()
```
---

## 5. Notes & Design Choices

- **Zarr is chosen** for:
    - chunked storage
    - fast random access
    - compatibility with CMIP6 Zarr stores
    - cloud‑ready workflows
- **Time coordinate uses** `cftime_range`  
    Ensures compatibility with non‑standard calendars if needed.
-  **Daily rasters are cleaned**  
    Negative, non‑finite, and extreme (>500 mm/day) values are set to 0.
- **Clipping is inherited from** `ingest_chirps.py`  
    If `clip_to_region: true`, the Zarr cube is region‑specific.
-  **This script does not resample or change resolution**  
    CHIRPS remains at native 0.05°.
- **This is an overnight job**  
    CHIRPS ingestion is I/O‑heavy; long runtimes are expected.

---

## 6. Why This Matters

This Zarr cube is the **single source of truth** for historical rainfall in CCART.
Every rainfall‑driven diagnostic — from Rx2day to flood susceptibility — depends on this dataset being:

- clean
- continuous
- reproducible
- grid‑aligned
- scientifically defensible

This script ensures that.

## 7. Output Path

```python
ccart/outputs/chirps_india/chirps.zarr
```
This folder is created automatically if missing.