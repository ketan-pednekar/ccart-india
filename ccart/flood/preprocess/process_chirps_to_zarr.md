# CCART‑Floods — CHIRPS → Zarr Preprocessing (`process_chirps_to_zarr.py`)

**Canonical preprocessing of CHIRPS daily rainfall into a historical Zarr cube**

---

## 🌐 Purpose

This preprocessing script converts **daily CHIRPS rainfall rasters** into a **continuous historical rainfall cube** stored in **Zarr format**, clipped to the India grid and aligned with CMIP6 Zarr stores.

The output Zarr dataset is used for:

- **RX1day / RX2day diagnostics**
- **Static FSI baseline**
- **Exposure alignment**
- **Historical hazard validation**
- **CHIRPS‑aligned grid for CMIP6 regridding**

---

## 📥 Inputs

| Input | Description |
|-------|-------------|
| CHIRPS daily rasters | Year‑wise folders containing daily GeoTIFF rainfall files |
| `paths.yaml` | Provides CHIRPS root directory and clipping configuration |
| `chirps_ingest.load_chirps()` | Supplies file inventory, clipping geometry, canonical grid, and daily loader |
| Date fields (`year`, `month`, `day`) | Extracted from filenames using flexible regex |

Daily CHIRPS filenames may follow any of these patterns:

`YYYY.MM.DD.tif`
`YYYY-MM-DD.tif`
`YYYY_MM_DD.tif`

---

## 📤 Outputs

| Output | Description |
|--------|-------------|
| `ccart/outputs/chirps_india/chirps.zarr` | Continuous daily rainfall Zarr store |
| Variable: `pr` | Daily rainfall (mm/day), float32 |
| Coordinates | `time`, `lat`, `lon` |
| Grid | CHIRPS/FSI canonical 0.05° grid |
| Time span | Determined by available CHIRPS years |
| Metadata | Includes description + CHIRPS source path |

---

## 🔬 Methodology

### 1. Load CHIRPS ingestion metadata

```python
ch = load_chirps()
years = ch["years"]
load_day = ch["load_day"]
lats = ch["lats"]
lons = ch["lons"]
```
This provides:

- File inventory
- Clipping geometry
- Canonical CHIRPS grid
- Callable daily loader

### 2. Loop year‑wise and load all valid days

For each year:

- Read all daily rasters
- Clean invalid values (handled by load_day())
- Collect valid dates
- Stack into a (time, ny, nx) array

```python
arr = np.stack(daily_arrays, axis=0)
```

### 3. Build time coordinate

Uses CF‑compliant cftime:

```python
time = xr.cftime_range(start=valid_dates[0], periods=len(valid_dates), freq="D")
```

### 4. Construct Xarray Dataset

```python
ds = xr.Dataset(
    {"pr": (("time", "lat", "lon"), arr.astype("float32"))},
    coords={"time": time, "lat": lats, "lon": lons},
    attrs={
        "description": "CHIRPS daily rainfall (mm/day), clipped to India",
        "source": chirps_cfg["root"],
    },
)
```

### 5. Write to Zarr (append year‑wise)

- First year → `mode="w"`
- Subsequent years → `mode="a"` with `append_dim="time"`

```python
ds.to_zarr(out_path, mode="a", append_dim="time")
```

## 📐 Unit Conversions

CHIRPS is already in **mm/day**, so no unit conversion is applied here.

For completeness, CCART‑standard formulas:


### Precipitation (pr)

```
pr_mm_per_day = pr_kg_m2_per_s * 86400
```

### Maximum Temperature (tasmax)

```
tasmax_C = tasmax_K - 273.15
```

(Used in CMIP6 preprocessing, not CHIRPS.)

---

## ▶️ Usage

### Run preprocessing

```bash
python process_chirps_to_zarr.py
```

### Output location

`ccart/outputs/chirps_india/chirps.zarr`

---

## 🧭 Notes

- Produces a **continuous, clean, CHIRPS‑aligned** rainfall cube
- Perfectly aligned with CMIP6 Zarr stores for future hazard modelling
- No hardcoded paths — fully config‑driven
- Skips unreadable days with warnings
- Ensures reproducibility for hazard engines and diagnostics