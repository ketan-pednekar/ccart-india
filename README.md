# CCART: Cyclone Calibration and Risk Toolkit (India)

<p align="left">
  <img src="https://img.shields.io/badge/Python-3.10%2B-blue" />
  <img src="https://img.shields.io/badge/License-MIT-yellow" />
  <img src="https://img.shields.io/badge/Status-Active-brightgreen" />
  <img src="https://img.shields.io/badge/Release-v1.3-brightgreen" />
  <img src="https://img.shields.io/github/last-commit/ketan-pednekar/ccart-india" />
  <img src="https://img.shields.io/github/issues/ketan-pednekar/ccart-india" />
  <img src="https://img.shields.io/github/stars/ketan-pednekar/ccart-india?style=social" />
</p>

---

## CCART v1.3 — Pan‑India Multi‑State Automated Release

**CCART** is a transparent, reproducible, and India‑focused toolkit for district‑level tropical cyclone impact modelling.  
It integrates **CLIMADA’s open‑source hazard engine** with **DLNA‑aligned calibration** to generate consistent, physics‑based loss estimates across all Indian districts.

Version **v1.3** introduces:

- A fully automated **multi‑state cyclone pipeline**
- A clean, duplicate‑free **national master dataset**
- Reproducible **district‑level hazard–exposure–loss outputs**
- Standardized **SID‑anchored cyclone metadata**
- Improved **coastline clipping** and inland attenuation logic
- A stable architecture for future **synthetic cyclone simulation (v3.0)**

---

## Key Features

### 🔹 Reproducible Cyclone Modelling
- Built on CLIMADA’s hazard engine  
- Deterministic, transparent, and version‑controlled  
- No black‑box components

### 🔹 DLNA‑Aligned Calibration
- Uses state‑reported DLNA totals  
- Ensures district‑level losses sum to official values  
- Enables comparison with literature‑based loss estimates

### 🔹 Pan‑India District Coverage
- 789 districts  
- Multi‑state cyclone footprints  
- Automated state‑wise exports

### 🔹 Clean National Master File (v1.3)
Each cyclone contributes one row per district, containing:

- `sid`  
- `cyclone_name`  
- `year`  
- `state`  
- `District`  
- `loss_usd_raw`  
- `HWE_weight_norm`  
- `loss_usd_hwe`  
- `dlna_total`  
- `dist_to_coast_km`  
- `is_inland`

The v1.3 master file is **duplicate‑free**, **schema‑consistent**, and ready for downstream analysis.

---

**The goal is to build a national, open, reproducible cyclone‑impact platform that researchers, engineers, and policymakers can extend collaboratively.**

---

## 📘 Overview

CCART integrates the full cyclone‑impact workflow into a transparent, deterministic, and reproducible pipeline:

- **IBTrACS → CLIMADA hazard generation**
- **District‑level hazard diagnostics**
- **LitPop exposure extraction**
- **Coastal proximity and inland‑attenuation logic**
- **Tropical cyclone vulnerability curves**
- **Raw CLIMADA impact engine**
- **DLNA calibration** (state‑level, SID‑anchored)
- **Hazard–Weighted Exposure Engine (HWE)**
- **Automated multi‑cyclone runner** for all historical events (v1.3)

Version **v1.3** introduces:

- A unified **metadata‑driven multi‑state pipeline**
- Clean, duplicate‑free **national master dataset**
- Standardized **SID‑anchored cyclone metadata**
- Improved **coastline clipping** and inland logic
- Reproducible **per‑cyclone and national exports**
- A stable foundation for **synthetic cyclone simulation (v3.0)**

The engine is designed to be:

- **transparent** — no black‑box steps  
- **reproducible** — deterministic hazard + exposure + vulnerability  
- **extensible** — multi‑state, multi‑cyclone, multi‑hazard  
- **collaboration‑ready**

---
## 📁 Repository Structure (v1.3)

```text
ccart-india/
│
├── ccart/                              # Core Python package
│   ├── pipeline_v1_3.py                # v1.3 multi-state engine (metadata-driven)
│   ├── utils.py
│   ├── viz.py
│   └── __init__.py
│
├── scripts/                            # All cyclone scripts (v1.2 + v1.3)
│   ├── batch_runner_v1_3.py            # Automated batch runner (v1.3)
│   │
│   ├── run_aila_v1_3.py                # v1.3 cyclone scripts
│   ├── run_amphan_v1_3.py
│   ├── run_bulbul_v1_3.py
│   ├── run_fani_v1_3.py
│   ├── run_gaja_v1_3.py
│   ├── run_helen_v1_3.py
│   ├── run_hudhud_v1_3.py
│   ├── run_laila_v1_3.py
│   ├── run_nisarga_v1_3.py
│   ├── run_ockhi_v1_3.py
│   ├── run_phailin_v1_3.py
│   ├── run_tauktae_v1_3.py
│   ├── run_titli_v1_3.py
│   ├── run_vardah_v1_3.py
│   └── run_yaas_v1_3.py
│
│   ├── batch_runner.py                 # v1.2 legacy batch runner
│   │
│   ├── run_aila.py                     # v1.2 cyclone scripts (kept for reproducibility)
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
├── examples/                           # Example scripts and notebooks (unchanged)
│   └── CCART_v1.2_Diagnostics.ipynb
│
├── data/
│   ├── cyclone_metadata.csv
│   ├── india_districts.geojson
│   ├── coastl_ind.shp
│   ├── IBTrACS.ALL.v04r01.nc
│   ├── district_relationships_master_v1_3.csv
│   ├── district_relationships_master_v1_2.csv
│   └── cyclone_level_summary.csv
│
├── outputs/                            # Auto-generated outputs (empty in repo)
│
├── docs/
│
├── README.md
├── LICENSE
└── requirements.txt
---
## ⚙️ Key Features (v1.3)

- **CLIMADA-based hazard builder**  
  IBTrACS → TropCyclone

- **District-level hazard diagnostics**  
  - Maximum wind speed  
  - Mean wind speed  
  - Centroid distance to track  
  - Inland clipping logic

- **LitPop exposure extraction**  
  - Compatible with all Indian states and UTs  
  - Modular and reproducible

- **Coastal proximity logic**  
  - Distance-to-coast (in kilometers)  
  - Inland/coastal flag for attenuation

- **India-specific vulnerability curves**  
  - Housing  
  - Health  
  - Infrastructure

- **Raw CLIMADA impact engine**  
  - Physics-driven loss estimation  
  - Deterministic and transparent

- **DLNA calibration module**  
  - State-level alignment  
  - SID-anchored  
  - Multi-state aware

- **Hazard–Weighted Exposure Engine (HWE)**  
  - Spatial allocation of calibrated losses  
  - Normalized exposure weighting

- **Metadata-driven multi-cyclone runner**  
  - Supports all 14 calibrated cyclones  
  - Fully automated pipeline

- **Clean v1.3 national master dataset**  
  - District-level hazard, exposure, impact, calibration  
  - Duplicate-free and schema-consistent  
  - Ready for downstream analysis

- **Legacy v1.2 scripts preserved**  
  - Full reproducibility  
  - Transparent version history
---
## Installation

```bash
pip install -r requirements.txt
```
## 🚀 Quickstart (v1.3)

CCART v1.3 provides a fully automated, metadata‑driven pipeline for running calibrated cyclone analyses across India.  
You can run a single cyclone or all 14 calibrated cyclones using the updated `_v1_3` scripts.

### ▶️ Run a single calibrated cyclone (v1.3)

```bash
python scripts/run_fani_v1_3.py
```
### ▶️ Run all 14 calibrated cyclones (v1.3)

```bash
python scripts/run_all_cyclones.py
```
### ▶️ Run a single calibrated cyclone (v1.2 legacy)
```bash
python scripts/run_fani.py
```
### ▶️ Run an example script (v1.1 legacy)
```bash
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
## **Usage (v1.3)**

CCART v1.3 is built around a fully automated, metadata‑driven workflow.  
All cyclone analyses are executed through the `_v1_3` scripts, which run the complete end‑to‑end pipeline:

- hazard generation  
- exposure extraction  
- raw impact computation  
- DLNA calibration  
- district‑level output generation  
- national master dataset updates  

### What the v1.3 scripts do

- Load cyclone metadata (SID, name, year, DLNA totals)  
- Build the CLIMADA windfield hazard  
- Extract district‑level LitPop exposure  
- Compute raw physical losses  
- Apply DLNA calibration (state‑level, SID‑anchored)  
- Allocate calibrated losses using HWE  
- Export per‑cyclone and per‑state outputs  
- Append results to the **v1.3 national master dataset**

### Where to explore the workflow

The full v1.3 pipeline scripts are located in:

`scripts/`

These include:

- `batch_runner_v1_3.py` — run all calibrated cyclones  
- `run_<cyclone>_v1_3.py` — run a single cyclone  

For lightweight experimentation or legacy reproducibility, use the v1.2 examples:

`examples/`

These demonstrate how to run a cyclone, inspect outputs, and explore intermediate diagnostics.
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

### **v1.3 — Multi‑State, Metadata‑Driven Pipeline**
- unified multi‑state calibration for all 14 historical cyclones  
- metadata‑driven batch runner (`batch_runner_v1_3.py`)  
- clean national master dataset (district‑level hazard, exposure, impact, calibration)  
- improved inland logic, coastal proximity scoring, and exposure extraction  
- reproducible v1.2 scripts preserved for transparency  

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

### v1.3 – Automated, Metadata‑Driven Multi‑Cyclone Engine (Current)

- Introduced the **v1.3 multi‑state engine** (`pipeline_v1_3.py`) with metadata‑driven execution  
- Added **batch_runner_v1_3.py** for automated national‑scale cyclone processing  
- Standardized all cyclone scripts to the new `_v1_3` architecture  
- Integrated **coastal proximity logic**, improved inland clipping, and refined exposure extraction  
- Generated a **clean national master dataset (v1.3)** with district‑level hazard, exposure, impact, and calibration  
- Ensured strict **SID‑anchored consistency** across all 14 calibrated cyclones  
- Preserved all **v1.2 legacy scripts** for transparency and reproducibility  
- Refined repository structure for clarity, modularity, and future multi‑hazard expansion  


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
