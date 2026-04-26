# CCART‑Floods — Rx2 Engine (`rx2_engine.py`, CHIRPS India Grid)

The **Rx2 Engine** computes **2‑day maximum rainfall (Rx2max)** for:

- **CHIRPS historical period** (per year)
- **CMIP6 SSP370** (per year, already on CHIRPS grid)
- **CMIP6 SSP585** (per year, already on CHIRPS grid)

It also computes **period‑max Rx2max** for each scenario:

- `rx2max_ssp370_2027_2100_chirps.tif`
-  `rx2max_ssp585_2027_2100_chirps.tif`

These are core rainfall‑extreme inputs for:

- **FSI Uplift Engine**
- **Hazard Engine**
- **Hazard‑Max Engine**
- **CCART Number**

## 🌐 Purpose

The Rx2 Engine:

1. Loads the **CHIRPS India‑only Zarr cube**
2. Computes **CHIRPS Rx2max per year**
3. Computes **CMIP6 Rx2max per year** (SSP370, SSP585)
4. Computes **period‑max Rx2max** for each scenario
5. Saves all outputs as **CHIRPS‑aligned GeoTIFFs**

This produces the canonical rainfall‑extreme layers used throughout CCART‑Floods.

---

## 📥 Inputs

| Input                 | Description                                   |
|-----------------------|-----------------------------------------------|
| chirps_india_zarr/    | CHIRPS daily rainfall clipped to India (Zarr) |
| pr_370/               | CMIP6 SSP370 daily rainfall (CHIRPS grid)     |
| pr_585/               | CMIP6 SSP585 daily rainfall (CHIRPS grid)     |



All Zarr cubes must contain:

- `lat`
- `lon`
- `time`
- rainfall variable (`precip` for CHIRPS, `pr` for CMIP6)

---

## 📤 Outputs

### Per‑year Rx2max

| Directory        | Description                     |
|------------------|---------------------------------|
| rx2_chirps/      | CHIRPS Rx2max per year          |
| rx2_ssp370/      | SSP370 Rx2max per year          |
| rx2_ssp585/      | SSP585 Rx2max per year          |


Each file is named:

`rx2max_<year>.tif`

### Period‑max Rx2max

| Output                                      | Description                                |
|---------------------------------------------|--------------------------------------------|
| `rx2max_ssp370_2027_2100_chirps.tif`          | Max Rx2max across all SSP370 years         |
| `rx2max_ssp585_2027_2100_chirps.tif`          | Max Rx2max across all SSP585 years         |


### Raster characteristics

| Property     | Value                     |
|--------------|---------------------------|
| Grid         | CHIRPS India 0.05°        |
| CRS          | EPSG:4326                 |
| Data type    | float32                   |
| Nodata       | none                      |
| Compression  | LZW                       |
| Alignment    | Exact CHIRPS transform    |

---

## 🔬 Methodology

### 1. Load CHIRPS India‑only grid

Extract:

- latitude array
- longitude array
- CHIRPS grid transform (via `from_bounds`)

Ensures perfect alignment with all CCART rasters.

### 2. Compute Rx2max per year

For each year:

```python
rx2 = da_y.rolling(time=2).sum().max(dim="time")
```
This computes:

```
Rx2max_y = max over t of ( P_t + P_{t+1} )
```

where `P_t` is daily rainfall.

### 3. Compute CMIP6 Rx2max per year

Same method, but using CMIP6 rainfall (`pr`) already on CHIRPS grid.

### 4. Compute period‑max Rx2max

For each scenario:

```python
period_max = np.max(arrays, axis=0)
```
This computes:

`Rx2max_future = max of Rx2max_y over all years 2027–2100`

---

## 🧠 Why Rx2max Matters

Rx2max is the **core rainfall‑extreme metric** used throughout CCART‑Floods.

It is used in:

### 1. FSI Uplift Engine

```
FSI_uplift = FSI * (Rx2max_future / P95)
```

### 2. Hazard Engine

```
H_y_future = N_exceed_y * FSI_uplift
```

### 3. Hazard‑Max Engine

```
H_max_future = max( H_y_future for all years 2027–2100 )
```

### 4. CCART Number

```
CCART_Number = H_max_future / H_max_historical
```

---

## 🧩 Code Summary

### Load CHIRPS grid

```python
lats, lons, transform = load_chirps_grid()
```

### Compute Rx2max per year

```python
compute_rx2_per_year_from_zarr(...)
```

### Compute period‑max

```python
compute_period_max(...)
```

### Outputs

- `rx2max_<year>.tif`
- `rx2max_ssp370_2027_2100_chirps.tif`
- `rx2max_ssp585_2027_2100_chirps.tif`

---

## ▶️ Usage

Run directly:

```bash
python rx2_engine.py
```
Or import:

```python
from ccart.flood.rx2.rx2_engine import compute_rx2_per_year_from_zarr
```
---

## 🧭 Notes

- CMIP6 rainfall is **already on CHIRPS grid**, so no regridding is needed.
- Rx2max is computed **per year**, then aggregated.
- Period‑max is used for:
    - FSI uplift
    - hazard anomalies
    - hazard‑max
    - CCART Number