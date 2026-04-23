# 📘 CCART‑Floods — CMIP6 → Zarr Processor (process_cmip6_to_zarr.py)

***Append‑by‑time, memory‑safe CMIP6 processing aligned to the CHIRPS/FSI reference grid***

## 1. Purpose

`process_cmip6_to_zarr.py` converts CMIP6 daily climate variables into **continuous, append‑safe Zarr stores** aligned with the CHIRPS/FSI reference grid.

This module:

- loads CMIP6 daily precipitation (`pr`) and maximum temperature (`tasmax`)
- regrids each year to the CHIRPS reference grid (global or clipped)
- converts units to CCART standards (mm/day, °C)
- writes each year into a Zarr store using append_dim="time"
- **never allocates a full (time, lat, lon) array in memory**

These Zarr stores form the **future climate forcing backbone** for CCART‑Floods.

## 2. What This Module Produces

For each model + scenario + variable, the script generates:

```python
<processed_dir>/<model>/<scenario>/<var>.zarr
```
Example:

```python
ccart/outputs/cmip6_processed/ACCESS-CM2/ssp370/pr.zarr
ccart/outputs/cmip6_processed/ACCESS-CM2/ssp370/tasmax.zarr
```
These Zarr cubes are used for:

- **Rx2day uplift calculations**
- **future flood hazard generation**
- **delta‑hazard workflows**
- **exposure conditioning**
- **heatwave diagnostics**
- **model‑scenario comparisons**

## 3. What This Module Does

### 3.1 Loads CMIP6 metadata and grid

The script calls:

```python
cmip = load_cmip6(model, scenario, start_year, end_year)
```
This provides:

- `pr_files`, `tasmax_files` — year‑indexed file inventories
- `load_pr_year`, `load_tasmax_year` — year‑wise loaders
- `lats`, `lons` — CHIRPS‑aligned grid
- `shape` — (ny, nx)
- `crs` — always `EPSG:4326`

The CMIP6 data is **already regridded** to CHIRPS resolution by `ingest_cmip6.py`.

### 3.2 Processes one variable at a time

For each variable (`pr`, `tasmax`):

- selects the correct loader
- applies unit conversion
- loads one year at a time
- constructs a daily time coordinate
- builds a clean xarray Dataset

This ensures **low memory usage** and **clean separation** of variables.

## 3.3 Builds a clean xarray Dataset per year

Each year becomes:

```python
Dataset({
    var: (("time", "lat", "lon"), arr)
})
```

with coordinates:

- `time` — daily timestamps
- `lat`, `lon` — CHIRPS grid centers

and metadata:

- model
- scenario
- CRS
- units
- long_name

All arrays are stored as `float32` for efficiency.

Each year is chunked along the time dimension to optimize sequential reads during hazard computation.

### 3.4 Writes to Zarr (append‑safe)

The first year is written with:

```python
mode="w"
```
Subsequent years are appended with:

```python
mode="a", append_dim="time"
```
This produces a **continuous, multi‑decadal climate forcing cube** without ever holding the full dataset in memory.

---

**4. Output Structure**

Each Zarr store contains:

```python
<var>.zarr/
    <var>/        # daily values (mm/day or °C)
    time/         # daily timestamps
    lat/          # CHIRPS latitude centers
    lon/          # CHIRPS longitude centers
    .zmetadata    # consolidated metadata
```

All arrays are:

- `float32`
- CHIRPS‑aligned
- model‑ and scenario‑specific
- time‑continuous

---

## 5. Usage

**Command‑line**

```bash
python ccart/flood/preprocess/process_cmip6_to_zarr.py
```

**Inside Python**

```python
from ccart.flood.preprocess.process_cmip6_to_zarr import process_variable_to_zarr

process_variable_to_zarr("ACCESS-CM2", "ssp370", "pr")
process_variable_to_zarr("ACCESS-CM2", "ssp370", "tasmax")
```

The `main()` function processes:

- model: `ACCESS‑CM2`
- scenarios: `ssp370`, `ssp585`
- variables: `pr`, `tasmax`

---

## 6. Notes & Design Choices

- **Append‑by‑time**  
    Avoids allocating large arrays; ideal for multi‑decadal CMIP6 datasets.
- **Year‑wise loading**  
    Prevents memory blow‑up and allows overnight processing.
- **CHIRPS‑aligned grid**  
    Ensures perfect compatibility with CHIRPS, FSI, and hazard modules.
- **Unit conversions**
    - `pr`: kg m⁻² s⁻¹ → mm/day
    - `tasmax`: K → °C
- **Chunking**  
    Each year is chunked along time for fast sequential reads.
- **CRS is always EPSG:4326**  
    CMIP6 is regridded to CHIRPS’ geographic coordinate system.
- **No resampling here**  
    All regridding is handled upstream in ingest_cmip6.py.

---

## 7. Why This Matters

These Zarr cubes are the **future climate engine** of CCART‑Floods.

Every future hazard calculation — rainfall uplift, dynamic flood forcing, heatwave diagnostics, delta‑hazard maps — depends on these datasets being:

- clean
- continuous
- reproducible
- grid‑aligned
- scientifically defensible

This script ensures that CCART’s CMIP6 processing is **transparent, modular, and policy‑grade**.