# CCART‑Floods — FSI Uplift Engine (fsi_uplift_engine.py)

The **FSI Uplift Engine** computes **scenario‑conditioned flood susceptibility** for:

- SSP370
- SSP585

using:

- **Static FSI** (Indo‑Floods susceptibility baseline)
- **P95 (historical 2‑day rainfall threshold)**
- **Rx2max\_future** (future extreme rainfall intensity)

The uplifted FSI layers are core inputs for:

- Dynamic Hazard Engine
- Hazard‑Max Engine
- CCART Number Engine
- Resilience design layers

---

## 🌐 Purpose

The engine computes:


```
FSI_uplift = FSI * (Rx2max_future / P95)
```

for each scenario:

- `fsi_uplift_ssp370.tif`
- `fsi_uplift_ssp585.tif`

This produces **scenario‑conditioned susceptibility**, aligned to the CHIRPS grid.

---

## 📥 Inputs

| Input File                                      | Description                                      |
|-------------------------------------------------|--------------------------------------------------|
| static_fsi.tif                                  | Indo‑Floods static susceptibility (CHIRPS grid)  |
| p95_chirps_2day.tif                              | Historical 2‑day rainfall threshold (P95)        |
| rx2max_ssp370_2027_2100_chirps.tif               | Future extreme rainfall (SSP370)                 |
| rx2max_ssp585_2027_2100_chirps.tif               | Future extreme rainfall (SSP585)                 |

All rasters must be:

- CHIRPS‑aligned
- float32
- NaN‑masked using Indo‑Floods mask

---

## 📤 Outputs

| Output File               | Description                                   |
|---------------------------|-----------------------------------------------|
| fsi_uplift_ssp370.tif     | Scenario‑conditioned susceptibility (SSP370)  |
| fsi_uplift_ssp585.tif     | Scenario‑conditioned susceptibility (SSP585)  |


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

### 1. Load static FSI, P95, and Rx2max_future

All rasters are CHIRPS‑aligned:

```python
fsi_static, profile = load_raster(static_fsi_path)
p95, _ = load_raster(p95_path)
rx2_370, _ = load_raster(rx2_370_path)
rx2_585, _ = load_raster(rx2_585_path)
```

### 2. Compute uplift ratio

The uplift ratio is:

```
R = (Rx2max_future) / P95
```


#### Implementation:

```python
ratio = np.divide(rx2_future, p95, out=np.zeros_like(rx2_future), where=p95 > 0)
```

### 3. Compute FSI uplift

```
FSI_uplift = FSI * R
```

#### Implementation:

```python
uplift = static_fsi * ratio
```

### 4. Apply Indo‑Floods NaN mask

Static FSI contains NaN for:

- ungauged basins
- non‑India pixels

This mask is enforced:

```python
uplift[np.isnan(static_fsi)] = np.nan
```

### 5. Save output

```python
save_raster(out_dir / "fsi_uplift_ssp370.tif", uplift_370, profile)
save_raster(out_dir / "fsi_uplift_ssp585.tif", uplift_585, profile)
```
---

## 🧠 Why FSI Uplift Matters

FSI uplift transforms **static susceptibility** into **scenario‑conditioned susceptibility**.

It is used in:

### 1. Dynamic Hazard Engine

```
H_y_future = N_exceed_y * FSI_uplift
```


### 2. Hazard‑Max Engine

Worst‑case hazard depends on uplifted susceptibility.


### 3. CCART Number

```
CCART_Number = H_max_future / H_max_historical
```


### 4. Resilience design

Uplifted FSI is the **scenario‑aware susceptibility baseline**.

---

🧩 Code Summary

### Load rasters

```python
fsi_static, profile = load_raster(static_fsi_path)
p95, _ = load_raster(p95_path)
rx2_370, _ = load_raster(rx2_370_path)
rx2_585, _ = load_raster(rx2_585_path)
```

### Compute uplift

```python
uplift_370 = compute_fsi_uplift(fsi_static, p95, rx2_370)
uplift_585 = compute_fsi_uplift(fsi_static, p95, rx2_585)
```

### Save outputs

- `fsi_uplift_ssp370.tif`
- `fsi_uplift_ssp585.tif`

---

## ▶️ Usage

Run directly:

```bash
python fsi_uplift_engine.py
```

Or import:

```python
from ccart.flood.fsi_uplift.fsi_uplift_engine import compute_fsi_uplift
```
---

## 🧭 Notes

- FSI uplift is **scenario‑specific**.
- Indo‑Floods NaN mask ensures hydrological realism.
- Uplift is used by all downstream hazard engines.
- This is the **canonical CCART‑Floods susceptibility formulation**.