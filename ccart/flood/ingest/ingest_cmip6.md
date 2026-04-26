# CCART‑Floods — CMIP6 Ingestion Module (`ingest_cmip6.py`)

**CCART‑Floods Framework (v1.1)**
**Multi‑model CMIP6 ingestion aligned to CHIRPS/FSI 0.05° grid**

---

## 🌐 Purpose

The CMIP6 ingestion module provides **scenario‑conditioned future rainfall and temperature inputs** for CCART‑Floods. It is:

- **Multi‑model ready** (ACCESS‑CM2 configured; others pluggable)
- **Scenario‑aware** (e.g., SSP370, SSP585)
- **Grid‑aligned** to the canonical CHIRPS/FSI 0.05° grid
- **Config‑driven** (`paths.yaml`)
- **Unit‑standardized** for hazard engines

It produces year‑wise arrays of:

- `pr` (mm/day)
- `tasmax` (°C)

ready for:

- Dynamic Hazard Engine
- Future Hazard‑Max Engine
- CCART Number (future numerator)

---

## 📥 Inputs

| Input | Description |
|-------|-------------|
| `paths["cmip6"][model][scenario]["pr_dir"]` | Directory containing daily CMIP6 precipitation NetCDFs |
| `paths["cmip6"][model][scenario]["tasmax_dir"]` | Directory containing daily CMIP6 tasmax NetCDFs |
| Model name | e.g., `"ACCESS-CM2"` |
| Scenario | e.g., `"ssp370"`, `"ssp585"` |
| Year range | Optional `start_year`, `end_year` filters |
| CHIRPS grid | Obtained from `chirps_ingest` for regridding |

---

## 📤 Outputs

| Output | Description |
|--------|-------------|
| `shape` | (ny, nx) of CHIRPS reference grid |
| `lats`, `lons` | 1D coordinate arrays from CHIRPS grid |
| `transform`, `crs` | CHIRPS spatial metadata |
| `pr_files` | DataFrame indexed by year with paths to pr NetCDFs |
| `tasmax_files` | Same for tasmax |
| `load_pr_year(path)` | Returns np.ndarray[time, ny, nx] in mm/day |
| `load_tasmax_year(path)` | Returns np.ndarray[time, ny, nx] in °C |

---

## 🔬 Methodology

### 1. Inventory CMIP6 files

**Extract year from filenames**:

```python
m = re.search(r"(\d{4})", fp.name)
```
**Build a year‑indexed DataFrame**:

```python
df = pd.DataFrame(records).set_index("year").sort_index()
```

### 2. Get CHIRPS reference grid

This ensures perfect alignment with CHIRPS/FSI:

```python
lats, lons, transform, crs = _get_chirps_grid(paths)
```
Grid resolution: 0.05° × 0.05°

### 3. Unit conversions

#### Precipitation (pr)

```
pr_mm_per_day = pr_kg_m2_per_s * 86400
```

#### Maximum Temperature (tasmax)

```
tasmax_C = tasmax_K - 273.15
```

### 4. Regridding to CHIRPS grid

### Linear interpolation:

```python
ds[var].interp(lat=lats, lon=lons, method="linear")
```

**Output shape**:

```
(time, ny, nx)
```

### 5. Year‑wise loaders

**Precipitation**

```python
arr = _load_pr_year(path)
```

**Maximum temperature**

```python
arr = _load_tasmax_year(path)
```
---

## ▶️ Usage

**Import**

```python
from ccart.flood.ingest.ingest_cmip6 import load_cmip6
```

**Load ACCESS‑CM2 SSP370 (2027–2100)**

```python
cmip = load_cmip6(
    model="ACCESS-CM2",
    scenario="ssp370",
    start_year=2027,
    end_year=2100
)
```

**Load a single year**

```python
pr_2030 = cmip["load_pr_year"](cmip["pr_files"].loc[2030, "path"])
```
---

## ✅ Notes

- Multi‑model and scenario‑aware ingestion (ACCESS‑CM2 configured)
- Regrids CMIP6 to the canonical CHIRPS/FSI 0.05° grid
- Respects CHIRPS clipping (global or region‑clipped)
- Converts pr and tasmax to CCART‑standard units
- Provides year‑wise loaders for hazard engines
- Fully config‑driven (no hardcoded paths)
- Required by Dynamic Hazard and Future Hazard‑Max engines