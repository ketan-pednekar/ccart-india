# CCART‑Floods — CHIRPS Ingestion Module (`chirps_ingest.py`)

**CCART‑Floods Framework (v2)**  

**Canonical ingestion of CHIRPS daily rainfall rasters**

---

## 🌐 Purpose

The **CHIRPS Ingestion Module** loads daily CHIRPS rainfall rasters and prepares the **canonical reference grid** used across all CCART rainfall and hazard subsystems.

It supports:

- **Global mode** — no clipping
- **Regional mode** — clip to India or any polygon
- **Config‑driven ingestion** — paths + clipping rules from YAML
- **Cleaned rainfall arrays** — invalid values removed
- **Reference grid extraction** — shape, transform, CRS
- **Callable loader** — used by hazard engines

This module is the foundation for:

- P95 Engine
- Rx2 Engine
- Historical Hazard Engine
- Dynamic Hazard Engine

---

## 📥 Inputs

| Input | Description |
|-------|-------------|
| `CHIRPS_DIR` | Directory containing CHIRPS daily rasters (year‑wise folders) |
| `region_boundary` | Optional polygon for clipping (e.g., India) |
| `baseline.start`, `baseline.end` | Year range for ingestion |
| `clip_to_region` | Boolean flag controlling clipping |


Daily CHIRPS files must follow a flexible pattern:

```
YYYY.MM.DD.tif
YYYY-MM-DD.tif
YYYY_MM_DD.tif
```

---

## 📤 Outputs

The ingestion function returns a dictionary:

| Key | Description |
|------|-------------|
| `file_df` | Inventory of daily CHIRPS files |
| `years` | Sorted list of years found |
| `shape` | Raster grid shape (ny, nx) |
| `lats`, `lons` | Coordinate arrays |
| `transform` | Affine transform |
| `crs` | EPSG:4326 |
| `region_geom` | Clipping geometry (if enabled) |
| `clip` | Boolean flag |
| `load_day` | Callable to load a single day |

---

## 🔬 Methodology

### 1. Inventory CHIRPS files

Extracts year, month, day using a flexible regex:

```python
DATE_RE = re.compile(r"(\d{4})[.\-_](\d{1,2})[.\-_](\d{1,2})")
```
Builds a sorted DataFrame:

```python
file_df = (
    pd.DataFrame(records)
    .sort_values(["year", "month", "day"])
)
```

### 2. Load a single CHIRPS day

If clipping is enabled:

```python
out, tf = rasterio.mask.mask(src, region_geom, crop=True, filled=True, nodata=np.nan)
arr = out[0].astype("float32")
```

Else:

```python
arr = src.read(1).astype("float32")
tf = src.transform
```

**Cleaning invalid values:**

```python
arr = np.where(
    (arr < 0) | (arr > 500) | (~np.isfinite(arr)),
    0.0,
    arr
)
```

### 3. Establish reference grid

Uses the first CHIRPS file:

```python
shape, transform, crs = get_reference_grid(file_df, region_geom, clip=CLIP)
```

4. Build coordinate arrays

```python
lats = np.array([transform.f + transform.e * i for i in range(ny)])
lons = np.array([transform.c + transform.a * j for j in range(nx)])
```

## ▶️ Usage

### Import

```python
from ccart.flood.chirps_ingest import load_chirps
```

### Load CHIRPS for baseline period

```python
meta = load_chirps()
```

### Load a single day

```python
arr = meta["load_day"](meta["file_df"].iloc[0]["path"])
```
---

🧭 Notes

- CHIRPS ingestion is **config‑driven** — no hardcoded paths
- Supports **global** and **regional** workflows
- Produces the **canonical CHIRPS grid** used across CCART
- Cleans invalid rainfall values for hazard stability
- Fully compatible with all downstream engines