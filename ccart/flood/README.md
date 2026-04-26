# CCART‑Floods — Canonical Flood Hazard Framework for India (v1.1)

**Featuring the CCART Number — A New Metric for Scenario‑Conditioned Flood Hazard Change**

*CCART‑Floods v1.1 is a frequency‑based flood hazard engine for India, producing historical hazard, future hazard, hazard‑max layers, and the CCART Number.*

---

## ⭐ CCART Number — The Headline Contribution

The CCART Number is the central scientific contribution of CCART‑Floods.
It quantifies how much flood hazard increases (or decreases) under future climate scenarios relative to historical conditions.

```
CCART_Number = H_max_future / H_max_historical
```
Where:

- `H_max_historical` = worst flood‑hazard year in 1995–2024  
- `H_max_future` = worst flood‑hazard year in 2027–2100 (scenario‑conditioned)


### Interpretation

| CCART Number | Meaning |
|--------------|---------|
| < 1 | Future hazard lower than historical |
| = 1 | No change |
| 1–3 | Moderate increase |
| 3–10 | Strong increase |
| > 10 | Extreme increase |
| capped at 50 | Outlier protection |


### Outputs

- `ccart_number_ssp370.tif`
- `ccart_number_ssp585.tif`

The CCART Number is:

- **frequency‑based**
- **scenario‑conditioned**
- **FSI‑weighted**
- **CHIRPS‑aligned**
- **interpretable**
- **scientifically stable**

It is the **unifying metric** of the entire CCART‑Floods platform.

---

## 🌐 What is CCART‑Floods?

CCART‑Floods is a **canonical, frequency‑based flood hazard modelling system for India**, built on:

- **CHIRPS rainfall** (historical)
- **CMIP6 rainfall** (future, CHIRPS‑aligned)
- **IndoFloods‑derived Flood Susceptibility Index (FSI)**
- **A fully modular hazard pipeline**

It produces:

- Historical hazard (1995–2024)
- Future hazard (2027–2100)
- Hazard‑Max layers
- CCART Number (flagship metric)

---

## 🧠 Why Frequency‑Based Hazard?

Earlier CCART prototypes used intensity‑based hazard:

### Earlier CCART Prototype (Intensity‑Based Hazard)

```
H = FSI * max( Rx2day / P95 , 0 )
```
This produced unstable patterns and sensitivity to single events.

CCART‑Floods v1.1 introduces a **frequency‑based hazard**:

### CCART‑Floods v1.1 (Frequency‑Based Hazard)

```
H_y = N_exceed_y * FSI_uplift
```
Where:

- `N_exceed_y` = number of 2‑day rainfall events exceeding P95  
- `FSI_uplift` = scenario‑conditioned susceptibility


### Why this matters

| Aspect | Old Method (Intensity) | New Method (Frequency) |
|--------|--------------------------|--------------------------|
| Stability | Sensitive to single events | Stable across years |
| Interpretation | Hard to explain | Intuitive (“how often do extremes occur?”) |
| Hydrological realism | Mixed magnitude + susceptibility | Clean frequency × susceptibility |
| Scenario consistency | Weak | Strong |
| CCART Number | Unstable | Canonical |

This shift is the **core scientific upgrade** of CCART‑Floods v1.1. Due to change in methodology, CCART Flood 1.0 and CCART Flood 1.1 results are not comparable. 

---

## 🧩 CCART‑Floods Architecture

`CHIRPS → P95 → Rx2 → FSI → Hazard → Hazard‑Max → CCART Number`

A modular, reproducible pipeline:

### 1. Ingestion Subsystem

    - CHIRPS rasters → Zarr
    - CMIP6 NetCDF → CHIRPS‑aligned Zarr
    - Standardized units (mm/day, °C)

### 2. FSI Subsystem

    - IndoFloods geomorphology + hydrology
    - HYBAS L06 basin‑wise rasterisation
    - Static susceptibility surface (0–1)

### 3. P95 Engine
    - 95th percentile of 2‑day rainfall (CHIRPS)


### 4. Rx2 Engine

    - Annual Rx2max (CHIRPS + CMIP6)
    - Scenario‑max Rx2max (2027–2100)

### 5. FSI Uplift Engine — Scenario‑Conditioned Susceptibility

```
FSI_uplift = FSI * (Rx2max_future / P95)
```

### 6. Hazard Engines

    - Historical hazard (1995–2024)
    - Future hazard (2027–2100)
    - Frequency‑based exceedance counts

### 7. Hazard‑Max Engines

    - Worst‑case hazard (historical + future)

### 8. CCART Number

    - Final hazard‑change metric

---

## 📥 Ingestion Subsystem (Summary)

### CHIRPS Ingestion

- Daily rasters
- Cleans values
- Builds canonical CHIRPS grid
- Provides `load_day()`

### Historical CHIRPS Loader

- Loads CHIRPS Zarr
- No preprocessing
- Direct input to hazard engines

### CMIP6 Ingestion

- Reads daily pr and tasmax
- Converts units
- Regrids to CHIRPS grid
- Provides year‑wise loaders

Outputs are **directly consumable** by all hazard engines.

---

## 🌊 FSI Subsystem (Summary)

### FSI v1.1 — Empirical IndoFloods Susceptibility

- Geomorphology + soils + climate.

### FSI v1.2 — Hydrology‑Enhanced

- HYBAS L06 + upstream area + proxy masking.

### Rasterisation

- Basin‑wise → CHIRPS grid → rescale 0–1.

### Final Output

`ccart_floods_fsi_static_chirps_rescaled.tif`

---

## ⚡ Hazard Engines (Summary)

### Historical Hazard

```
H_y_historical = N_exceed_y * FSI_static
```


### Future Hazard

```
H_y_future = N_exceed_y * FSI_uplift
```

### Hazard‑Max (Historical)

```
H_max_historical = max( H_y_historical for all years 1995–2024 )
```


### Hazard‑Max (Future)

```
H_max_future = max( H_y_future for all years 2027–2100 )
```

---

## 🔥 CCART Number 

### CCART Number (Final Metric)

```
CCART_Number = H_max_future / H_max_historical
```
Where:

- `H_max_historical` = worst flood‑hazard year in 1995–2024  
- `H_max_future` = worst flood‑hazard year in 2027–2100 (scenario‑conditioned)

This is the **primary output** of CCART‑Floods.

## 📦 Canonical Directory Structure

```
ccart-floods/
    ingest/
    fsi/
    hazard/
    outputs/
        hazard_hist_annual/
        hazard_ssp370_annual/
        hazard_ssp585_annual/
        hazard_hist_max/
        hazard_max/
        ccart_number/
```

---

## ⚠️ Known Limitations

### INDOFLOODS Coverage
The public INDOFLOODS dataset excludes Ganga and 
Brahmaputra basin data. As a result:

| State | FSI Coverage | Note |
|-------|-------------|------|
| Bihar | 0.3% | Ganga basin — data pending |
| Uttarakhand | 0.0% | No coverage |
| Punjab | 0.0% | No coverage |
| Haryana | 0.0% | No coverage |
| Uttar Pradesh | 5.2% | Sparse coverage |
| Maharashtra | 42.9% | Western Ghats gap |

Complete INDOFLOODS data available on request 
from authors. FSI v2.0 will incorporate this 
when available.

### Single CMIP6 Model
CCART-Floods uses ACCESS-CM2 (single model).
Multi-model ensemble and Taylor diagram 
validation are planned for v2.0.

### No Hydrodynamic Modelling
FSI is a susceptibility index — not flood depth.
Engineering-grade depth modelling requires 
DEM + drainage network (planned for urban module).

---

## 📚 References

Kuntla, S. K., & Saharia, M. (2025).
INDOFLOODS: A comprehensive database for flood events in India enhanced with catchment attributes.  
Bulletin of the American Meteorological Society, 106(2), E333–E343.
https://doi.org/10.1175/BAMS-D-24-0008.1

Kuntla, S. K., & Saharia, M. (2025).
INDOFLOODS: A Comprehensive Database for Flood Events in India Enhanced with Catchment Attributes [Data set].
Zenodo. https://doi.org/10.5281/zenodo.14584654