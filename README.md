# CCART
CCART is a country-agnostic physical climate risk framework. India is the reference implementation. The architecture is designed so that any country can be added by providing local boundary files and climate data — the pipeline handles the rest. CCART-UK is planned as the first international extension.

# CCART v3 — Public Modular Release (Cyclone + OSM Vizag)

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

## Overview (v3)

CCART v3 introduces a clean, modular, and fully open repository structure designed for transparency, collaboration, and future multi‑hazard expansion. This release focuses on architecture, not a new cyclone engine.

The scientific engine remains CCART v2, which continues to power synthetic cyclone generation, hazard modelling, calibration, and HWE allocation.

The v3 repository includes:
- cyclone module (Vizag‑focused workflow)
- OSM building extraction for Vizag
- hazard simulation wrapper (`hazard_simulated_v2.py`)
- exposure, impact, vulnerability, calibration, and HWE modules
- visualization utilities (`viz_v2.py`)
- synthetic batch runner (`run_synthetic_batch.py`)
- clean `.gitignore` and reproducible folder structure
- example notebook for cyclone landfall + density maps

Large datasets, QGIS projects, and synthetic catalogue outputs are intentionally excluded to keep the repository lightweight.

---

## 📘 Documentation (v3)

CCART now includes a clean, modular documentation structure inside the `docs/` folder.  
These pages explain the scientific logic, modelling philosophy, and reproducible workflows behind CCART.

### 🔹 Key Documentation Pages

- **Cyclone Methodology (v2 Engine)**  
  `docs/methodology/cyclone_methodology.md`  
  A complete explanation of the synthetic cyclone generator, track perturbations, hazard engine, and physical reasoning behind CCART.

- **Vizag Design Cyclone Case Study**  
  `docs/case_studies/vizag_design_cyclone.md`  
  A full end‑to‑end example showing how CCART selects a representative design cyclone from 1100+ synthetic storms and generates a CLIMADA‑compatible hazard footprint.  
  Includes:
  - header figure  
  - workflow diagram  
  - reproducibility steps  
  - limitations  
  - uncertainty & sensitivity analysis  

- **OSM Exposure Extraction (Vizag)**  
  `docs/methodology/osm_extraction_vizag.md` *(optional placeholder)*  
  Explains how OSM building footprints are extracted and prepared for hazard overlay.

### 🔹 Documentation Structure

```
docs/
   methodology/
       cyclone_methodology.md
       osm_extraction_vizag.md
   case_studies/
       vizag_design_cyclone.md
   images/
       vizag_design_cyclone_header.png
```

The documentation is designed to be:
- **transparent** — every assumption is explicit  
- **reproducible** — every workflow can be replicated  
- **physically grounded** — no black‑box shortcuts  
- **extensible** — ready for flood + heat modules in v4  

---

## Relationship Between v2 and v3

### v2 = scientific engine
- synthetic generator
- hazard engine
- calibration
- HWE
- multi‑scenario batch runner

### v3 = repository architecture
- public release
- modular package structure
- OSM + cyclone integration
- ready for flood + heat modules in v4

The full v2 synthetic catalogue (baseline / warm SST / high‑end) is not bundled, but the complete v2 pipeline is available for users to generate their own catalogues.

---

## Next Steps

The v3 structure prepares CCART for:
- flood module integration (v4)
- heat module (tasmax anomalies)
- national exposure model
- multi‑hazard risk layers
- future‑climate scenario expansion

---

## **CCART v2 — Synthetic Cyclone Impact Engine (2026)**

A clean, modular, and fully reproducible engine for generating synthetic tropical cyclone impacts across India.

CCART integrates **CLIMADA’s open‑source hazard engine, DLNA‑aligned calibration,** and a **physics‑consistent synthetic track generator** to produce district‑level cyclone risk intelligence that is transparent, extensible, and ready for national‑scale analysis.

**CCART v2** marks a major evolution of the platform — from a calibrated historical toolkit (v1.x) to a probabilistic, scenario‑driven synthetic cyclone engine.
It introduces a complete end‑to‑end workflow that generates realistic cyclone tracks, builds hazard footprints, computes calibrated losses, and exports district‑level maps and metadata for every synthetic event.

This release is designed for researchers, analysts, and institutions seeking **credible, open, and reproducible climate‑risk diagnostics** for India, and for anyone who believes that transparent modelling is essential for adaptation planning.

## 🌟 What’s New in v2
CCART v2 is a major leap forward — transforming the toolkit from a calibrated historical engine into a **probabilistic, scenario‑driven synthetic cyclone platform**.
This release introduces a clean, modular, and fully automated workflow that generates realistic cyclone tracks, builds hazard footprints, computes calibrated losses, and exports district‑level maps for every synthetic event.

**🔹 1. Synthetic Cyclone Generator (v2)**
A redesigned generator that produces physics‑consistent synthetic tracks using:
- historical analogue clustering
- track‑shape perturbations
- curvature adjustments
- translation‑speed variety (new)
- intensity peak/decay/timing perturbations
This creates a diverse, realistic catalogue of storms beyond the historical record.

**🔹 2. Translation‑Speed Variety (New in v2)**
A key realism lever added in v2:
- slower storms → more rainfall + coastal concentration
- faster storms → deeper inland penetration
- more diverse hazard footprints
This significantly improves the physical behaviour of synthetic tracks.

**🔹 3. Improved Hazard Engine (v2)**
A refined CLIMADA‑based hazard wrapper with:
- better inland decay
- bounding‑box hazard clipping
- district‑level hazard statistics
- peak wind diagnostics
- inland/coastal classification
The hazard footprint is now more stable, efficient, and physically interpretable.

**🔹 4. Exposure–Hazard Clipping**
A major performance improvement:
- only exposure points inside the hazard footprint are processed
- reduces computation by 80–90%
- preserves spatial accuracy
This makes large synthetic catalogues feasible.

**🔹 5. DLNA‑Aligned Calibration (Coastal‑Only)**
Calibration is now applied only to coastal districts, ensuring:
- scientific consistency
- stable national‑scale loss estimates
- realistic inland decay patterns
This avoids over‑calibration in inland regions.

**🔹 6. Hazard‑Weighted Exposure (HWE)**
A refined spatial allocation method that:
- preserves hazard gradients
- distributes calibrated losses proportionally
- produces interpretable district‑level patterns
HWE is now the default allocation engine for all synthetic events.

**🔹 7. Clean, Reproducible Output Structure**
Each synthetic run now includes:
- `impact.gpkg`
- `metadata.json`
- district‑level maps
- state‑level summaries
- hazard diagnostics
This structure is designed for catalogue‑level analysis and long‑term archival.

**🔹 8. Batch Catalogue Generation**
A fully automated batch runner that:
- generates 10, 50, 100, or 1000 synthetic storms
- appends results to synthetic_summary.csv
- supports return‑period curves and hotspot analysis
This is the foundation for national‑scale probabilistic risk layers.

**🔹 9. Fully Transparent, Fully Open**
Every step — hazard, exposure, impact, calibration, HWE — is:
- deterministic
- reproducible
- inspectable
- open‑source
No black‑box components.
No hidden assumptions.

---

## Key Features (v2)
A clean, modular, and fully reproducible cyclone‑impact engine designed for India’s district‑level risk landscape.
CCART v2 brings together hazard science, geospatial analysis, and transparent calibration into a single, deterministic workflow.

---
**🔹 Synthetic Cyclone Generator**
A physics‑consistent generator that produces realistic synthetic tracks using:
- historical analogue clustering
- track‑shape perturbations
- curvature adjustments
- translation‑speed variety (new)
- intensity peak/decay/timing perturbations
This creates a diverse catalogue of storms that extend beyond the historical record while remaining grounded in real cyclone behaviour.

---
**🔹 v2 Hazard Engine (Windfield + Inland Decay)**
A refined CLIMADA‑based hazard wrapper with:
- improved inland decay
- bounding‑box hazard clipping for efficiency
- district‑level hazard statistics (max wind, inland flag, coastal proximity)
- peak wind diagnostics for every synthetic event
The hazard footprint is now more stable, efficient, and physically interpretable.

---
**🔹 Exposure–Hazard Clipping**
A major performance improvement:
- only exposure points inside the hazard footprint are processed
- reduces computation by 80–90%
- preserves spatial accuracy
This makes large synthetic catalogues (100–1000 storms) computationally feasible.

---
**🔹 DLNA‑Aligned Calibration (Coastal‑Only)**
Calibration is applied only to coastal districts, ensuring:
- scientific consistency
- realistic inland decay
- stable national‑scale loss estimates
This avoids over‑calibration in inland regions and keeps the model physically meaningful.

---
**🔹 Hazard‑Weighted Exposure (HWE)**
A refined spatial allocation method that:
- preserves hazard gradients
- distributes calibrated losses proportionally
- produces interpretable district‑level patterns
HWE is now the default allocation engine for all synthetic events.

---
**🔹 Batch Catalogue Generation**
A fully automated batch runner that:
- generates 10, 50, 100, or 1000 synthetic storms
- appends results to `synthetic_summary.csv`
- supports return‑period curves, exceedance probability curves, and hotspot analysis
This is the foundation for national‑scale probabilistic risk layers.

---
**🔹 Fully Transparent, Fully Open**
Every step — hazard, exposure, impact, calibration, HWE — is:
- deterministic
- reproducible
- inspectable
- open‑source
No black‑box components.
No hidden assumptions.
No proprietary dependencies.

---
**The goal is to build a national, open, reproducible cyclone‑impact platform that researchers, engineers, and policymakers can extend collaboratively.**

---

## 📘 Overview (v2)

CCART v2 introduces a fully automated **synthetic cyclone impact engine** that extends CCART beyond the historical record into probabilistic, scenario‑driven climate‑risk analysis. The v2 pipeline is clean, modular, and fully reproducible, integrating hazard, exposure, impact, calibration, and visualization into a deterministic workflow.

The v2 engine includes:

- **Synthetic cyclone generation** using historical analogue clustering
- **Track‑shape perturbations** (curvature, translation‑speed variety, intensity shifts)
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
├── ccart/                                   # CCART v2 engine (active)
│   │
│   ├── synthetic/                           # Synthetic cyclone generation (v2)
│   │   ├── run_synthetic_cyclone_v2.py      # Run one synthetic cyclone
│   │   ├── run_synthetic_batch.py           # Generate full synthetic catalogue
│   │   ├── generator.py                     # Track generator + analogue logic
│   │   └── __init__.py
│   │
│   ├── viz/                                 # Mapping + visualisation
│   │   ├── viz_v2.py                        # District/state choropleths
│   │   └── __init__.py
│   │
│   ├── hazard.py                            # Hazard engine (windfield + decay)
│   ├── hazard_simulated_v2.py               # CLIMADA-based hazard wrapper
│   ├── exposure.py                          # LitPop + exposure utilities
│   ├── vulnerability.py                     # Vulnerability functions
│   ├── impact.py                            # Impact computation
│   ├── hwe.py                               # Hazard-Weighted Exposure engine
│   ├── calibration.py                       # DLNA coastal calibration
│   ├── __init__.py
│
├── legacy/                                  # CCART v1.3 historical engine
│   ├── pipeline_v1_3.py
│   ├── utils.py
│   ├── viz.py
│   └── ...
│
├── archive/                                 # Old scripts, prototypes, v1.2 code
│   └── ...
│
├── scripts/                                 # Helper scripts (optional)
│   └── ...
│
├── data/                                    # Required datasets (not bundled)
│   ├── IBTrACS.ALL.v04r01.nc
│   ├── india_districts.geojson
│   ├── coastal_ind.shp
│   └── ...
│
├── outputs/                                 # Auto-generated outputs
│   │
│   ├── v1.2/                                # Historical calibrated outputs (v1.2)
│   │   └── ...
│   │
│   ├── v1.3/                                # Historical calibrated outputs (v1.3)
│   │   └── ...
│   │
│   ├── synthetic_runs_multi/                # v2 synthetic catalogue (multi-scenario)
│   │   ├── master_summary.csv               # Combined summary for all runs
│   │   │
│   │   ├── baseline/                        # Baseline synthetic runs
│   │   │   ├── run_001/
│   │   │   ├── run_002/
│   │   │   └── ...
│   │   │
│   │   ├── warm_sst/                        # Warm SST scenario runs
│   │   │   ├── run_001/
│   │   │   ├── run_002/
│   │   │   └── ...
│   │   │
│   │   ├── high_end/                        # High-end climate scenario runs
│   │   │   ├── run_001/
│   │   │   ├── run_002/
│   │   │   └── ...
│   │
│   └── diagnostics/                         # Plots, logs, maps
│
├── docs/                                    # Documentation + methodology
├── examples/                                # Example workflows
├── notebooks/                               # Jupyter notebooks
├── analysis/                                # Additional analysis scripts
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
outputs/synthetic_runs_multi/
    master_summary.csv

    baseline/
        run_001/
        run_002/
        ...

    warm_sst/
        run_001/
        run_002/
        ...

    high_end/
        run_001/
        run_002/
        ...
```
Each run folder contains:
- `impact.gpkg`
- district‑level and state‑level losses
- hazard footprint
- calibration + HWE outputs
- metadata JSON
- maps
The `master_summary.csv` file aggregates all runs across all scenarios for catalogue‑level analysis.

---
## 🧭 CCART V2 Pipeline

```
┌──────────────────────────────────────────┐
│      Synthetic Track Engine (v2)         │
│  • Analogue selection                    │
│  • Track-shape perturbations             │
│  • Curvature adjustments                 │
│  • Translation-speed variety (new)       │
│  • Intensity peak/decay/timing shifts    │
└───────────────────────┬──────────────────┘
                        │
                        ▼
┌──────────────────────────────────────────┐
│            Hazard Engine v2              │
│   • CLIMADA windfield                    │
│   • Improved inland decay                │
│   • Bounding-box hazard clipping         │
│   • District-level hazard stats          │
└───────────────────────┬──────────────────┘
                        │
                        ▼
┌──────────────────────────────────────────┐
│        Exposure–Hazard Clipping          │
│   • District geometry mask               │
│   • Efficient exposure filtering         │
└───────────────────────┬──────────────────┘
                        │
                        ▼
┌──────────────────────────────────────────┐
│              Impact Module               │
│        • Raw CLIMADA losses              │
│        • Hazard diagnostics              │
└───────────────────────┬──────────────────┘
                        │
                        ▼
┌──────────────────────────────────────────┐
│      DLNA-Aligned Calibration (Coastal)  │
│   • Coastal-only scaling                 │
│   • Preserves inland decay               │
└───────────────────────┬──────────────────┘
                        │
                        ▼
┌──────────────────────────────────────────┐
│        Hazard-Weighted Exposure (HWE)    │
│   • Spatial allocation of calibrated loss│
│   • Preserves hazard gradients           │
└───────────────────────┬──────────────────┘
                        │
                        ▼
┌──────────────────────────────────────────┐
│              Final Outputs               │
│   • District-level GPKG                  │
│   • State summaries                      │
│   • Maps (PNG)                           │
│   • Metadata (JSON)                      │
│   • Batch catalogue (CSV)                │
└──────────────────────────────────────────┘

```
---
## **Usage (v2)**

CCART v2 is built around a clean, modular workflow.
All synthetic cyclone analyses are executed through the `ccart/synthetic/` scripts:

The v2 engine automatically handles:
- synthetic track generation
- hazard footprint creation
- exposure–hazard clipping
- raw impact computation
- coastal‑only DLNA calibration
- Hazard‑Weighted Exposure (HWE) allocation
- district‑level and state‑level map export
- metadata logging
- multi‑scenario catalogue generation

---

### **What the v2 scripts do**
- Generate a synthetic cyclone track
- Apply track‑shape perturbations (curvature, translation speed, intensity variety)
- Build the v2 hazard footprint
- Clip hazard to district geometry
- Compute raw CLIMADA losses
- Apply coastal‑only DLNA calibration
- Allocate calibrated losses using HWE
- Export maps and impact tables
- Write run‑level metadata
- Append results to master_summary.csv (multi‑scenario batch mode)
---

### Where to explore the workflow

```
ccart/
    synthetic/      # Track generation + batch runner
    hazard.py       # Hazard engine (windfield + inland decay)
    exposure.py     # Exposure extraction + clipping
    impact.py       # Raw CLIMADA impact
    calibration.py  # DLNA coastal calibration
    hwe.py          # Hazard-Weighted Exposure
    viz/            # District/state maps
```
These scripts demonstrate how to:
- generate synthetic tracks
- build hazard footprints
- compute raw and calibrated losses
- allocate losses spatially
- export maps and metadata
- generate multi‑scenario catalogues

---

## ⚠️ Known Limitations

- **Exposure is proxy‑based.** 
  We rely on litpop and other proxies; results depend on proxy quality and spatial resolution.
- **District‑level calibration.** 
  DLNA values are aggregated and may not capture local variations in impact.
- **Windfield simplifications.** 
  CLIMADA’s wind model is robust but may differ from high‑resolution dynamical simulations, especially for extreme events.
- **Wind‑only impact modelling.**
  v2 currently models wind impacts only. Flood, rainfall, and storm‑surge modules are planned for future releases.
- **Historical bias in analogue selection.**  
  Synthetic tracks depend on IBTrACS track accuracy and reporting quality; historical biases can influence analogue clusters.
- **Not a substitute for engineering studies.**
  CCART provides indicative district‑level risk patterns, not site‑specific structural assessments.
- **Synthetic tracks follow historical geometry envelopes.**
  v2 includes perturbations (curvature, translation speed, intensity variety), but full Monte‑Carlo geometry expansion is planned for v2.1.

---

## 🌍 Why CCART?

India faces rising cyclone risk, yet district‑level impact intelligence remains fragmented, opaque, and difficult to reproduce.
CCART was built to change that.

This toolkit provides:

- **Transparent, calibrated cyclone loss estimates** at the district level
- **Reproducible, open workflows** built entirely on public data and open‑source tools
- **A modular pipeline** covering hazard, exposure, impact, calibration, and spatial allocation
- **Scenario‑driven synthetic catalogues** for probabilistic risk analysis
- **A foundation for future expansion** into multi‑hazard and future‑climate scenarios

CCART is designed for researchers, analysts, and institutions seeking **credible, scalable, and fully transparent climate‑risk diagnostics for India-** a platform that can evolve into a national public good.

---
## 🧭 Roadmap

### v2.0 — Synthetic Cyclone Expansion (Current Release)
- analogue‑based synthetic track generation
- track‑shape perturbations (curvature, translation speed, intensity variety)
- calibrated wind‑impact modelling across all coastal states
- district‑level hazard, exposure, impact, and HWE allocation
- multi‑scenario synthetic catalogues (baseline, warm SST, high‑end)
- reproducible outputs for probabilistic risk layers

---
### v3.0 — High‑Resolution & ML‑Driven Cyclone Risk
*(Refining cyclone impacts before expanding into multi‑hazard)*
- high‑resolution proxy layers (nightlights, land use, infrastructure density)
- machine‑learning models for local damage estimation where DLNA data is unavailable
- QGIS‑ready outputs for TCFD, site‑level screening, and infrastructure planning
- refined cyclone‑only risk layers for adaptation and insurance use‑cases

---
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
Pednekar, K. (2026). CCART: CCART: A Country-Agnostic Physical Climate Risk Framework —
India Implementation. github.com/ketan-pednekar/ccart-india.
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
- Developed with AI-assisted tooling for debugging and documentation.

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
- Introduces a physics‑consistent synthetic cyclone generator with analogue clustering, curvature perturbations, translation‑speed variety, and intensity variation.
- Adds the full v2 hazard engine with improved inland decay, bounding‑box clipping, and district‑level hazard diagnostics.
- Implements district‑level hazard, exposure, impact, calibration, and HWE allocation for every synthetic event.
- Supports multi‑scenario synthetic catalogues (baseline, warm SST, high‑end) for probabilistic and climate‑conditioned risk analysis.
- Adds run‑level metadata, diagnostics, maps, and reproducible outputs for each synthetic cyclone.
- Provides clean v2 scripts:
  `run_synthetic_cyclone_v2.py`
  `run_synthetic_batch.py`
  `generator.py`
  `hazard.py`
  `calibration.py`
  `hwe.py`
  `viz_v2.py`
- Establishes a modular, transparent v2 workflow for national‑scale synthetic risk modelling.

Note:  
v2 focuses on **synthetic cyclone modelling**.
Historical DLNA‑calibrated datasets remain available under **v1.2** and **v1.3** for transparency, reproducibility, and comparison.

---
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

---
### v1.2 – Metadata‑Driven, Multi‑State Architecture

- Introduced a fully metadata‑driven cyclone workflow (single script, multiple cyclones)  
- Added multi‑state calibration logic for cyclones affecting more than one state  
- Separated state‑agnostic CCART engine from state‑specific configuration  
- Upgraded all cyclone scripts to the new v1.2 architecture  
- Regenerated the full 15‑cyclone national dataset using the new engine  
- Integrated batch runner for end‑to‑end national automation  
- Ensured SID‑anchored consistency across all outputs  
- Refined directory structure for clarity, reproducibility, and future expansion  

---
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

---
### v1.0 – Multi‑Cyclone Calibrated Release

- Added Amphan, Fani, Nisarga, Phailin, and Tauktae  
- Introduced Hazard–Weighted Exposure (HWE)  
- Implemented hazard floor and inland clipping  
- Added district‑level calibrated loss tables  
- Added standardized cyclone maps and narratives  
- Published CCART v1.0 slide carousel  
- Repository restructured for clarity and reproducibility  

---
### v0.9 – Fani Baseline

- Initial prototype of CCART  
- First implementation of hazard ingestion, exposure, and vulnerability  
- Early calibration workflow       

---
