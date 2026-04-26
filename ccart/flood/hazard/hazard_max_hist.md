# CCART‑Floods — Historical Hazard‑Max Engine (`hazard_max_hist_engine.py`)

The **Historical Hazard‑Max Engine** computes the **pixel‑wise maximum historical flood hazard for the period**:

**1995–2024**

using:

- Annual historical hazard rasters (`hazard_hist_YYYY.tif`)
- Indo‑Floods static FSI mask (for NaN domain enforcement)

This produces the **historical worst‑case hazard envelope**, essential for:

- CCART Number Engine
- Historical vs Future hazard comparison
- Resilience design baselines

---

## 🌐 Purpose

For the historical period (1995–2024), the engine:

1. Loads all **annual historical hazard rasters**
2. Computes the **pixel‑wise maximum** across all years
3. Applies the **Indo‑Floods NaN mask**
4. Saves the **historical hazard‑max raster**:
    `hazard_max_hist_1995_2024.tif`

This is the **canonical historical hazard envelope** for CCART‑Floods.

---

## 📥 Inputs

| Input / Directory         | Description                                      |
|---------------------------|--------------------------------------------------|
| `hazard_hist_annual/`     | Annual historical hazard rasters (1995–2024)     |
| `static_fsi.tif`          | Indo‑Floods static susceptibility (NaN mask)     |


Annual hazard rasters must follow:

`hazard_hist_YYYY.tif`

---

## 📤 Outputs

| Output File                         | Description                                      |
|------------------------------------|--------------------------------------------------|
| `hazard_max_hist_1995_2024.tif`    | Pixel‑wise max historical hazard (1995–2024)     |


**Raster characteristics**

| Property     | Value                     |
|--------------|---------------------------|
| Grid         | CHIRPS India 0.05°        |
| CRS          | EPSG:4326                 |
| Data type    | float32                   |
| Nodata       | NaN                       |
| Compression  | LZW                       |
| Alignment    | Exact CHIRPS transform    |

---

## 🔬 Methodology

### 1. Load Indo‑Floods NaN mask

```python
fsi_arr, _ = load_raster(fsi_path)
nan_mask = np.isnan(fsi_arr)
```
The mask ensures:

- no hazard outside India
- no hazard in ungauged basins

### 2. Load all annual historical hazard rasters

```python
files = sorted(annual_dir.glob("hazard_hist_*.tif"))
```

### 3. Compute pixel‑wise maximum

The historical hazard‑max is defined as:

```
H_max_historical = max( H_y_historical for all years 1995–2024 )
```

Where:

```
H_y_historical = N_exceed_y * FSI_static
```

#### Implementation:

```python
max_arr = np.nanmax(np.stack([max_arr, arr]), axis=0)
```

### 4. Apply Indo‑Floods NaN mask

```python
max_arr[nan_mask] = np.nan
```

### 5. Save output

```python
save_raster(out_path, max_arr, profile)
```

---

## 🧠 Why Historical Hazard‑Max Matters

Historical hazard‑max is the baseline worst‑case hazard for CCART‑Floods.

It is used in:

### 1. CCART Number

```
CCART_Number = H_max_future / H_max_historical
```

### 2. Historical vs Future hazard comparison

Shows how hazard frequency changes under climate scenarios.

### 3. Resilience design

Provides the **observed worst‑case hazard envelope** for infrastructure planning.

---

## 🧩 Code Summary

### Load inputs

```python
fsi_arr, _ = load_raster(fsi_path)
files = sorted(annual_dir.glob("hazard_hist_*.tif"))
```

### Compute hazard‑max

```python
max_arr = np.nanmax(np.stack([max_arr, arr]), axis=0)
```

### Save output

`hazard_max_hist_1995_2024.tif`

---

## ▶️ Usage

Run directly:

```bash
python hazard_max_hist_engine.py
```

Or import:

```python
from ccart.flood.hazard_hist_max.hazard_max_hist_engine import compute_hist_max
```
---

## 🧭 Notes

- Historical hazard‑max is **not an average** — it is a **maximum**
- Represents **worst‑case historical hazard** across 30 years
- Indo‑Floods NaN mask ensures hydrological realism
- Feeds directly into:
    - CCART Number
    - Resilience design layers