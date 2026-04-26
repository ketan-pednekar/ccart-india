# CCART‑Floods — High‑Level Overview (v1.1)

**Canonical Frequency‑Based Flood Hazard Framework for India (CHIRPS Grid)**

CCART‑Floods is a **scenario‑conditioned flood hazard modelling system** built on:

- CHIRPS rainfall (historical)
- CMIP6 rainfall (future, CHIRPS‑aligned)
- Indo‑Floods susceptibility (FSI)
- A fully reproducible, modular hazard pipeline

It produces:

- **Historical hazard (1995–2024)**
- **Future hazard (2027–2100)**
- **Hazard‑Max layers (historical + future)**
- **CCART Number** — the headline hazard‑change metric

---

## ⭐ Shift in Methodology: From Intensity‑Based to Frequency‑Based Hazard

Earlier CCART prototypes used an intensity‑based hazard:

```
H = FSI * max( Rx2day / P95 , 0 )
```

This approach mixed rainfall magnitude with susceptibility and produced:

- unstable spatial patterns
- interpolation artifacts
- sensitivity to single extreme events

CCART‑Floods v1.1 introduces a **new, stable, frequency‑based hazard definition**:

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
| Interpretation | Hard to explain | “How often do extremes occur?” |
| Hydrological realism | Mixed magnitude + susceptibility | Pure frequency × susceptibility |
| Scenario consistency | Weak | Strong |
| CCART Number | Unstable | Canonical |


This shift is the **core scientific upgrade** in CCART‑Floods v1.1.

---

## 🧩 CCART‑Floods Architecture

CCART‑Floods Pipeline (v1.1)

            ┌──────────────────────┐
            │   CHIRPS Rainfall    │
            │   (Historical)        │
            └─────────┬────────────┘
                      │
                      ▼
            ┌──────────────────────┐
            │     P95 Engine       │
            │  95th percentile     │
            └─────────┬────────────┘
                      │
                      ▼
            ┌──────────────────────┐
            │      Rx2 Engine      │
            │  Rx2max (CHIRPS +    │
            │   CMIP6 SSP370/585)  │
            └─────────┬────────────┘
                      │
                      ▼
            ┌──────────────────────┐
            │   FSI Uplift Engine  │
            │  scenario‑conditioned │
            │     susceptibility    │
            └─────────┬────────────┘
                      │
       ┌──────────────┼────────────────────────┐
       │              │                        │
       ▼              ▼                        ▼
┌────────────┐  ┌──────────────┐       ┌────────────────┐
│ Historical │  │ Future Hazard │       │  Hazard‑Max     │
│ Hazard     │  │ Engine        │       │ (Hist + Future) │
│ (1995–24)  │  │ (2027–2100)   │       └────────┬───────┘
└─────┬──────┘  └──────┬───────┘                │
      │                │                         ▼
      └──────────┬─────┴──────────────┐  ┌───────────────┐
                 ▼                    ▼  │   CCART Number  │
        ┌────────────────┐   ┌──────────────────────────┐ │
        │ Hazard‑Max     │   │ Hazard‑Max (Future)       │ │
        │ (Historical)   │   └──────────────────────────┘ │
        └────────────────┘                                │
                                                           ▼
                                                ┌────────────────────┐
                                                │ CCART_Number =     │
                                                │ Hmax_future /       │
                                                │ Hmax_historical     │
                                                └────────────────────┘


CCART‑Floods consists of six canonical engines, each producing a reproducible scientific asset.

### 1. P95 Engine — Historical Rainfall Threshold

#### Computes the 95th percentile of 2‑day rainfall from CHIRPS.

```
P95 = 95th percentile of ( P_t + P_{t+1} )
```

#### Output:

`p95_chirps_2day.tif`


### 2. Rx2 Engine — Rainfall Extremes

#### Computes:

- CHIRPS Rx2max per year
- CMIP6 Rx2max per year (SSP370, SSP585)
- Period‑max Rx2max for each scenario

```
Rx2max_y = max over t of ( P_t + P_{t+1} )
```

#### Outputs:

- `rx2_chirps/`
- `rx2_ssp370/`
- `rx2_ssp585/`
- `rx2max_ssp370_2027_2100_chirps.tif`
- `rx2max_ssp585_2027_2100_chirps.tif`


### 3. FSI Uplift Engine — Scenario‑Conditioned Susceptibility

```
FSI_uplift = FSI_static * ( Rx2max_future / P95 )
```

#### Outputs:

- `fsi_uplift_ssp370.tif`
- `fsi_uplift_ssp585.tif`


### 4. Dynamic Hazard Engine — Annual Hazard (Future)

For each year:

- Compute 2‑day rolling rainfall
- Count exceedances above P95
- Multiply by FSI uplift

```
H_y_future = N_exceed_y * FSI_uplift
```

#### Outputs:

- `hazard_ssp370_YYYY.tif`
- `hazard_ssp585_YYYY.tif`


### 5. Historical Hazard Engine — Annual Hazard (1995–2024)

Same formula, but using CHIRPS rainfall and static FSI:

```
H_y_historical = N_exceed_y * FSI_static
```

#### Outputs:

`hazard_hist_YYYY.tif`


### 6. Hazard‑Max Engines — Worst‑Case Hazard

Historical Hazard‑Max

```
H_max_historical = max( H_y_historical for all years 1995–2024 )
```

### Output:

`hazard_max_hist_1995_2024.tif`


### 7. Future Hazard‑Max

```
H_max_future = max( H_y_future for all years 2027–2100 )
```

#### Outputs:

- `hazard_max_ssp370_2027_2100.tif`
- `hazard_max_ssp585_2027_2100.tif`

---

## 🔥 CCART Number — Headline Hazard‑Change Metric

```
CCART_Number = H_max_future / H_max_historical
```

### Interpretation:

| CCART Number | Meaning |
|--------------|---------|
| < 1 | Future hazard lower than historical |
| = 1 | No change |
| 1–3 | Moderate increase |
| 3–10 | Strong increase |
| > 10 | Extreme increase |
| capped at 50 | Outlier protection |


**Outputs**:

- `ccart_number_ssp370.tif`
- `ccart_number_ssp585.tif`

---

## 📦 Directory Structure (Canonical)

```
ccart-floods/
    inputs/
        static_fsi.tif
        p95_chirps_2day.tif
        rx2max_ssp370_2027_2100_chirps.tif
        rx2max_ssp585_2027_2100_chirps.tif
    hazard_hist_annual/
    hazard_ssp370_annual/
    hazard_ssp585_annual/
    hazard_hist_max/
    hazard_max/
    ccart_number/
```

## 🧭 Scientific Guarantees

- CCART‑Floods v1.1 ensures:
- CHIRPS‑aligned grid
- Indo‑Floods NaN mask
- Frequency‑based hazard
- Scenario‑conditioned susceptibility
- Reproducible workflows
- Canonical hazard definitions
- Clean, modular engines

---

## 📚 References — IndoFloods (Primary Source)

Kuntla, S. K., & Saharia, M. (2025). *INDOFLOODS: A comprehensive database for flood events in India enhanced with catchment attributes*. Bulletin of the American Meteorological Society, 106(2), E333–E343. https://doi.org/10.1175/BAMS-D-24-0008.1

Kuntla, S. K., & Saharia, M. (2025). *INDOFLOODS: A Comprehensive Database for Flood Events in India Enhanced with Catchment Attributes* [Data set]. Zenodo. https://doi.org/10.5281/zenodo.14584654
