# CCART: Cyclone Calibration and Risk Toolkit (India)

<p align="left">
  <img src="https://img.shields.io/badge/Python-3.10%2B-blue" />
  <img src="https://img.shields.io/badge/License-MIT-yellow" />
  <img src="https://img.shields.io/badge/Status-Active-brightgreen" />
  <img src="https://img.shields.io/badge/Release-v1.2-brightgreen" />
  <img src="https://img.shields.io/github/last-commit/ketan-pednekar/ccart-india" />
  <img src="https://img.shields.io/github/issues/ketan-pednekar/ccart-india" />
  <img src="https://img.shields.io/github/stars/ketan-pednekar/ccart-india?style=social" />
</p>

**CCART v1.2 — Pan‑India Multi‑State Automated Release**

A transparent, reproducible, and India‑focused toolkit for district‑level tropical cyclone impact modelling.  
CCART combines CLIMADA’s hazard engine with DLNA‑aligned calibration to produce credible, physics‑driven loss estimates across India.

---

## What’s New in v1.2

- **Metadata‑driven batch automation** for all 15 calibrated cyclones  
- **SID‑anchored cyclone metadata** for reproducible multi‑state workflows  
- **Automated state‑level slicing** and clean GeoJSON exports  
- **All‑India master CSV** for each cyclone (district‑level hazard, exposure, impact)  
- **Standardized logs** for every run  
- **Dedicated `scripts/` folder** for each cyclone’s reproducible workflow  

This release marks the transition from manual, cyclone‑specific scripts to a unified, automated national engine.

---

**The goal is to build a national, open, reproducible cyclone impact platform that researchers, engineers, and policymakers can extend collaboratively.**

---

## 📘 Overview

CCART integrates the full cyclone‑impact workflow:

- **IBTrACS → CLIMADA hazard generation**
- **District-level hazard diagnostics**
- **LitPop exposure extraction**
- **Coastal tier logic for India**
- **Tropical cyclone vulnerability curves**
- **Raw CLIMADA impact engine**
- **DLNA calibration** (state-level)
- **Hazard–Exposure Weighting Engine (HWE)**
- **Multi-cyclone runner** for historical and synthetic storms

The engine is designed to be:

- **transparent** — no black-box steps  
- **reproducible** — deterministic hazard + exposure + vulnerability  
- **extensible** — multi-state, multi-cyclone, multi-hazard  
- **collaboration-ready**

---
## 📁 Repository Structure

```
ccart-india/
│
├── ccart/                      # Core Python package
│   ├── engine.py               # v1.2 unified engine (metadata-driven)
│   ├── utils.py
│   ├── viz.py
│   └── __init__.py
│
├── scripts/                    # Reproducible cyclone runners (v1.2)
│   ├── run_aila.py
│   ├── run_amphan.py
│   ├── run_bulbul.py
│   ├── run_fani.py
│   ├── run_gaja.py
│   ├── run_helen.py
│   ├── run_hudhud.py
│   ├── run_laila.py
│   ├── run_nisarga.py
│   ├── run_ockhi.py
│   ├── run_phailin.py
│   ├── run_tauktae.py
│   ├── run_titli.py
│   ├── run_vardah.py
│   └── run_yaas.py
│
├── scripts/run_all_cyclones.py     # Automated batch runner (v1.2)
│
├── examples/                   # Example scripts and notebooks
│   ├── run_aila.py
│   ├── run_amphan.py
│   ├── run_bulbul.py
│   ├── run_fani.py
│   ├── run_gaja.py
│   ├── run_helen.py
│   ├── run_hudhud.py
│   ├── run_laila.py
│   ├── run_nisarga.py
│   ├── run_ockhi.py
│   ├── run_phailin.py
│   ├── run_tauktae.py
│   ├── run_titli.py
│   ├── run_vardah.py
│   ├── run_yaas.py
│   └── CCART_v1.2_Diagnostics.ipynb
│
├── data/                       # Lightweight inputs + metadata
│   ├── cyclone_metadata.csv
│   ├── INDIA_DISTRICTS.geojson
│   ├── coastl_ind.shp
│   ├── district_relationships_master.csv
│   ├── district_relationships_master_v1_2.csv   # Frozen v1.2 dataset
│   └── cyclone_level_summary.csv
│
├── outputs/                    # Auto-generated outputs (empty in repo)
│
├── docs/                       # Documentation, figures, outreach
│
├── README.md
├── LICENSE
└── requirements.txt
```
---

## ⚙️ Key Features
- CLIMADA-based hazard builder (IBTrACS to TropCyclone)
- District-level hazard diagnostics (max wind, mean wind, centroid distance, inland clipping)
- LitPop exposure extraction for any Indian state
- Coastal tier classification (Tier 1, Tier 2, Tier 3, coastal proximity score)
- India-specific vulnerability curves (housing, health, infrastructure)
- Raw CLIMADA impact engine for physics-driven loss estimation
- DLNA calibration module (state-level, SID-anchored, multi-state aware)
- Hazard–Weighted Exposure Engine (HWE) for spatial allocation of calibrated losses
- Metadata-driven multi-cyclone runner for all 15 calibrated cyclones
- Reproducible v1.2 cyclone scripts for each historical event
- National master dataset generation (district-level hazard, exposure, impact, calibration)
---

## Installation

```bash
pip install -r requirements.txt
```
---
## 🚀 Quickstart

CCART v1.2 provides reproducible, metadata‑driven scripts for running calibrated cyclone analyses.
You can run a single cyclone or all 15 calibrated cyclones using the scripts included in the repository.

### Run a single calibrated cyclone
```
python scripts/run_fani.py
```

### Run all 15 calibrated cyclones
```
python scripts/run_all_cyclones.py
```
### Run an example script
```
python examples/run_fani.py
```
---
## 🧭 CCART Pipeline

```
┌────────────────────┐
│   IBTrACS Track    │
│   + CMIP6 (opt.)   │
└─────────┬──────────┘
│
▼
┌────────────────────┐
│  Hazard Module     │
│  (Windfield, HWE)  │
└─────────┬──────────┘
│
▼
┌────────────────────┐
│  Exposure Module   │
│ (District Geometry)│
└─────────┬──────────┘
│
▼
┌────────────────────┐
│  Impact Module     │
│ (Raw Losses)       │
└─────────┬──────────┘
│
▼
┌────────────────────┐
│ Calibration Module │
│ (DLNA Alignment)   │
└─────────┬──────────┘
│
▼
┌────────────────────┐
│  Final Outputs     │
│  (District Losses) │
└────────────────────┘
```
---

## **Usage**

CCART v1.2 is built around reproducible, metadata‑driven workflows.
All cyclone analyses are executed through the scripts included in the repository, which handle the full end‑to‑end pipeline automatically.

### What the scripts do
- load cyclone metadata
- build the CLIMADA hazard
- extract district‑level exposure
- compute raw physical losses
- apply DLNA calibration
- generate district‑level outputs
- update the national master dataset

### Where to explore the workflow
You can inspect or modify the reproducible cyclone scripts in:
```
scripts/
```
For lightweight demonstration and experimentation, use the example scripts in:
```
examples/
```
These examples show how to run a cyclone, inspect outputs, and explore intermediate diagnostics.
---

## 🔬 Scientific Notes: Understanding `raw_to_dlna_ratio`

CCART uses a transparent, reproducible calibration step to align CLIMADA’s **raw physical loss estimates** with **observed DLNA/PDNA totals** for each cyclone.

This is expressed through a simple but powerful scaling factor:
`raw_to_dlna_ratio = DLNA_total / raw_climada_loss`

Why this ratio exists

**CLIMADA’s raw impact engine computes losses using:**

- windfield intensity
- exposure (LitPop)
- vulnerability curves

However, raw physical losses rarely match **observed** post‑disaster assessments because DLNAs include:
- indirect losses
- infrastructure damage
- service disruption
- agriculture and livelihood impacts
- reporting and valuation differences

The ratio corrects for these structural gaps.

**How CCART applies the ratio**

For each cyclone:
- Compute **raw_climada_loss** (sum of district‑level raw losses).
- Retrieve **DLNA_total** from official/state reports.
- Compute the scaling factor `raw_to_dlna_ratio`.
- Multiply each district’s raw loss by this factor:

`loss_usd_calibrated = loss_usd_raw * raw_to_dlna_ratio`

This preserves **spatial patterns** from physics while matching **total observed losses**.

**Why this method is scientifically defensible**
- It maintains **physical gradients** from the hazard field.
- It avoids arbitrary redistribution or manual adjustments.
- It ensures **district‑level losses sum exactly** to DLNA totals.
- It is reproducible, deterministic, and transparent.
- It allows cross‑cyclone comparability (v1.1’s 15‑event dataset).

**Interpreting the ratio**
- A ratio > 1 means CLIMADA under‑estimated losses (common for infrastructure‑heavy states).
- A ratio < 1 means CLIMADA over‑estimated losses (rare, usually exposure‑driven).
  - Ratios vary by cyclone due to differences in:
  - track geometry
  - exposure distribution
  - vulnerability of built environment
  - DLNA methodology

**Where the ratio appears in CCART**
- `district_relationships_master.csv`
- `cyclone_level_summary.csv`
- All example scripts in `scripts/`
- The calibration module inside `ccart/engine.py`
---

## ⚠️ Known Limitations

- **Exposure is proxy‑based.** We rely on litpop and other proxies; results depend on proxy quality and spatial resolution.
- **District‑level calibration.** DLNA values are aggregated and may not capture local variations in impact.
- **Windfield simplifications.** CLIMADA’s parametric wind model may differ from high‑resolution dynamical simulations.
- **No flood or storm‑surge module yet.** The current version models wind impacts only.
- **Historical bias.** Outputs depend on IBTrACS track accuracy and reporting quality.
- **Not a substitute for engineering studies.** CCART provides indicative risk patterns, not site‑specific structural assessments.

---

## 🌍 Why CCART?

India faces increasing cyclone risk, yet district-level impact intelligence remains fragmented, opaque, and hard to reproduce.  
CCART was built to change that.

This toolkit provides:

- Transparent, calibrated cyclone loss estimates at the district level  
- Reproducible workflows built on open data and open-source tools  
- A modular pipeline for hazard, exposure, impact, and calibration  
- A foundation for future expansion into multi-hazard and future-climate scenarios  

CCART is designed for researchers, analysts, and institutions seeking credible, scalable climate risk diagnostics for India.

---

## 🧭 Roadmap

### **v1.2 — Multi‑State Calibration**
- cross‑state harmonization for cyclones affecting multiple states  
- optional unified scaling for multi‑state events  
- exposure‑ or hazard‑weighted blending for state‑level calibration  

### **v2.0 — Synthetic Cyclone Expansion**
- synthetic track generation to extend beyond historical events  
- climate‑conditioned hazard scenarios for long‑term shifts  
- return‑period curves for probabilistic risk layers  

### **v3.0 — QGIS‑Based Machine Learning for TCFD Damage Estimation**
- high‑resolution proxy layers (nightlights, land use, infrastructure density, etc.)  
- ML models to estimate local damage where DLNA data is unavailable  
- QGIS‑ready outputs for site‑level TCFD and adaptation assessments  

---

## 📂 Data Sources

CCART relies on a combination of open datasets and curated inputs.  
Large datasets are **not bundled** with this repository to keep the project lightweight.

### 🌪️ Tropical Cyclone Tracks (IBTrACS)

The full IBTrACS dataset can be downloaded from NOAA:  
https://www.ncei.noaa.gov/products/international-best-track-archive

Place the netcdf file at: 
`data/IBTRACS.ALL.v04r01.nc`

### 🗺️ Administrative Boundaries

CCART requires district‑level administrative boundaries for hazard, exposure, and impact aggregation.

Place the national‑level GeoJSON or shapefile in:
`data/INDIA_DISTRICTS.geojson`

### 📊 DLNA / PDNA Calibration Inputs

DLNA/PDNA totals are required for cyclone‑level calibration.
These files are not included due to licensing restrictions.

Place cleaned DLNA/PDNA summaries in:
`data/dlna/<cyclone>.xlsx`

For example:
`data/dlna/fani.xlsx`

`data/dlna/yaas.xlsx`

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
Pednekar, K. (2026). A transparent, reproducible framework for district‑level tropical cyclone impact modelling in India using CLIMADA, DLNA calibration, and Hazard‑Weighted Exposure (HWE).
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

v1.2 – Metadata‑Driven, Multi‑State Architecture

- Introduced a fully metadata‑driven cyclone workflow (single script, multiple cyclones)
- Added multi‑state calibration logic for cyclones affecting more than one state
- Separated state‑agnostic CCART engine from state‑specific configuration
- Upgraded all cyclone scripts to the new v1.2 architecture
- Regenerated the full 15‑cyclone national dataset using the new engine
- Integrated batch runner for end‑to‑end national automation
- Ensured SID‑anchored consistency across all outputs
- Refined directory structure for clarity, reproducibility, and future expansion


v1.1 – Pan‑India 15‑Cyclone Calibrated Release

- Added **15 calibrated historical cyclones** (2009–2021) covering both Bay of Bengal and Arabian Sea basins
- Added **district_relationships_master.csv** (full India, 15‑event calibrated dataset)
- Added **cyclone_level_summary.csv** (cross‑cyclone diagnostics: raw loss, calibrated loss, DLNA ratios)
- Added **export‑enabled scripts** for all 15 cyclones under a unified CCART v1.0 engine
- Added **SID‑anchored metadata** for every cyclone
- Standardized all cyclone workflows for reproducibility and transparency
- Improved documentation and repository structure for national‑scale analysis

  🌀 Cyclones Included in v1.1

  CCART v1.1 expands the platform from 5 calibrated cyclones to a full
  15‑cyclone national dataset covering all major Indian landfalls from 2009–2021.

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


v1.0 – Multi‑cyclone calibrated release

- Added Amphan, Fani, Nisarga, Phailin, and Tauktae
- Introduced Hazard–Weighted Exposure (HWE)
- Implemented hazard floor and inland clipping
- Added district‑level calibrated loss tables
- Added standardized cyclone maps and narratives
- Published CCART v1.0 slide carousel
- Repository restructured for clarity and reproducibility


v0.9 – Fani baseline

- Initial prototype of CCART
- First implementation of hazard ingestion, exposure, and vulnerability
- Early calibration workflow


      
