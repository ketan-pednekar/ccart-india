# CCART‑Floods — Hazard‑Max Engine (`hazard_max_engine.py`)

The **Hazard‑Max Engine** computes the **pixel‑wise maximum dynamic flood hazard** for each scenario:

- **SSP370** (2027–2100)
- **SSP585** (2027–2100)

It aggregates **annual hazard rasters** into a single **period‑maximum hazard layer**, representing the **worst‑case hazard** expected across the entire future window.

This is a core input for:

- CCART Number Engine
- Resilience design layers
- CCART‑UK / CCART‑Heat future integrations

---

## 🌐 Purpose

For each scenario (SSP370, SSP585), the engine:

1. Loads all **annual hazard rasters**
2. Computes the **pixel‑wise maximum** across all years
3. Applies the **Indo‑Floods NaN mask** (from static FSI)
4. Saves the **period‑max hazard raster**:
    `hazard_max_ssp370_2027_2100.tif`
    `hazard_max_ssp585_2027_2100.tif`

This produces the **canonical resilience design hazard layers**.

---

## 📥 Inputs

| Input / Directory       | Description                                      |
|-------------------------|--------------------------------------------------|
| `hazard_annual/`          | Annual hazard rasters (2027–2100)                |
| `fsi_static.tif`          | Static FSI raster (provides Indo‑Floods NaN mask)|

Annual hazard rasters must follow the naming pattern:

- `hazard_ssp370_YYYY.tif`
- `hazard_ssp585_YYYY.tif`

---

## 📤 Outputs

| Output File                               | Description                                 |
|--------------------------------------------|---------------------------------------------|
| hazard_max_ssp370_2027_2100.tif            | Pixel‑wise max hazard for SSP370            |
| hazard_max_ssp585_2027_2100.tif            | Pixel‑wise max hazard for SSP585            |


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

### 1. Load Indo‑Floods NaN mask

The static FSI raster contains NaN for:

- ungauged basins
- non‑India pixels

This mask is enforced on the final hazard‑max layer.

### 2. Load all annual hazard rasters

For each scenario:

```python
rasters = sorted(hazard_annual_dir.glob(f"hazard_{scenario}_*.tif"))
```

### 3. Compute pixel‑wise maximum

The period‑max hazard is defined as:

```
H_max_future = max of H_y over all years 2027–2100
```

where 

- `H_y = annual hazard`
- `H_max_future = worst-case hazard across the future window`


#### Implementation:

```python

# Initialize with the first annual hazard raster

period_max = first_raster.copy()

# Iterate through remaining rasters and update the pixel‑wise maximum

for arr in remaining_rasters:
    period_max = np.nanmax(np.stack([period_max, arr]), axis=0)
```

### 4. Apply Indo‑Floods NaN mask

```python
period_max[np.isnan(fsi_arr)] = np.nan
```

This ensures:

- no synthetic hazard in ungauged basins
- no hazard outside India

### 5. Save output

```python
save_raster(out_path, period_max, profile)
```

## 🧠 Why Hazard‑Max Matters

Hazard‑Max is the resilience design layer for CCART‑Floods.

It is used in:

### 1. CCART Number

```
CCART_Number = H_max_future / H_max_historical
```

### 2. Infrastructure planning

Hazard‑Max represents the **worst‑case hazard** expected in the future climate.

### 3. Scenario comparison

It allows comparing SSP370 vs SSP585 hazard intensities.

---

## 🧩 Code Summary

### Load FSI mask

```python
fsi_mask = rasterio.open(fsi_path).read(1)
```

### Compute period‑max

```python
compute_period_max("ssp370")
compute_period_max("ssp585")
```

### Output files

- `hazard_max_ssp370_2027_2100.tif`
- `hazard_max_ssp585_2027_2100.tif`

---

## ▶️ Usage

Run directly:

```bash
python hazard_max_engine.py
```

Or import:

```python
from ccart.flood.hazard_max.hazard_max_engine import compute_period_max
```
---

## 🧭 Notes

- Hazard‑Max is **not an average** — it is a **maximum**.
- It represents **worst‑case hazard** across 74 years (2027–2100).
- Indo‑Floods NaN mask ensures hydrological realism.
- Hazard‑Max feeds directly into:
    - CCART Number
    - Resilience design layers