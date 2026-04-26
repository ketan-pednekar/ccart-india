# CCART‑Floods — CMIP6 → Zarr Preprocessing (`process_cmip6_to_zarr.py`)

**Append‑by‑time CMIP6 processor (no preallocation, CHIRPS‑aligned)**

---

## 🌐 Purpose

This preprocessing script converts **daily CMIP6 precipitation** (`pr`) and **maximum temperature** (`tasmax`) into **continuous Zarr stores**, aligned to the **canonical CHIRPS/FSI 0.05° grid**.

It is designed for:

- **Future hazard engines**
- **Hazard‑max engine**
- **CCART Number (future numerator)**
- **Scenario‑conditioned diagnostics**
- **Model‑agnostic ingestion**

The processor:

- Loads CMIP6 daily NetCDFs
- Converts units to CCART standards
- Regrids to CHIRPS grid
- Writes **year‑by‑year** into Zarr
- Never allocates a full (`time`, `lat`, `lon`) array

---

## 📥 Inputs

| Input | Description |
|-------|-------------|
| CMIP6 daily NetCDFs | `pr` and `tasmax` files for each year |
| `paths.yaml` | Provides CMIP6 root directories and processed output paths |
| `load_cmip6()` | Supplies file inventory, grid, CRS, and year‑wise loaders |
| Flood parameters (`future.start`, `future.end`) | Defines year range for processing |
| CHIRPS reference grid | Used for regridding CMIP6 to 0.05° |

Supported variables:

- `pr` — precipitation
- `tasmax` — daily maximum temperature

---

## 📤 Outputs

| Output | Description |
|--------|-------------|
| `.../cmip6_processed/<model>/<scenario>/pr.zarr` | Daily precipitation (mm/day) |
| `.../cmip6_processed/<model>/<scenario>/tasmax.zarr` | Daily maximum temperature (°C) |
| Coordinates | `time`, `lat`, `lon` |
| Grid | CHIRPS/FSI canonical 0.05° grid |
| Metadata | Model, scenario, CRS, units, long_name |
| Time span | Determined by `future.start` → `future.end` |

Each Zarr store is:

- **Append‑safe** (`append_dim="time"`)
- **Chunked by year**
- **Float32**

---

## 🔬 Methodology

### 1. Load CMIP6 ingestion metadata

```python
cmip = load_cmip6(model=model, scenario=scenario,
                  start_year=start_year, end_year=end_year)
```
Provides:

- Year‑indexed file lists
- Year‑wise loaders
- CHIRPS‑aligned grid
- CRS and metadata

### 2. Select variable configuration

```python
if var == "pr":
    units = "mm/day"
    long_name = "Daily precipitation"
elif var == "tasmax":
    units = "degC"
    long_name = "Daily maximum temperature"
```

### 3. Loop year‑wise and load daily arrays

```python
arr = loader(fp)   # (time, ny, nx)
```
- Already regridded to CHIRPS
- Already unit‑converted
- Already clipped (if configured)

### 4. Build time coordinate

```python
time = pd.date_range(f"{yr}-01-01", periods=tlen, freq="D")
```
### 5. Construct Xarray Dataset

```python
ds_year = xr.Dataset(
    {var: (("time", "lat", "lon"), arr.astype("float32"))},
    coords={"time": time, "lat": lats, "lon": lons},
)
```
Metadata added:

- model
- scenario
- CRS
- units
- long_name

### 6. Write to Zarr (append‑by‑time)

```python
ds_year.to_zarr(out_path, mode="a", append_dim="time")
```
- First year uses `mode="w"`
- Subsequent years append along `time`

---

## 📐 Unit Conversions (Markdown‑Ready)

These conversions are applied inside `ingest_cmip6.py`, not in this script — but they are included here for documentation completeness.


### Precipitation (pr)

```
pr_mm_per_day = pr_kg_m2_per_s * 86400
```

### Maximum Temperature (tasmax)

```
tasmax_C = tasmax_K - 273.15
```

---

## ▶️ Usage

### Run preprocessing

```bash
python process_cmip6_to_zarr.py
```

### Output directory structure

```
cmip6_processed/
    ACCESS-CM2/
        ssp370/
            pr.zarr/
            tasmax.zarr/
        ssp585/
            pr.zarr/
            tasmax.zarr/
```

---

## 🧭 Notes

- No full (`time`, `lat`, `lon`) array is ever allocated
- Perfectly aligned with CHIRPS grid
- Fully config‑driven (no hardcoded paths)
- Supports multi‑model, multi‑scenario workflows

