[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.19427627.svg)](https://doi.org/10.5281/zenodo.19427627)

# CCART — Country‑Agnostic Climate Risk Framework

*India Implementation (v4) — Cyclone + Flood (v1.1) + Heat* 

**Anyone can add, critique, or modify — in order to get closer to the truth.**

CCART is a **country‑agnostic physical climate‑risk framework**.

India is the reference implementation, but the architecture is designed so that any country can be added by supplying:

- national boundary files
- hazard‑specific climate data

The pipeline handles the rest.

**CCART‑UK will be the first international extension.**

<p align="left">
<img src="https://img.shields.io/badge/Python-3.10%2B-blue" />
<img src="https://img.shields.io/badge/License-MIT-yellow" />
<img src="https://img.shields.io/badge/Status-Active-brightgreen" />
<img src="https://img.shields.io/badge/Release-v3.1-brightgreen" />
<img src="https://img.shields.io/github/last-commit/ketan-pednekar/ccart-india" />
<img src="https://img.shields.io/github/issues/ketan-pednekar/ccart-india" />
<img src="https://img.shields.io/github/stars/ketan-pednekar/ccart-india?style=social" />
</p>

---

## 🌍 Overview

**CCART** is a transparent, modular, reproducible climate‑risk framework designed for:

- hazard modelling  
- exposure processing  
- impact computation  
- calibration  
- spatial allocation  
- multi‑hazard expansion  

The architecture is:

- modular — each hazard is a standalone subsystem
- transparent — explicit formulas, assumptions, and data sources  
- reproducible — deterministic outputs, config‑driven paths  
- country‑agnostic — India is the reference, not the limit  
- open‑source ready — clean structure, no hidden steps  

The v3 repository introduces a **public, modular structure** that now includes:

- **Cyclone module** (historical + synthetic)  
- **Flood module** (CHIRPS + FSI + CMIP6)  
- **README documentation for each module**  
- **Example workflows**  
- **Reproducible folder structure**  

---

## Why CCART?

CCART exists because climate‑risk modelling is often opaque, proprietary, and irreproducible.  
This project aims to build a national, open, transparent climate‑risk framework that anyone can inspect, critique, and improve.

---

## 🧱 Architecture

CCART is organized into hazard modules, each with its own ingestion → hazard → exposure → impact → calibration pipeline.

```python
ccart-india/
│
├── README.md
├── LICENSE
├── requirements.txt
├── pyproject.toml
├── .gitignore
│
├── ccart/
    ├── __init__.py
    │
    ├── cyclone/          # Historical + synthetic cyclone engine
    ├── flood/            # Climate-conditioned flood hazard engine
    ├── heat/             # WBT + TXx + population exposure (in progress)
    │
    ├── exposure/         # Shared exposure utilities
    ├── vulnerability/    # Vulnerability curves + utilities
    ├── calibration/      # DLNA + calibration utilities
    ├── data/             # Boundary files, masks, static layers

```

**Each module includes its own README with full scientific and technical documentation.**

---

## 📦 Modules at a Glance

| Module            | Status   | Description |
|-------------------|----------|-------------|
| `cyclone/`        | Mature   | Historical + synthetic cyclone engine (v2) |
| `flood/`          | Updated  | Climate‑conditioned flood hazard engine (v1.1) |
| `heat/`           | Updated  | WBT + TXx + population exposure (v4) |
| `exposure/`       | Utility  | Shared exposure preprocessing tools |
| `vulnerability/`  | Utility  | Damage functions + vulnerability curves |
| `calibration/`    | Utility  | DLNA + calibration utilities |
| `data/`           | Static   | Boundary files, masks, static layers |

---

## 🌪️ Cyclone Module (v2 Engine)

A complete historical + synthetic cyclone modelling framework.

The cyclone module provides:

- Historical hazard reconstruction (IBTrACS + CLIMADA)
- Synthetic cyclone generation (analogue clustering + perturbations)
- Hazard modelling (windfield + inland decay)
- Exposure–hazard clipping
- Impact computation
- DLNA‑aligned calibration
- Hazard‑Weighted Exposure (HWE)
- Batch catalogue generation (baseline, warm SST, high‑end)

It is the most mature subsystem in CCART and sets the architectural standard.

### Full documentation:

```bash
ccart/cyclone/README.md
```
---

## 🌧️ Flood Module (v1.1 Engine)

A **frequency‑based, climate‑conditioned flood hazard engine** for India.

The v1.1 release introduces a **major methodological upgrade**:

### 🔄 Methodology Shift — Intensity → Frequency

#### **Earlier (v1.0) — Intensity‑Based Hazard**
Used a single extreme rainfall event:


```
H = FSI × max( Rx2day / P95, 0 )
```

**Issues:**  
- Sensitive to one extreme event  
- Unstable year‑to‑year  
- Hard to interpret  
- Weak scenario consistency  


#### **Current (v1.1) — Frequency‑Based Hazard**

Counts how often rainfall exceeds the P95 threshold:

```
H_y = (N_exceed, y) * FSI_uplift
```

Where:

- `(N_exceed,y)` = number of 2‑day rainfall events exceeding P95  
- `(FSI_uplift)` = scenario‑conditioned susceptibility  

**Benefits:**  
- Stable  
- Interpretable  
- Hydrologically realistic  
- Scenario‑consistent  
- Fully compatible with **CCART Number**  

---

### 🔧 Core Components

- **CHIRPS daily rainfall** (1995–2024)  
- **P95 Engine** — 95th percentile of 2‑day rainfall  
- **Rx2 Engine** — historical + CMIP6 extremes  
- **FSI v1.2** — IndoFloods + HydroBASINS hydrology  
- **FSI uplift** — scenario‑conditioned susceptibility  
- **CMIP6 SSP3‑7.0 / SSP5‑8.5** rainfall projections  

### 🎯 Primary Output — CCART Number

The Flood Module produces the two hazard‑max layers required for:

```
CCART_Number = H_max_future / H_max_historical
```
Where:

- `(H_max_historical)` = worst flood‑hazard year in 1995–2024  
- `(H_max_future)` = worst flood‑hazard year in 2027–2100 (scenario‑conditioned)

The **CCART Number** is the **headline metric** of CCART‑Floods and the key output of the module.

### Known Limitations - INDOFLOODS Coverage Gap
The Ganga and Brahmaputra basin data in INDOFLOODS is restricted by source agencies: CWC, NWIC, and 
Ministry of Jal Shakti. The INDOFLOODS authors confirmed this restriction directly. FSI v2.0 will 
incorporate this data when access is obtained through appropriate channels.

### 📄 Full documentation  

`ccart/flood/README.md`

---

## 🔥 Heat Module (v4 Engine — WBT35, TXx)

The CCART‑Heat module is a full wet‑bulb temperature (WBT) and heat‑extreme hazard engine for India.

It is built to be modular, transparent, and fully reproducible, following the same architectural principles as Cyclone and Flood.

The module produces:

- Daily WBT (wet‑bulb temperature) from CMIP6 variables
- Annual exceedance cubes (e.g., days > 35°C WBT)
- Time‑slice hazard cubes (e.g., 2081–2100)
- GeoTIFF hazard layers for mapping and GIS workflows
- District‑level exceedance summaries
- Strict India masks for spatial consistency

It is the third major hazard engine in CCART, after Cyclone and Flood.

### 🔧 Core Components

#### 1. Ingestion Layer

Uses CMIP6 variables:

- tas (air temperature)
- hurs (relative humidity)
- tasmax (for TXx, if needed)
- wbt (added later via add_wbt_to_ingested.py)

All ingested into standardized Zarr cubes under:

```
ccart/Heat/ingested/
```

#### 2. WBT Engine

Computes daily wet‑bulb temperature using a scientifically validated formulation.

Outputs:

```
WBT(time, lat, lon)
```

#### 3. Exceedance Engine

Computes:

```
exceed(year) = count of days where WBT > 35°C
```
Produces annual exceedance cubes for:

- hist
- ssp370
- ssp585

#### 4. Time‑Slice Hazard Cubes

Extracts 20‑year windows (e.g., 2081–2100) and computes:

- max exceedance
- mean exceedance
- district‑level exceedance

Saved under:

```
ccart/Heat/outputs/timeslice_cubes/
```

#### 5. GeoTIFF Export

Exports north‑up, GIS‑ready TIFFs:

```
ccart/Heat/outputs/timeslices_wbt35/
```

#### 6. Validation Suite

Located in:

```
ccart/Heat/utils/
```

Includes:

- Ingested cube validator
- Time‑slice cube validator
- Time‑slice TIFF validator
- Strict India mask generator
- Orientation diagnostics
- District‑level exceedance checks

This ensures no flipped rasters, no CRS mismatches, no misaligned grids.

---

### 📈 Primary Outputs

- Annual exceedance cubes (Tw > 35°C)
- Time‑slice hazard cubes (e.g., 2081–2100)
- GeoTIFF hazard layers
- District‑level exceedance tables
- Strict India mask

These outputs are designed for:

- climate‑risk analysis
- adaptation planning
- heat‑stress mapping
- exposure modelling
- multi‑hazard integration

---

### 🧪 Scientific Notes

- WBT is computed using a physically consistent formulation (Stull (2011))
- All hazards are regridded to a 0.05° India grid
- CMIP6 native resolution remains ~175 km (ACCESS‑CM2 N96)
- Outputs are directional indicators, not forecasts
- All orientation logic is explicitly documented
- All validators are open and reproducible

---

### 📄 Full documentation

```
ccart/Heat/README.md
```

---

## 🧩 CCART — Unified Multi‑Hazard Architecture

CCART is not just a cyclone engine or a flood engine — it is a **country‑agnostic, modular, multi‑hazard climate‑risk framework**.

India is the **reference implementation (v3)**, but the architecture is designed so that any country can be added by supplying:

- national boundary files
- hazard‑specific climate data

The pipeline handles the rest.

**CCART‑UK will be the first international extension.**

---

## 🌍 CCART Philosophy

CCART is built on four non‑negotiable principles:

### 1. Modularity

- Each hazard engine is independent, testable, and replaceable.

### 2. Scientific Honesty

- No black‑box shortcuts.
- All formulas are explicit.
- All assumptions are visible.

### 3. Reproducibility

- Config‑driven paths.
- Deterministic outputs.
- No hidden steps.

### 4. Country‑Agnostic Design

- Any country can be added by supplying boundary files + climate data.
- The CCART pipeline handles ingestion → hazard → exposure → impact → calibration → metrics.

---

## 🧱 CCART High‑Level Architecture


`Ingestion → Hazard Engines → Exposure → Impact → Calibration → Metrics`

### Shared Ingestion Layer

- CHIRPS rainfall (historical)
- CMIP6 rainfall & temperature (future)
- IBTrACS cyclone tracks
- IndoFloods catchment attributes
- CLIMADA hazard engines

### Hazard Modules

- **CCART‑Cyclone** (historical + synthetic)
- **CCART‑Floods** (frequency‑based hazard + CCART Number)
- **Heat module** (tasmax anomalies, WBT)

### Impact & Calibration

- Exposure preprocessing
- Vulnerability curves
- District‑level aggregation
- DLNA‑style calibration (cyclone)
- Hazard‑Weighted Exposure (HWE)

### Outputs

- Hazard rasters
- Impact tables
- Scenario‑conditioned metrics
- CCART Number (floods)
- Synthetic cyclone ensembles

---

## 📚 Scientific References

### Rainfall & Climate Data

- CHIRPS — Funk et al. (2015). The Climate Hazards Infrared Precipitation with Stations (CHIRPS).
- CMIP6 — Eyring et al. (2016). Overview of CMIP6.

## Flood Data

Kuntla, S. K., & Saharia, M. (2025).
INDOFLOODS: A comprehensive database for flood events in India enhanced with catchment attributes.  
Bulletin of the American Meteorological Society, 106(2), E333–E343.
https://doi.org/10.1175/BAMS-D-24-0008.1

Kuntla, S. K., & Saharia, M. (2025).
INDOFLOODS: A Comprehensive Database for Flood Events in India Enhanced with Catchment Attributes [Data set].
Zenodo. https://doi.org/10.5281/zenodo.14584654

## Cyclone Data

IBTrACS — Knapp et al. (2010). The International Best Track Archive for Climate Stewardship.

## Hazard Engine
CLIMADA — Aznar‑Siguan & Bresch (2019). CLIMADA v1.

## ⚠️ Disclaimer — Interpretation of CCART Outputs

**CCART does not claim pinpoint accuracy.**  

It provides **directional, physics‑based indicators** that help understand how climate‑related risks may shift under different scenarios.
Outputs are **not predictions, forecasts, or guarantees** of future events.

**ACCESS‑CM2** native atmospheric/land resolution is **~175 km (N96 grid), regridded to 0.05°** for consistency with the observational baseline. 
The effective resolution of future projections remains **~175 km.**

All methodology, data sources, assumptions, and limitations are fully documented,
openly accessible, and independently verifiable.

Users are encouraged to review the documentation and assess suitability for their specific applications.

### Version History
- v4.0 (June 2026): Added Heat module, updated Flood config, integrated Vulnerability
- v3.1 (May 2026): Cyclone + Flood integration
