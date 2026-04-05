# CCART — Country‑Agnostic Climate Risk Framework

*India Implementation (v3) — Cyclone + Flood Modules*

**Anyone can add, critique, or modify — in order to get closer to the truth.**

CCART is a **country‑agnostic physical climate‑risk framework**.

India is the reference implementation, but the architecture is designed so that any country can be added by supplying:

- national boundary files
- hazard‑specific climate data

The pipeline handles the rest.

CCART‑UK will be the first international extension.

<p align="left">
<img src="https://img.shields.io/badge/Python-3.10%2B-blue" />
<img src="https://img.shields.io/badge/License-MIT-yellow" />
<img src="https://img.shields.io/badge/Status-Active-brightgreen" />
<img src="https://img.shields.io/badge/Release-v3.0-brightgreen" />
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
│   ├── __init__.py
│   │
│   ├── cyclone/          # Historical + synthetic cyclone engine
│   ├── flood/            # Climate-conditioned flood hazard engine
│   ├── heat/             # Placeholder for tasmax anomaly module (v4)
│   │
│   ├── exposure/         # Shared exposure utilities
│   ├── vulnerability/    # Vulnerability curves + utilities
│   ├── calibration/      # DLNA + calibration utilities
│   ├── data/             # Boundary files, masks, static layers
│
└── ccart.egg-info/       # Package metadata (auto-generated)
```
Each module includes its own README with full scientific and technical documentation.

---

## 📦 Modules at a Glance

| Module            | Status   | Description |
|-------------------|----------|-------------|
| `cyclone/`        | Mature   | Historical + synthetic cyclone engine (v2) |
| `flood/`          | New      | Climate‑conditioned flood hazard engine (v1) |
| `Heat/`           | Planned  | Tasmax anomaly + exposure module (v4) |
| `exposure/`       | Utility  | Shared exposure preprocessing tools |
| `vulnerability/`  | Utility  | Damage functions + vulnerability curves |
| `calibration/`    | Utility  | DLNA + calibration utilities |
| `data/`           | Static   | Boundary files, masks, static layers |

---

## 🌪️ Cyclone Module (v2 Engine)

A complete historical + synthetic cyclone modelling framework

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

### 📄 Full documentation:  

```bash
ccart/cyclone/README.md
```
---

## 🌧️ Flood Module (v1 Engine)

Climate‑conditioned flood hazard for India

The flood module integrates:

- CHIRPS daily rainfall (1995–2024)
- Rx2day + P95 baseline metrics
- FSI v1.2 (INDOFLOODS + HydroBASINS)
- CMIP6 SSP3‑7.0 / SSP5‑8.5 rainfall projections

**Hazard formula:**
H = FSI × max( Rx2day / P95, 0 )

where:
- FSI = Flood Susceptibility Index (0–1, INDOFLOODS empirical)
- Rx2day = annual maximum 2-day accumulated precipitation (mm)
- P95 = 95th percentile of Rx2day over 1995–2024 baseline (mm)

The pipeline includes:

- CHIRPS ingestion
- rainfall metrics
- FSI construction + rasterisation
- hazard computation (historical + future)
- resume‑friendly year‑by‑year loops

### 📄 Full documentation:  

`ccart/flood/README.md`

---

## 🚀 Quickstart

Install dependencies:

```bash
pip install -r requirements.txt
```

Run cyclone examples:

```bash
python ccart/cyclone/synthetic/run_single_synthetic.py
python ccart/cyclone/synthetic/run_batch.py
```

Run flood pipeline:

```python
python ccart/flood/example/run_flood_pipeline.py
```
---

## 🧭 Roadmap

- Current - v3 — Modular Public Release
  - Cyclone module
  - Flood module (current)

- Future
  V4 - Improving current version
    - Heat module (tasmax anomalies)
    - Surge integration
    - OSM + DEM models for exposure calculation
    - Unified multi‑hazard risk layers

  v5 — International Expansion
    - CCART‑UK
    - CCART‑Japan

---

## 📚 Data & Tools Acknowledgements

CCART relies on several open scientific datasets and tools.

We acknowledge and thank the creators and maintainers of:

- **CHIRPS** — Climate Hazards Group InfraRed Precipitation with Station data
- **CMIP6** — Coupled Model Intercomparison Project Phase 6 climate projections
- **INDOFLOODS** — Geomorphology‑based flood susceptibility dataset for India
- **HydroBASINS** — Global hydrological basin boundaries
- **CLIMADA** — Open‑source climate‑risk modelling engine used for cyclone hazards
- **India administrative boundaries** — Publicly available district‑level shapefiles used for research and non‑commercial analysis

These datasets and tools form the scientific foundation for CCART’s hazard and impact modelling workflows.

---

## 📄 License

Released under the MIT License.

---

## 📑 How to Cite CCART

```bash
Pednekar, K. (2026). CCART: A Country‑Agnostic Physical Climate Risk Framework — 
India Implementation. github.com/ketan-pednekar/ccart-india.
```
---

## 🤝 Contributing

CCART welcomes contributions from:

- climate scientists
- geospatial analysts
- engineers
- open‑source contributors
- adaptation planners

To contribute:

- Open an issue
- Discuss the idea
- Submit a modular pull request

CCART is built on transparency, collaboration, and scientific clarity.

---

## 🎯 Summary

The new CCART architecture is:

- **modular**
- **transparent**
- **reproducible**
- **multi‑hazard ready**
- **country‑agnostic**

Cyclone + Flood modules now form the foundation of a national, open, reproducible climate‑risk platform — ready for expansion into heat, surge, and international deployments.