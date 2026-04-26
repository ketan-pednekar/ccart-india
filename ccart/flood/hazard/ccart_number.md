# CCART‑Floods — CCART Number Engine (`ccart_number_engine.py`)

The **CCART Number Engine** computes the **CCART Number**, the core CCART‑Floods metric that compares:

- **Future worst‑case hazard** (2027–2100)

**to**

- **Historical worst‑case hazard** (1995–2024)

for each climate scenario:

- **SSP370**
- **SSP585**

The CCART Number is a **dimensionless hazard‑change index** used for:

- Climate‑risk communication
- Infrastructure resilience design
- Scenario comparison
- CCART‑UK / CCART‑Heat integrations

## 🌐 Definition

The CCART Number is defined as:

```
CCART_Number = H_max_future / H_max_historical
```
Where:

- `H_max_historical` = worst flood‑hazard year in 1995–2024  
- `H_max_future` = worst flood‑hazard year in 2027–2100 (scenario‑conditioned)

---

## 📥 Inputs

| Input File                                   | Description                                      |
|-----------------------------------------------|--------------------------------------------------|
| hazard_max_hist_1995_2024.tif                 | Historical hazard‑max (1995–2024)                |
| hazard_max_ssp370_2027_2100.tif               | Future hazard‑max (SSP370)                       |
| hazard_max_ssp585_2027_2100.tif               | Future hazard‑max (SSP585)                       |
| static_fsi.tif                                | Indo‑Floods domain mask (NaN mask)               |

All rasters must be:

- CHIRPS‑aligned
- float32
- NaN‑masked using Indo‑Floods mask

---

## 📤 Outputs

| Output File               | Description                                   |
|---------------------------|-----------------------------------------------|
| ccart_number_ssp370.tif   | CCART Number for SSP370                       |
| ccart_number_ssp585.tif   | CCART Number for SSP585                       |


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

### 1. Load historical and future hazard‑max rasters

```python
hist_max, profile = load_raster(hist_max_path)
fut370_max, _ = load_raster(fut370_max_path)
fut585_max, _ = load_raster(fut585_max_path)
fsi_arr, _ = load_raster(fsi_path)
```

### 2. Apply Indo‑Floods NaN mask

```python
nan_mask = np.isnan(fsi_arr)
```
Ensures:

- no CCART Number outside India
- no CCART Number in ungauged basins


## 3. Compute CCART Number

Mathematical definition

```
CCART_Number = H_max_future / H_max_historical
```

#### Stability rules (canonical CCART‑Floods v1.1)

- Minimum historical hazard threshold:

```
H_max_historical > 0.01
```

- Maximum allowed ratio:  

```
CCART_Number <= 50
```


#### Implementation

```python
valid = (hist_max > MIN_HIST) & (~nan_mask)
out[valid] = fut_max[valid] / hist_max[valid]
out = np.clip(out, 0, MAX_RATIO)
```
---

## 🧠 Why CCART Number Matters

The CCART Number is the **headline climate‑risk metric** for CCART‑Floods.

It quantifies:

- **How much worse future hazard becomes**
- **Scenario differences (SSP370 vs SSP585)**
- **Spatial patterns of hazard amplification**
- **Resilience design priorities**

**Interpretation**

| CCART Number | Meaning                                           |
|--------------|---------------------------------------------------|
| < 1          | Future hazard lower than historical               |
| = 1          | No change                                         |
| 1–3          | Moderate increase                                 |
| 3–10         | Strong increase                                   |
| > 10         | Extreme increase                                  |
| capped at 50 | Outlier protection threshold                      |

---

## 🧩 Code Summary

### Load rasters

```python
hist_max, profile = load_raster(hist_max_path)
fut370_max, _ = load_raster(fut370_max_path)
fut585_max, _ = load_raster(fut585_max_path)
fsi_arr, _ = load_raster(fsi_path)
```

### Compute CCART Number

```python
ccart_370 = compute_ccart_number(fut370_max, hist_max, nan_mask)
ccart_585 = compute_ccart_number(fut585_max, hist_max, nan_mask)
```

### Save outputs

- `ccart_number_ssp370.tif`
- `ccart_number_ssp585.tif`

---

## ▶️ Usage

Run directly:

```bash
python ccart_number_engine.py
```

Or import:

```python
from ccart.flood.ccart_number.ccart_number_engine import compute_ccart_number
```
---

## 🧭 Notes

- CCART Number is dimensionless.
- It is not a probability or return period.
- It is a hazard amplification index.
- Indo‑Floods NaN mask ensures hydrological realism.
- CCART Number feeds directly into:
    - CCART‑UK
    - CCART‑Heat
    - Resilience design layers