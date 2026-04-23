# 📘 CCART‑Floods — CMIP6 Ingestion Module

***Multi‑model, scenario‑aware, CHIRPS‑aligned climate forcing engine***

---

## 1. Overview

`ingest_cmip6.py` provides a **uniform, reproducible ingestion pipeline** for CMIP6 daily climate variables used in CCART‑Floods.
It converts raw CMIP6 NetCDF files into **CHIRPS‑aligned, India‑ready daily arrays** for rainfall and temperature.

This module is:

- **multi‑model ready** (ACCESS‑CM2 configured; others can be added via `paths.yaml`)
- **scenario aware** (ssp126 / ssp245 / ssp370 / ssp585)
- **grid‑aligned** to the CHIRPS/FSI 0.05° reference grid
- **unit‑standardized** (mm/day, °C)
- **region‑consistent** (respects CHIRPS clipping and India mask)

It exposes simple year‑wise loaders for downstream hazard engines (e.g., Rx2day, dynamic flood forcing, heatwave diagnostics).

---

## 2. Scientific Rationale

CCART‑Floods requires **future rainfall and temperature** at the same spatial resolution and grid as CHIRPS, because:

- flood susceptibility (FSI) is built on CHIRPS
- exposure alignment uses CHIRPS grid
- dynamic hazard modules require consistent grids
- climate uplift factors must be computed on a common baseline

CMIP6 models differ in:

- native resolution
- coordinate orientation
- land/sea masks
- temporal coverage
- variable naming conventions

This module standardizes all of them into a **single, reproducible climate forcing format**.

---

## 3. Inputs

### 3.1 Required variables

- `pr` — daily precipitation (kg m⁻² s⁻¹)
- `tasmax` — daily maximum temperature (K)

## 3.2 Directory structure (`paths.yaml`)

```yaml
cmip6:
  ACCESS-CM2:
    ssp370:
      pr_dir: "D:/CMIP6/ACCESS-CM2/ssp370/pr"
      tasmax_dir: "D:/CMIP6/ACCESS-CM2/ssp370/tasmax"
```
Each directory must contain **one NetCDF per year**, with the year in the filename:

```python
pr_day_ACCESS-CM2_ssp370_2030.nc
tasmax_day_ACCESS-CM2_ssp370_2030.nc
```
---

## 4. Outputs

The loader returns a dictionary:

```python
{
  "model": "ACCESS-CM2",
  "scenario": "ssp370",
  "shape": (ny, nx),
  "transform": Affine(...),
  "crs": CRS(...),
  "lats": [...],
  "lons": [...],
  "pr_files": DataFrame(year → path),
  "tasmax_files": DataFrame(year → path),
  "load_pr_year": callable,
  "load_tasmax_year": callable,
}
```
Each loader returns:

```python
np.ndarray of shape (time, ny, nx)
aligned to the CHIRPS/FSI grid.
```
---

## 5. Pipeline Steps

### 5.1 Load CHIRPS reference grid

The module imports `load_chirps()` to extract:

- grid shape
- affine transform
- CRS
- lat/lon centers

This ensures **perfect alignment** between:

- CHIRPS
- FSI
- CMIP6 rainfall
- CMIP6 temperature

## 5.2 Inventory CMIP6 files

`_inventory_nc_files()` scans each directory and extracts the year from filenames.

This creates a clean year‑indexed DataFrame:

```python
year | path
2030 | pr_day_ACCESS-CM2_ssp370_2030.nc
2031 | ...
```
### 5.3 Year filtering

`start_year` and `end_year` allow slicing:

```python
load_cmip6(..., start_year=2027, end_year=2100)
```
### 5.4 Regridding

Regridding is performed in the model’s native units before conversion to ensure numerical stability.

CMIP6 grids differ by model.

We use:

```python
ds[var].interp(lat=lats, lon=lons, method="linear")
```
This ensures:

- monotonic lat ordering
- CHIRPS‑aligned grid
- consistent shape for all models

### 5.5 Unit conversion

**Rainfall**

CMIP6 `pr` is in kg m⁻² s⁻¹.
Convert to mm/day:

```python
pr_mm_day = pr * 86400
```
**Temperature**

CMIP6 `tasmax` is in Kelvin.

Convert to Celsius:

```python
tasmax_C = tasmax - 273.15
```
### 5.6 Return year‑wise loaders

Two callables:

```python
load_pr_year(path)     # → (time, y, x)
load_tasmax_year(path) # → (time, y, x)
```
These are used by:

- Rx2day
- climate uplift
- dynamic flood forcing
- heatwave diagnostics

## 6. Configuration Keys

**paths.yaml**

- `cmip6 → model → scenario → pr_dir`
- `cmip6 → model → scenario → tasmax_dir`

**load_cmip6() arguments**

- `model="ACCESS-CM2"`
- `scenario="ssp370"`
- `start_year=2027`
- `end_year=2100`

---

## 7. Troubleshooting

**❗ No files found**

Check:

- directory paths
- filename patterns
- year in filename
- scenario folder structure

**❗ Variable missing (`pr` not found)**

Some models use different variable names.
Rename or symlink before ingestion.

**❗ Latitude descending**

Handled automatically by:

```python
if ds.lat.values[0] > ds.lat.values[-1]:
    ds = ds.sortby("lat")
```

**❗ Memory pressure**

Use:

```python
ds = ds.load()
ds.close()
```
already implemented.

## 8. Performance Notes

- Regridding is the heaviest step (xarray interpolation).
- ACCESS‑CM2 is relatively coarse → fast.
- High‑resolution models (e.g., EC‑Earth3) will be slower.
- Year‑wise loading avoids memory blow‑up.
- Perfect for overnight runs.

---

## 9. Example Usage

```python
from ccart.flood.ingest.ingest_cmip6 import load_cmip6

cmip = load_cmip6(
    model="ACCESS-CM2",
    scenario="ssp370",
    start_year=2027,
    end_year=2100
)

# Load rainfall for 2030
pr_2030 = cmip["load_pr_year"](cmip["pr_files"].loc[2030, "path"])

# Load temperature for 2050
tas_2050 = cmip["load_tasmax_year"](cmip["tasmax_files"].loc[2050, "path"])
```
---

## 10. CCART Philosophy

This module follows CCART’s core principles:

- **transparent**
- **reproducible**
- **modular**
- **scientifically defensible**
- **India‑ready**
- **climate‑conditioned**

It converts raw CMIP6 outputs into a **policy‑grade climate forcing engine** for flood and heat hazard modelling.