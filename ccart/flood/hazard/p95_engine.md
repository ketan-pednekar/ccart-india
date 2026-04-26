# CCART‑Floods — P95 Engine (`p95_engine.py`, CHIRPS India Grid)

The **P95 Engine** computes the **95th percentile of 2‑day rainfall (P95)** over the full CHIRPS historical period for the **India‑only CHIRPS grid**.

This raster is a **core rainfall‑extreme threshold** used by:

- the **FSI Uplift Engine**
- the **Hazard Engine**
- the **Hazard‑Max Engine**
- CCART‑Number

P95 represents the **historical 2‑day extreme rainfall threshold**, against which future rainfall extremes (Rx2max) are compared.

---

## 🌐 Purpose

The P95 Engine:

- Loads the **CHIRPS India‑only Zarr cube**
- Computes **2‑day rolling rainfall**
- Computes the **95th percentile** across the entire time dimension
- Saves the result as a **CHIRPS‑aligned GeoTIFF**

This produces:

`p95_chirps_2day.tif`

which is the **canonical rainfall threshold layer** for CCART‑Floods.

---

## 📥 Inputs

| Input                 | Description                                   |
|-----------------------|-----------------------------------------------|
| chirps_india_zarr/    | CHIRPS daily rainfall clipped to India (Zarr) |


The Zarr must contain:

- `lat`
- `lon`
- `time`
- rainfall variable (`precip` or first data var)

---

## 📤 Outputs

| Output                  | Description                                      |
|-------------------------|--------------------------------------------------|
| p95_chirps_2day.tif     | 95th percentile of 2‑day rainfall (CHIRPS grid)  |

Raster characteristics:

| Property     | Value                     |
|--------------|---------------------------|
| Grid         | CHIRPS India 0.05°        |
| CRS          | EPSG:4326                 |
| Data type    | float32                   |
| Nodata       | none                      |
| Compression  | LZW                       |
| Alignment    | Exact CHIRPS transform    |


## 🔬 Methodology

### 1. Load CHIRPS India‑only grid

The engine reads the Zarr cube and extracts:

- latitude array
- longitude array
- CHIRPS grid transform (via from_bounds)

This ensures **perfect alignment** with all other CCART rasters.

### 2. Compute 2‑day rolling rainfall

```python
r2 = da.rolling(time=2).sum()
```

This produces a daily series of 2‑day accumulated rainfall.

### 3. Compute the 95th percentile

```python
p95 = r2.quantile(0.95, dim="time")
```

This gives the **historical extreme rainfall threshold** for each pixel.

### 4. Save as CHIRPS‑aligned GeoTIFF

The output is written with:

- float32
- EPSG:4326
- CHIRPS transform
- LZW compression

---

## 🧠 Why P95 Matters

P95 is the **baseline rainfall extreme threshold** for CCART‑Floods.

It anchors all rainfall‑driven hazard computations.

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

**Without P95, the entire hazard subsystem has no baseline for rainfall extremes.**

P95 is *the anchor* that makes all future rainfall anomalies and hazard ratios meaningful.

---

## 🧩 Code Summary

### Load CHIRPS grid

```python
lats, lons, transform = load_chirps_grid()
```

### Compute P95

```python
compute_p95(transform)
```

### Save output

`p95_chirps_2day.tif`

---

## ▶️ Usage

Run directly:

```bash
python p95_engine.py
```
Or import:

```python
from ccart.flood.p95.p95_engine import compute_p95
```
---

## 🧭 Notes

- P95 is computed **once** for the entire CHIRPS period (1981–present).
- It is **static** and reused across all hazard workflows.
- Output is **CHIRPS‑aligned**, ensuring compatibility with:
    - FSI uplift
    - rainfall anomalies
    - hazard rasters
    - CCART Number