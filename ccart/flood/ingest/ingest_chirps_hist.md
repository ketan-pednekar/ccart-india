# CCART‑Floods — Historical CHIRPS Loader (ingest_chirps_hist.py)

**CCART‑Floods Framework (v1.1)**

**Canonical historical rainfall dataset loader (pr_hist)**

---

## 🌐 Purpose

The **Historical CHIRPS Loader** provides the **`pr_hist`** dataset used across the CCART‑Floods historical hazard subsystem.

This module loads a **pre‑processed CHIRPS India Zarr dataset**, which is:

- Already clipped to India
- Already aligned to the CHIRPS grid
- Already CF‑compliant
- Already validated and cleaned

It produces a **single Xarray Dataset** with variable `pr`, ready for:

- Historical Hazard Engine
- Historical Hazard‑Max Engine
- CCART Number (historical denominator)

---

## 📥 Inputs

The module expects a single Zarr dataset:

`chirps_india_clipped.zarr`

Containing:

The module expects the following inputs:

| Input | Description |
|-------|-------------|
| `chirps_india_clipped.zarr` | Pre‑processed CHIRPS India Zarr dataset |
| `paths["flood"]["inputs"]["pr_hist"]` | Config path to historical rainfall Zarr |
| Variable: `pr` | Daily rainfall (mm/day), CF‑compliant |

---

## 📤 Outputs

The loader returns:

| Output | Description |
|--------|-------------|
| `xarray.Dataset` | Dataset containing variable `pr` |
| `pr` | Daily CHIRPS rainfall aligned to CHIRPS grid |
| Time range | Historical baseline (e.g., 1995–2024) |
| Ready for | Historical hazard, hazard‑max, CCART Number |

Metadata preserved

Used directly by:

- `hazard_hist_engine.py`
- `hazard_hist_max.py`
- `ccart_number.py`

## 🔬 Methodology

### 1. Resolve path from config

```python
paths = load_paths()
project_root = Path(paths["project_root"])
pr_hist_path = project_root / paths["flood"]["inputs"]["pr_hist"]
```

### 2. Load Zarr dataset

```python
ds = xr.open_zarr(pr_hist_path)
```

### 3. Validate variable name

```python
if "pr" not in ds:
    raise ValueError("'pr' variable not found")
```

### 4. Print diagnostics

- Time range
- Shape
- Successful load confirmation

### 5. Return dataset

```python
return ds
```
---

## ▶️ Usage

### Import

```python
from ccart.flood.ingest.ingest_chirps_hist import load_pr_hist
```

### Load dataset

```python
ds = load_pr_hist()
```

### Inspect

```python
print(ds)
print(ds.pr.shape)
print(ds.time.values[0], ds.time.values[-1])
```

## ✅ Notes

- Uses the canonical CHIRPS India Zarr dataset (`pr_hist`)
- Assumes CF‑compliant structure and CHIRPS‑aligned grid
- No cleaning or preprocessing performed at this stage
- Variable name must be `pr` for downstream compatibility
- Time dimension defines the historical hazard period
- Fully config‑driven path resolution (no hardcoded locations)
- Output dataset is consumed directly by historical hazard engines
