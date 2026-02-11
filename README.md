# CCART: Cyclone Calibration and Risk Toolkit (India)

<p align="left">
  <img src="https://img.shields.io/badge/Python-3.10%2B-blue" />
  <img src="https://img.shields.io/badge/License-MIT-yellow" />
  <img src="https://img.shields.io/badge/Status-Active-brightgreen" />
  <img src="https://img.shields.io/badge/Release-v2.0-brightgreen" />
  <img src="https://img.shields.io/github/last-commit/ketan-pednekar/ccart-india" />
  <img src="https://img.shields.io/github/issues/ketan-pednekar/ccart-india" />
  <img src="https://img.shields.io/github/stars/ketan-pednekar/ccart-india?style=social" />
</p>
---

## **CCART v2 — Synthetic Cyclone Impact Engine (2026)**

A clean, modular, reproducible engine for generating synthetic tropical cyclone impacts across India. It integrates **CLIMADA’s open‑source hazard engine** with **DLNA‑aligned calibration** to generate consistent, physics‑based loss estimates across all Indian districts. 

**CCART v2** introduces a fully automated synthetic cyclone generator that produces realistic, physics‑consistent cyclone impacts beyond the historical record. It extends CCART from a calibrated historical toolkit (v1.3) into a **probabilistic, scenario‑driven climate‑risk platform**.

## 🌟 What’s New in v2
- Synthetic cyclone generator (historical analogue clustering)
- v2 hazard engine with improved footprint realism
- Inland masking using distance‑to‑coast
- Exposure–hazard clipping for computational efficiency
- District‑level hazard statistics (max wind, inland flag, coastal proximity)
- Calibration applied only to coastal districts
- Hazard‑Weighted Exposure (HWE) for spatial allocation
- District + state maps for every affected region
- Batch runner for generating synthetic catalogues
- Clean per‑run folder structure and metadata
- Catalogue‑ready outputs for probabilistic risk analysis
---

## Key Features (v2)

### 🔹 Synthetic Cyclone Generator
- Generates realistic, physics‑consistent synthetic cyclone tracks  
- Based on historical analogue clustering and intensity distributions  
- Enables probabilistic and scenario‑driven risk analysis  

### 🔹 v2 Hazard Engine
- Improved windfield realism and inland decay  
- Bounding‑box hazard clipping for computational efficiency  
- District‑level hazard statistics (max wind, inland flag, coastal proximity)  

### 🔹 DLNA‑Aligned Calibration (Coastal‑Only)
- Calibration applied only to coastal districts for scientific consistency  
- Ensures calibrated losses remain physically meaningful  
- Produces stable, reproducible national‑scale loss estimates  

### 🔹 Hazard‑Weighted Exposure (HWE)
- Allocates calibrated losses using hazard‑weighted exposure  
- Preserves spatial gradients from the hazard footprint  
- Ensures district‑level loss patterns remain physically interpretable  

### 🔹 Clean, Modular Output Structure
Each synthetic run produces a reproducible folder containing:

- `impact.gpkg`  
- `metadata.json`  
- District‑level maps  
- State‑level maps  

This structure is designed for catalogue‑level analysis and long‑term archival.

### 🔹 Batch Catalogue Generation
- Run 10, 50, 100, or 1000 synthetic cyclones  
- Automatically generates `synthetic_summary.csv`  
- Enables return‑period curves, exceedance probability curves, and atlas‑level diagnostics  

### 🔹 Fully Reproducible, Fully Transparent
- Deterministic hazard → exposure → impact → calibration → HWE pipeline  
- No black‑box components  
- Built entirely on open‑source tools (CLIMADA, GeoPandas, NumPy, Pandas)  
---

**The goal is to build a national, open, reproducible cyclone‑impact platform that researchers, engineers, and policymakers can extend collaboratively.**
---

## 📘 Overview (v2)

CCART v2 introduces a fully automated **synthetic cyclone impact engine** that extends CCART beyond the historical record into probabilistic, scenario‑driven climate‑risk analysis. The v2 pipeline is clean, modular, and fully reproducible, integrating hazard, exposure, impact, calibration, and visualization into a deterministic workflow.

The v2 engine includes:

- **Synthetic cyclone generation** using historical analogue clustering  
- **v2 hazard engine** with improved footprint realism and inland decay  
- **Exposure–hazard clipping** for computational efficiency  
- **District‑level hazard diagnostics** (max wind, inland flag, coastal proximity)  
- **DLNA‑aligned calibration** applied only to coastal districts  
- **Hazard‑Weighted Exposure (HWE)** for spatial allocation  
- **District‑level and state‑level maps** for every affected region  
- **Per‑run metadata** for catalogue‑level analysis  
- **Batch runner** for generating synthetic storm catalogues  

The v2 engine is designed to be:

- **transparent** — deterministic hazard → exposure → impact → calibration → HWE  
- **reproducible** — identical results for identical inputs  
- **extensible** — ready for flood, surge, and multi‑hazard expansion  
- **catalogue‑ready** — supports 10, 50, 100, or 1000 synthetic runs  
---

## 📁 Repository Structure (v2)

```text
ccart-india/
│
├── ccart/                               # CCART v2 engine (active)
│   │
│   ├── synthetic/                       # Synthetic cyclone generation (v2)
│   │   ├── run_synthetic_cyclone_v2.py  # Run one synthetic cyclone
│   │   ├── run_synthetic_batch.py       # Generate full synthetic catalogue
│   │   ├── generator.py                 # Track generator + analog logic
│   │   └── __init__.py
│   │
│   ├── viz/                             # Mapping + visualisation
│   │   ├── viz_v2.py                    # District/state choropleths
│   │   └── __init__.py
│   │
│   ├── hazard.py                        # Hazard engine (windfield + decay)
│   ├── hazard_simulated_v2.py           # CLIMADA-based hazard wrapper
│   ├── exposure.py                      # LitPop + exposure utilities
│   ├── vulnerability.py                 # Vulnerability functions
│   ├── impact.py                        # Impact computation
│   ├── hwe.py                           # Hazard-Weighted Exposure engine
│   ├── calibration.py                   # DLNA coastal calibration
│   ├── __init__.py
│
├── legacy/                              # CCART v1.3 historical engine
│   ├── pipeline_v1_3.py
│   ├── utils.py
│   ├── viz.py
│   └── ...
│
├── archive/                             # Old scripts, prototypes, v1.2 code
│   └── ...
│
├── scripts/                             # Helper scripts (optional)
│   └── ...
│
├── data/                                # Required datasets (not bundled)
│   ├── IBTrACS.ALL.v04r01.nc
│   ├── india_districts.geojson
│   ├── coastal_ind.shp
│   └── ...
│
├── outputs/                             # Auto-generated outputs
│   ├── synthetic/                       # v2 synthetic catalogue
│   └── diagnostics/                     # Plots, logs, maps
│
├── docs/                                # Documentation + methodology
├── examples/                            # Example workflows
├── notebooks/                           # Jupyter notebooks
├── analysis/                            # Additional analysis scripts
│
├── README.md
├── LICENSE
├── requirements.txt
├── pyproject.toml
└── .gitignore
```
---

## Installation

```bash
pip install -r requirements.txt
```
---

## 🚀 Quickstart (v2)
CCART v2 provides a clean, modular, fully automated pipeline for generating synthetic tropical cyclone impacts across India.
You can run a single synthetic cyclone or generate a full synthetic catalogue.

### ▶️ Run a single synthetic cyclone
Runs one analogue‑based synthetic track through the full v2 hazard–impact pipeline.

```bash
python synthetic/run_synthetic_cyclone_v2.py
```
### ▶️ Run a batch of synthetic cyclones
Generates the full v2 synthetic catalogue (92 events by default).

```bash
python synthetic/run_synthetic_batch.py
```
### This will automatically generate:

```bash
outputs/synthetic_runs/
    run_001/
    run_002/
    ...
    synthetic_summary.csv
```
---
## 🧭 CCART V2 Pipeline

```
┌──────────────────────────┐
│  Synthetic Track Engine  │
│ (Analogue-based generator)│
└───────────────┬──────────┘
                │
                ▼
┌──────────────────────────┐
│     Hazard Engine v2     │
│ (Windfield + inland decay)│
└───────────────┬──────────┘
                │
                ▼
┌──────────────────────────┐
│   Exposure–Hazard Clip   │
│ (District geometry mask) │
└───────────────┬──────────┘
                │
                ▼
┌──────────────────────────┐
│      Impact Module       │
│   (Raw CLIMADA losses)   │
└───────────────┬──────────┘
                │
                ▼
┌──────────────────────────┐
│   Calibration (Coastal)  │
│  DLNA-aligned scaling    │
└───────────────┬──────────┘
                │
                ▼
┌──────────────────────────┐
│ Hazard-Weighted Exposure │
│   (Spatial allocation)   │
└───────────────┬──────────┘
                │
                ▼
┌──────────────────────────┐
│     Final Outputs        │
│ Maps • GPKG • Metadata   │
└──────────────────────────┘
```
---
## **Usage (v2)**

CCART v2 is built around a clean, modular workflow.
All synthetic cyclone analyses are executed through the `ccart/synthetic/` scripts:

- hazard generation (v2)
- exposure–hazard clipping
- raw impact computation
- coastal‑only DLNA calibration
- HWE spatial allocation
- district‑level and state‑level maps
- metadata export
- batch catalogue generation  
---

### **What the v2 scripts do**
- Generate a synthetic cyclone track
- Build the v2 hazard footprint
- Clip hazard to district geometry
- Compute raw CLIMADA losses
- Apply coastal‑only DLNA calibration
- Allocate calibrated losses using HWE
- Export maps and impact tables
- Write run‑level metadata
- Append results to `synthetic_summary.csv` (batch mode)
---

### Where to explore the workflow

The full v2 pipeline scripts are located in:
`ccart`
`ccart/synthetic/`

Key components include:

`run_synthetic_cyclone_v2.py` — run a single synthetic cyclone
`run_synthetic_batch.py` — generate a synthetic catalogue
`hazard_v2.py` — hazard engine
`calibration_v2.py` — coastal calibration
`hwe_v2.py` — spatial allocation
`viz_v2.py` — map generation
These scripts demonstrate how to run a cyclone, inspect outputs, and explore intermediate diagnostics.

---

## ⚠️ Known Limitations

- **Exposure is proxy‑based.** We rely on litpop and other proxies; results depend on proxy quality and spatial resolution.
- **District‑level calibration.** DLNA values are aggregated and may not capture local variations in impact.
- **Windfield simplifications.** CLIMADA’s parametric wind model may differ from high‑resolution dynamical simulations.
- **No flood or storm‑surge module yet.** The current version models wind impacts only.
- **Historical bias.** Outputs depend on IBTrACS track accuracy and reporting quality.
- **Not a substitute for engineering studies.** CCART provides indicative risk patterns, not site‑specific structural assessments.
- **Synthetic tracks are analogue‑based.** They follow historical geometry patterns and do not yet include perturbations or Monte‑Carlo variations (planned for v2.1).

---

## 🌍 Why CCART?

India faces rising cyclone risk, yet district‑level impact intelligence remains fragmented, opaque, and difficult to reproduce.
CCART was built to change that.

This toolkit provides:

- **Transparent, calibrated cyclone loss estimates** at the district level
- **Reproducible, open workflows** built entirely on public data and open‑source tools
- **A modular pipeline** covering hazard, exposure, impact, and calibration
- **A foundation for future expansion** into multi‑hazard and future‑climate scenarios

CCART is designed for researchers, analysts, and institutions seeking **credible, scalable, and fully transparent climate‑risk diagnostics for India.**

---
## 🧭 Roadmap

### v2.0 — Synthetic Cyclone Expansion (Current Release)
- analogue‑based synthetic track generation
- calibrated wind‑impact modelling across all coastal states
- district‑level hazard, exposure, impact, and HWE allocation
- reproducible synthetic catalogue for probabilistic risk layers

### v2.1 — Enhanced Synthetic Engine
- perturbation‑based track variations (Monte‑Carlo geometry)
- improved inland decay and exposure masking
- expanded diagnostics and metadata for each synthetic run

### v3.0 — High‑Resolution & ML‑Driven Cyclone Risk
*(Refining cyclone impacts before expanding into multi‑hazard)*
- high‑resolution proxy layers (nightlights, land use, infrastructure density)
- machine‑learning models for local damage estimation where DLNA data is unavailable
- QGIS‑ready outputs for TCFD, site‑level screening, and infrastructure planning
- refined cyclone‑only risk layers for adaptation and insurance use‑cases

### v4.0 — Multi‑Hazard Expansion (Post‑Cyclone Consolidation)
- Flood module (rainfall + riverine + surge integration)
- Heat module (tasmax anomalies + population‑weighted exposure)
- unified multi‑hazard impact layers for adaptation planning
- long‑term climate scenario integration (CMIP6/7)
---

## 📂 Data Sources

CCART relies on a combination of open datasets and curated inputs.  
Large datasets are **not bundled** with this repository to keep the project lightweight.

---
### 🌪️ Tropical Cyclone Tracks (IBTrACS)

The full IBTrACS dataset can be downloaded from NOAA:  
https://www.ncei.noaa.gov/products/international-best-track-archive

Place the netcdf file at: 
`data/IBTRACS.ALL.v04r01.nc`

---
### 🗺️ Administrative Boundaries

CCART requires district‑level administrative boundaries for hazard, exposure, and impact aggregation.

Place the national‑level GeoJSON or shapefile in:
`data/INDIA_DISTRICTS.geojson`

---
### 🗺️ INDIA SHAPEFILES

INDIAN‑SHAPEFILES by datta07 on GitHub — used for district‑level administrative boundaries of India.
These boundaries are incorporated solely for research, modelling, and non‑commercial analysis within the CCART project.

---
## 🏷️ Topics

`open-source` `geospatial` `cyclone` `india` `adaptation`  
`climada` `climate-risk` `disaster-risk` `impact-modelling` `hazard-modelling`

---
## 🌐 Website

Visit [www.ccartghg.com](http://www.ccartghg.com) for updates and future outreach.

---
## 📄 License

This project is released under the **MIT License**.  
See `LICENSE` for details.

---
## 📑 How to Cite CCART

If you use CCART in research, analysis, or publications, please cite it as:

```
Pednekar, K. (2026). CCART: Cyclone Calibration and Risk Toolkit (India) – Pan‑India 15‑Cyclone Calibrated Release (v1.1).
https://github.com/ketan-pednekar
```

For general reference to the methodology:
```
Pednekar, K. (2026). A transparent, reproducible framework for district‑level tropical cyclone impact modelling in India using CLIMADA, DLNA calibration, and Hazard‑Weighted Exposure (HWE).`
```
If you use specific datasets from the repository (e.g., district_relationships_master.csv or cyclone_level_summary.csv), please cite:
```
CCART Dataset (2026). District‑level calibrated cyclone impact dataset for 15 historical Indian cyclones (2009–2021). Part of CCART v1.1.
```
---

## 🤝 Contributors & Acknowledgements

CCART is shaped by open-source principles, transparent methods, and collaborative thinking.

**Core Developer**
- Ketan Pednekar — Architecture, modelling, calibration logic, documentation, and overall design.

**Acknowledgements**
- Appreciation to the open-source climate modelling community whose tools and ideas make reproducible risk analysis possible.
- Thanks to Microsoft Copilot for collaborative support in debugging, structuring workflows, refining documentation, and shaping CCART into a clear, modular, and credible toolkit.

**How to Contribute**
CCART welcomes collaboration from:

- climate scientists  
- geospatial analysts  
- engineers and modellers  
- open‑source contributors  
- risk analysts and adaptation planners  

To contribute:

1. Open an issue to discuss ideas, bugs, or enhancements  
2. Submit a pull request with clear, modular changes  
3. Follow the project’s structure and reproducibility principles  

CCART is built on transparency, collaboration, and scientific clarity — and contributions that uphold these values are especially welcome.

---

Open an **Issue** or start a **Discussion** to get involved.

---
## 🚀 Releases

### v2.0 – Synthetic Cyclone Engine (Current Release)
- Introduces **synthetic cyclone generation** using analogue‑based track geometry
- Adds the full **v2 hazard engine** with improved inland decay and spatial consistency
- Implements **district‑level hazard, exposure, impact, and HWE allocation** for synthetic events
- Adds **run‑level metadata**, diagnostics, and reproducible outputs for every synthetic cyclone
- Supports **batch catalogue generation** for probabilistic risk analysis
- Provides **clean v2 scripts** (`run_synthetic_cyclone_v2.py`, `run_synthetic_batch.py`, `hazard_v2.py`, `calibration_v2.py`, `hwe_v2.py`, `viz_v2.py`)
- Establishes a **modular, transparent v2 workflow** for national‑scale synthetic risk modelling

Note:  
v2 focuses on **synthetic cyclone modelling**. Historical DLNA‑calibrated datasets remain available under v1.x for transparency and reproducibility.



### v1.3 – Automated, Metadata‑Driven Multi‑Cyclone Engine

- Introduced the **v1.3 multi‑state engine** (`pipeline_v1_3.py`) with metadata‑driven execution  
- Added **batch_runner_v1_3.py** for automated national‑scale cyclone processing  
- Standardized all cyclone scripts to the new `_v1_3` architecture  
- Integrated **coastal proximity logic**, improved inland clipping, and refined exposure extraction  
- Generated a **clean national master dataset (v1.3)** with district‑level hazard, exposure, impact, and calibration  
- Ensured strict **SID‑anchored consistency** across all 14 calibrated cyclones  
- Preserved all **v1.2 legacy scripts** for transparency and reproducibility  
- Refined repository structure for clarity, modularity, and future multi‑hazard expansion  

**Note on Cyclone Tauktae (2021)**  
Cyclone Tauktae is excluded from the v1.3 calibrated dataset.
During processing, CLIMADA’s parametric windfield model reached a computational ceiling under Tauktae’s extreme intensity and multi‑state footprint, resulting in unstable hazard fields. To maintain scientific integrity and reproducibility, Tauktae is deferred to a future release once a stable configuration is established.

### v1.2 – Metadata‑Driven, Multi‑State Architecture

- Introduced a fully metadata‑driven cyclone workflow (single script, multiple cyclones)  
- Added multi‑state calibration logic for cyclones affecting more than one state  
- Separated state‑agnostic CCART engine from state‑specific configuration  
- Upgraded all cyclone scripts to the new v1.2 architecture  
- Regenerated the full 15‑cyclone national dataset using the new engine  
- Integrated batch runner for end‑to‑end national automation  
- Ensured SID‑anchored consistency across all outputs  
- Refined directory structure for clarity, reproducibility, and future expansion  


### v1.1 – Pan‑India 15‑Cyclone Calibrated Release

- Added **15 calibrated historical cyclones** (2009–2021)  
- Added **district_relationships_master.csv** (full India, 15‑event calibrated dataset)  
- Added **cyclone_level_summary.csv** (cross‑cyclone diagnostics: raw loss, calibrated loss, DLNA ratios)  
- Added export‑enabled scripts for all 15 cyclones under a unified CCART v1.0 engine  
- Added SID‑anchored metadata for every cyclone  
- Standardized all cyclone workflows for reproducibility and transparency  
- Improved documentation and repository structure for national‑scale analysis  

#### 🌀 Cyclones Included in v1.1

| Cyclone | Year | DLNA (USD) | State |
|--------|------|------------|--------|
| Aila | 2009 | 1.2B | West Bengal |
| Laila | 2010 | 0.6B | Andhra Pradesh |
| Phailin | 2013 | 4.15B | Odisha |
| Helen | 2013 | 0.5B | Andhra Pradesh |
| Hudhud | 2014 | 3.5B | Andhra Pradesh |
| Vardah | 2016 | 1.0B | Tamil Nadu |
| Ockhi | 2017 | 0.9B | Kerala |
| Titli | 2018 | 0.92B | Odisha |
| Gaja | 2018 | 1.6B | Tamil Nadu |
| Fani | 2019 | 4.2B | Odisha |
| Bulbul | 2019 | 3.2B | West Bengal |
| Amphan | 2020 | 13.0B | West Bengal |
| Nisarga | 2020 | 0.6B | Maharashtra |
| Tauktae | 2021 | 1.0B | Gujarat |
| Yaas | 2021 | 2.99B | Odisha |

**Each cyclone includes:**

- District‑level calibrated loss table  
- Choropleth map  
- Narrative summary  
- HWE diagnostics  


### v1.0 – Multi‑Cyclone Calibrated Release

- Added Amphan, Fani, Nisarga, Phailin, and Tauktae  
- Introduced Hazard–Weighted Exposure (HWE)  
- Implemented hazard floor and inland clipping  
- Added district‑level calibrated loss tables  
- Added standardized cyclone maps and narratives  
- Published CCART v1.0 slide carousel  
- Repository restructured for clarity and reproducibility  


### v0.9 – Fani Baseline

- Initial prototype of CCART  
- First implementation of hazard ingestion, exposure, and vulnerability  
- Early calibration workflow       
