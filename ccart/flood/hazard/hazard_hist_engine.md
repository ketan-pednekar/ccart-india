# CCART‑Floods — Historical Hazard Engine (hazard_hist_engine.py)

The **Historical Hazard Engine** computes **annual historical flood hazard layers** for:

- **1995–2024**

using:

- CHIRPS daily rainfall (India‑clipped)
- 2‑day rolling rainfall exceedance over P95
- Indo‑Floods FSI static mask

These historical hazard layers are essential for:

- CCART Number Engine
- Historical vs Future hazard comparison
- Baseline resilience assessments

---

## 🌐 Purpose

For each year (1995–2024), the engine:

- Loads **CHIRPS daily rainfall**
- Computes **2‑day rolling rainfall**
- Counts **exceedances above P95**
- Multiplies exceedance counts by **FSI static**
- Saves **annual historical hazard rasters**:

`hazard_hist_YYYY.tif`

This produces the **canonical historical hazard baseline** for CCART‑Floods.

---

## 📥 Inputs

| Input File                 | Description                                      |
|----------------------------|--------------------------------------------------|
| pr_hist/                   | CHIRPS daily rainfall (India‑clipped, Zarr)      |
| p95_chirps_2day.tif        | Historical 2‑day rainfall threshold (P95)        |
| static_fsi.tif             | Indo‑Floods static susceptibility mask           |

All rasters must be:

- CHIRPS‑aligned
- float32
- NaN‑masked using Indo‑Floods mask

---

## 📤 Outputs

| Output File              | Description                               |
|--------------------------|-------------------------------------------|
| hazard_hist_YYYY.tif     | Annual historical hazard for year YYYY    |

Raster characteristics

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

### 1. Load CHIRPS rainfall

```python
ds = xr.open_zarr(pr_hist_path)
pr = ds["pr"]
```

### 2. Compute 2‑day rolling rainfall

```python
pr2 = pr.rolling(time=2).sum().isel(time=slice(1, None))
```

Mathematically:

```
P2_t = P_t + P_{t+1}
```

### 3. Count exceedances above P95

For each year:

```python
exceed = (pr2_y > p95_arr).sum(dim="time")
```

Mathematically:

```
N_exceed_y = sum over t of 1( P2_t > P95 )
```

Where:

```
N_exceed_y = frequency of extreme rainfall events in year y
```

### 4. Compute historical hazard

```python
hazard = exceed_arr * fsi_arr
```

Mathematically:

```
H_y_historical = N_exceed_y * FSI_static
```

#### Apply Indo‑Floods NaN mask**

```python
hazard[np.isnan(fsi_arr)] = np.nan
```
Ensures:

- no hazard outside India
- no hazard in ungauged basins

### 5. Save output

```python
save_raster(out_path, hazard, profile)
```

## 🧠 Why Historical Hazard Matters

Historical hazard is the baseline for all CCART‑Floods metrics.

It is used in:

### 1. CCART Number

```
CCART_Number = H_max_future / H_max_historical
```

### 2. Historical vs Future hazard comparison

Shows how hazard frequency changes under climate scenarios.


### 3. Resilience design

Provides the observed hazard baseline for infrastructure planning.

---

## 🧩 Code Summary

### Load inputs

```python
ds = xr.open_zarr(pr_hist_path)
p95_arr, profile = load_raster(p95_path)
fsi_arr, _ = load_raster(fsi_path)
```

### Compute hazard

```python
exceed = (pr2_y > p95_arr).sum(dim="time")
hazard = exceed_arr * fsi_arr
```

### Save outputs

```
hazard_hist_1995.tif

…

hazard_hist_2024.tif
```
---

## ▶️ Usage

Run directly:

```bash
python hazard_hist_engine.py
```

Or import:

```python
from ccart.flood.hazard_hist.hazard_hist_engine import compute_historical_hazard
```
---

## 🧭 Notes

- Historical hazard is **frequency‑based**, not magnitude‑based.
- FSI static ensures hydrological realism.
- Historical hazard feeds directly into:
- CCART Number
- Hazard‑Max (historical)
- Baseline resilience assessments