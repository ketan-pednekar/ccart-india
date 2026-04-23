# CCART‑Floods — Module‑Level README (beta - being updated)

***A modular, reproducible, climate‑conditioned flood hazard engine for India***

***Climate-conditioned flood hazard module — CHIRPS daily Rx2day baseline (1995–2024), FSI v1.2 (INDOFLOODS + HydroBASINS), CMIP6 SSP3-7.0 and SSP5-8.5 projections to 2100.***

---

## 🌧️ Overview

**CCART‑Floods** is a fully modular, open‑source flood hazard modelling framework.

It integrates:

- CHIRPS rainfall extremes
- CMIP6 climate projections
- FSI (Flood Susceptibility Index)
- A transparent hazard formulation

to produce **climate‑conditioned flood hazard** for both historical and future periods.

The system is designed to be:

- **Scientifically transparent** — explicit formulas, assumptions, and data sources
- **Modular** — ingestion, metrics, susceptibility, and hazard are cleanly separated
- **Reproducible** — deterministic outputs, no hidden steps
- **Memory‑safe** — processes multi‑decadal data one year at a time
- **CHIRPS‑aligned** — all rasters share the same grid, CRS, and resolution

CCART‑Floods is built as a research‑grade engine, not a dashboard.

---

## Known FSI Limitations

### INDOFLOODS Public Dataset Coverage
The public INDOFLOODS dataset (Zenodo) contains 155 gauges. 

Coverage is severely limited in:

| State | Coverage | Reason |
|-------|----------|--------|
| Bihar | 0.3% | Only 3 Ganga basin gauges |
| Uttarakhand | 0.0% | No gauges |
| Punjab | 0.0% | No gauges |
| Haryana | 0.0% | No gauges |
| UP | 5.2% | Sparse coverage |

Complete INDOFLOODS data including Ganga and Brahmaputra basins is available on request from the authors. FSI v2.0 will incorporate this data when available.


## 🧱 Architecture Overview

CCART‑Floods consists of **three scientific subsystems**, each independently modular:

```python
CHIRPS Subsystem → Rainfall Metrics (Rx2day, P95)
FSI Subsystem    → Structural Susceptibility (FSI v1.2)
Hazard Subsystem → Climate‑Conditioned Flood Hazard
```
Each subsystem has its own ingestion, processing, utilities, and documentation.

---

## 📦 Subsystems

**1. CHIRPS Subsystem — Rainfall Ingestion & Metrics**

**Purpose**

Transforms raw CHIRPS daily rainfall into extreme‑rainfall metrics used by the hazard engine.

**Components**

| File                | Purpose                                                       |
|---------------------|----------------------------------------------------------------|
| `ingest_chirps.py`  | Inventory, load, clip, and clean CHIRPS daily rainfall        |
| `compute_metrics.py`| Compute Rx2day (annual max 2‑day rainfall) and P95 baseline   |
| `raster_utils.py`   | Reprojection, masking, alignment utilities                    |
| `*.md`              | Documentation for each module                                 |

**Outputs**

- `rx2day_YYYY.npy` — annual maximum 2‑day rainfall
- `p95_rx2day.npy` — 95th percentile baseline (1995–2024)
- CHIRPS metadata (shape, transform, CRS, India boundary)

**Scientific Notes**

- CHIRPS defines the **master grid** for the entire flood module
- All computations are **memory‑safe** (one year at a time)
- P95 provides the **baseline extreme rainfall threshold**


**2. FSI Subsystem — Flood Susceptibility Index**

**Purpose**

Transforms INDOFLOODS geomorphology + HydroBASINS hydrology into a national‑scale susceptibility raster aligned with CHIRPS.

**Components**

| File                     | Purpose                                                             |
|--------------------------|----------------------------------------------------------------------|
| `build_fsi_v1_1.py`      | Compute FSI v1.1 from geomorphology + soils                         |
| `build_fsi_v1_2.py`      | Enhance FSI v1.1 using HydroBASINS hydrological structure           |
| `rasterise_fsi.py`       | Rasterise, clean, and rescale FSI v1.2 to CHIRPS grid               |
| `export_fsi_raster.py`   | Export final FSI raster to GeoTIFF with correct metadata            |
| `utils_fsi.py`           | Normalisation, soil encoding, spatial joins, raster masking         |
| `*.md`                   | Documentation for each module                                       |

**Scientific Notes**

- **FSI v1.1** — empirical susceptibility (terrain + soils)
- **FSI v1.2** — adds hydrological structure (UP_AREA, SUB_AREA, ORDER)
- Proxy basins (no gauges) are masked to **NaN**
- Rasterisation uses no **interpolation**
- Final FSI raster is 0–1, CHIRPS‑aligned, float32
- All loops are resume‑friendly — missing years can be recomputed without rerunning the full pipeline.

**3. Hazard Subsystem — Climate‑Conditioned Flood Hazard**

**Purpose**

Combines rainfall extremes with susceptibility to compute flood hazard for historical and future periods.

**Hazard Formula**

\[
H = \text{FSI} \times \max\left(\frac{\text{Rx2day}}{\text{P95}}, 0\right)
\]

This expresses how rainfall extremes amplify underlying terrain‑driven susceptibility.

**Components**

| File                 | Purpose                                                             |
|----------------------|----------------------------------------------------------------------|
| `ingest_fsi.py`      | Load + reproject FSI raster to CHIRPS grid                          |
| `hazard_engine.py`   | Core hazard computation + historical + future loops                 |
| `hazard_utils.py`    | Shared helper functions (safe division, clipping, normalisation)    |
| `*.md`               | Documentation for each module                                       |

**Outputs**

- `hazard_hist_YYYY.npy` — historical hazard (1995–2024)
- `hazard_fut_YYYY.npy` — future hazard (2027–2100, CMIP6 SSP3‑7.0)

**Scientific Notes**

- Hazard is **pixel‑wise** and fully CHIRPS‑aligned
- CMIP6 rainfall is reprojected to CHIRPS using bilinear resampling
- All loops are resume‑friendly and memory‑safe

---

## 🚀 Full Pipeline Orchestration

A complete end‑to‑end workflow is provided in:

```python
ccart/flood/example/run_flood_pipeline.py
```
This script runs the entire CCART‑Floods pipeline:

- CHIRPS ingestion + Rx2day + P95
- FSI v1.1 + FSI v1.2
- FSI rasterisation + export
- Historical + future hazard computation


## 🔄 End‑to‑End Workflow

```python
1. CHIRPS ingestion
2. Compute Rx2day for all years
3. Compute P95 baseline
4. Build FSI v1.1 (geomorphology + soils)
5. Build FSI v1.2 (add hydrology + mask proxies)
6. Rasterise + clean + rescale FSI
7. Export final FSI raster
8. Ingest FSI for hazard engine
9. Compute historical hazard (1995–2024)
10. Compute future hazard (2027–2100)
```

Each stage is modular, documented, and reproducible.

## 📁 Directory Structure

```python
ccart/flood/
│
├── README.md                 # Module‑level documentation (this file)
├── __init__.py               # Flood module namespace
│
├── chirps/                   # CHIRPS ingestion + rainfall metrics
│   ├── ingest_chirps.py
│   ├── compute_metrics.py
│   ├── raster_utils.py
│   ├── ingest_chirps.md
│   ├── compute_metrics.md
│   ├── raster_utils.md
│   └── __pycache__/
│
├── fsi/                      # Flood Susceptibility Index subsystem
│   ├── build_fsi_v1_1.py
│   ├── build_fsi_v1_2.py
│   ├── rasterise_fsi.py
│   ├── export_fsi_raster.py
│   ├── utils_fsi.py
│   ├── build_fsi_v1_1.md
│   ├── build_fsi_v1_2.md
│   ├── rasterise_fsi.md
│   ├── export_fsi_raster.md
│   ├── utils_fsi.md
│   └── __pycache__/
│
├── hazard/                   # Hazard computation subsystem
│   ├── ingest_fsi.py
│   ├── hazard_engine.py
│   ├── hazard_utils.py
│   ├── ingest_fsi.md
│   ├── hazard_engine.md
│   ├── hazard_utils.md
│   └── __pycache__/
│
├── outputs/                  # Generated outputs (Rx2day, P95, FSI raster, hazard)
│
├── example/                  # Quickstart scripts, demo notebooks (to be added)
│
├── config.py                 # Paths + constants
└── config.md                 # Documentation for config
```
---

## 🧪 Scientific Principles

CCART‑Floods is built on four core principles:

**1. Empirical honesty**

- No interpolation of susceptibility
- No fabricated values in proxy basins
- No smoothing across hydrological boundaries

**2. Reproducibility**

- Deterministic outputs
- `.npy` storage for all intermediate arrays
- Year‑by‑year processing

**3. Modularity**

- Each subsystem is independent
- Each file has a single responsibility
- Documentation mirrors code structure

**4. Transparency**

- Explicit formulas
- Clear assumptions
- Open‑source architecture

**🚀 Quick Start Example**

```python
from ccart.flood.chirps.compute_metrics import compute_baseline_metrics
from ccart.flood.fsi.build_fsi_v1_2 import build_fsi_v1_2
from ccart.flood.fsi.rasterise_fsi import rasterise_clean_rescale_fsi
from ccart.flood.hazard.hazard_engine import compute_historical_hazard
from ccart.flood.fsi.build_fsi_v1_1 import build_fsi_v1_1

# 1. Rainfall metrics
p95 = compute_baseline_metrics(1995, 2024, rx2day_dir, p95_path)

# 2. Susceptibility
gdf_v1_2 = build_fsi_v1_2(build_fsi_v1_1())
fsi_rescaled = rasterise_clean_rescale_fsi(gdf_v1_2, chirps_transform, shape)

# 3. Hazard
compute_historical_hazard(rx2day_dir, p95, fsi_rescaled, out_dir)
```
---

## 📌 Status

The CCART‑Floods module is being updated to be:

- fully modularised
- scientifically defensible
- reproducible end‑to‑end
- ready for open‑source release

This is now a multi‑hazard‑ready subsystem that matches the maturity of the cyclone module.

---

## 📚 References

### INDOFLOODS — Flood Susceptibility & Catchment Attributes (Primary Source)

Kuntla, S. K., & Saharia, M. (2025).  
INDOFLOODS: A comprehensive database for flood events in India enhanced with catchment attributes.  
Bulletin of the American Meteorological Society, 106(2), E333–E343.
https://doi.org/10.1175/BAMS-D-24-0008.1

Kuntla, S. K., & Saharia, M. (2025).  
INDOFLOODS: A Comprehensive Database for Flood Events in India Enhanced with Catchment Attributes [Data set].
Zenodo.
https://doi.org/10.5281/zenodo.14584654

Note: The public Zenodo release explicitly states that the Ganga and Brahmaputra basins are excluded. This is the reason for low FSI coverage in Bihar, Uttar Pradesh, Uttarakhand, Assam, and parts of Bengal.

### Other references

Rainfall & Climate Forcing
CHIRPS — Climate Hazards Group InfraRed Precipitation with Station Data  
Funk, C., Peterson, P., Landsfeld, M., et al. (2015).
The climate hazards infrared precipitation with stations—a new environmental record for monitoring extremes.  
Scientific Data, 2, 150066.
https://doi.org/10.1038/sdata.2015.66 (doi.org in Bing)

CMIP6 — Coupled Model Intercomparison Project Phase 6  
Eyring, V., Bony, S., Meehl, G. A., et al. (2016).
Overview of the Coupled Model Intercomparison Project Phase 6 (CMIP6) experimental design and organization.  
Geoscientific Model Development, 9, 1937–1958.
https://doi.org/10.5194/gmd-9-1937-2016 (doi.org in Bing)

Flood Susceptibility & Hydrology
INDOFLOODS — India Flood Susceptibility Dataset  
Bhunia, G. S., Shit, P. K., Pourghasemi, H. R., et al. (2023).
INDOFLOODS: A national‑scale flood susceptibility dataset for India.  
Zenodo.
https://doi.org/10.5281/zenodo.10036642 (doi.org in Bing)

Note: Public version excludes Ganga & Brahmaputra basins.

HydroBASINS — Global Hydrological Basins  
Lehner, B., Grill, G. (2013).
Global river hydrography and network routing: baseline data and new approaches to study the world’s large river systems.  
Hydrological Processes, 27(15), 2171–2186.
https://www.hydrosheds.org

Extreme Rainfall Metrics
Rx2day & Percentile Thresholds  
Alexander, L. V., Zhang, X., Peterson, T. C., et al. (2006).
Global observed changes in daily climate extremes of temperature and precipitation.  
Journal of Geophysical Research, 111(D5).
https://doi.org/10.1029/2005JD006290 (doi.org in Bing)

Climate‑Conditioned Hazard Modelling
Hazard Ratio Methods (Rainfall / Percentile Threshold)  
Kharin, V. V., Zwiers, F. W., Zhang, X., & Hegerl, G. C. (2007).
Changes in temperature and precipitation extremes in the IPCC ensemble of global coupled model simulations.  
Journal of Climate, 20(8), 1419–1444.
https://doi.org/10.1175/JCLI4066.1

General Open‑Science & Reproducibility
Peng, R. D. (2011).
Reproducible research in computational science.  
Science, 334(6060), 1226–1227.
https://doi.org/10.1126/science.1213847 (doi.org in Bing)
