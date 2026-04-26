# CCART‑Floods — Dynamic Flood Hazard Engine (hazard_engine.py)

The **Dynamic Flood Hazard Engine** computes **annual flood hazard rasters** for:

- **SSP370** (2027–2100)
- **SSP585** (2027–2100)

using:

- **CMIP6 daily rainfall** (CHIRPS‑aligned)
- **P95 (2‑day rainfall threshold)**
- **FSI uplift** (scenario‑specific)

This is the **core hazard computation** in CCART‑Floods v1.1.

---

## 🌐 Purpose

For each scenario (SSP370, SSP585), the engine:

1. Loads **daily rainfall** (CHIRPS‑aligned CMIP6)
2. Computes **2‑day rolling rainfall**
3. **Counts exceedances above P95**
4. Multiplies exceedance counts by **FSI uplift**
5. Saves **annual hazard rasters**:
    `hazard_ssp370_YYYY.tif`
    `hazard_ssp585_YYYY.tif`

This produces the **canonical hazard fields** used by:

- Hazard‑Max Engine
- CCART Number Engine
- CCART‑UK / CCART‑Heat future integrations

---

## 📥 Inputs

| Input                     | Description                                      |
|---------------------------|--------------------------------------------------|
| `pr_370/`                   | CMIP6 SSP370 daily rainfall (CHIRPS‑aligned)     |
| `pr_585/`                   | CMIP6 SSP585 daily rainfall (CHIRPS‑aligned)     |
| `p95_chirps_2day.tif`       | Historical 2‑day rainfall threshold (P95)        |
| `fsi_uplift_ssp370.tif`     | Scenario‑conditioned susceptibility (SSP370)     |
| `fsi_uplift_ssp585.tif`     | Scenario‑conditioned susceptibility (SSP585)     |


All rainfall inputs must contain:

- `lat`
- `lon`
- `time`
- rainfall variable `pr` (mm/day)

## 📤 Outputs

### Annual hazard rasters

| Output Pattern              | Description                     |
|-----------------------------|---------------------------------|
| hazard_ssp370_YYYY.tif      | Annual hazard for SSP370        |
| hazard_ssp585_YYYY.tif      | Annual hazard for SSP585        |


### Raster characteristics

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

### 1. Load P95 and FSI uplift

- `p95_arr` → historical 2‑day rainfall threshold
- `fsi_uplift` → scenario‑conditioned susceptibility

Both are CHIRPS‑aligned rasters.

### 2. Load CMIP6 rainfall

Rainfall is already on CHIRPS grid:

```python
ds = xr.open_zarr(pr_370_zarr)
pr = ds["pr"]
```

### 3. Compute 2‑day rolling rainfall

```python
pr2 = pr.rolling(time=2).sum().isel(time=slice(1, None))
```

This computes:

```
P2_t = P_t + P_{t+1}
```

### 4. Count exceedances above P95

For each year:

```python
exceed = (pr2_y > p95_arr).sum(dim="time")
```

Mathematically:

```
N_exceed_y = sum over t of 1( P2_t > P95 )
```

### 5. Compute hazard

Hazard is defined as:

```
H_y = N_exceed_y * FSI_uplift
```
Where:

- `N_exceed_y` = number of 2‑day rainfall events exceeding P95  
- `FSI_uplift` = scenario‑conditioned susceptibility

This is the canonical CCART‑Floods hazard definition.

---

## 🧠 Why This Hazard Definition Matters

Earlier CCART prototypes used:

```
H = FSI * max( Rx2day / P95 , 0 )
```

This mixed magnitude + susceptibility and produced unstable fields.

CCART‑Floods v1.1 introduces a stable, frequency‑based hazard:

```
H_y = N_exceed_y * FSI_uplift
```
This new formulation:

- emphasizes frequency of extreme rainfall
- removes interpolation artifacts
- preserves Indo‑Floods empirical mask
- produces scenario‑consistent hazard fields
- is the first citable CCART‑Floods hazard definition

---

## 🧩 Code Summary

### Load inputs

```python
p95_arr, profile = load_raster(p95_path)
fsi_uplift_370, _ = load_raster(fsi_uplift_370_path)
fsi_uplift_585, _ = load_raster(fsi_uplift_585_path)
```

### Load rainfall

```python
ds_370 = load_pr_dataset(pr_370_zarr)
ds_585 = load_pr_dataset(pr_585_zarr)
```

### Compute hazard

```python
compute_hazard_for_scenario(...)
```

### Output files

- `hazard_ssp370_YYYY.tif`
- `hazard_ssp585_YYYY.tif`

---

## ▶️ Usage

Run directly:

```bash
python hazard_engine.py
```

Or import:

```python
from ccart.flood.hazard.hazard_engine import compute_hazard_for_scenario
```

---

## 🧭 Notes

- Hazard is **annual**, not daily.
- Hazard is **frequency‑based**, not magnitude‑based.
- FSI uplift already contains Indo‑Floods NaN mask.
- P95, uplift, and rainfall must be **CHIRPS‑aligned**.
- Hazard feeds directly into:
- Hazard‑Max Engine
- CCART Number Engine