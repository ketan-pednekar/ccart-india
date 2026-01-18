# CCART: Cyclone Calibration and Risk Toolkit (India)

<p align="left">
  <img src="https://img.shields.io/badge/Python-3.10%2B-blue" />
  <img src="https://img.shields.io/badge/License-MIT-yellow" />
  <img src="https://img.shields.io/badge/Status-Active-brightgreen" />
  <img src="https://img.shields.io/badge/Release-v0.9-orange" />
  <img src="https://img.shields.io/github/last-commit/ketan-pednekar/ccart-india" />
  <img src="https://img.shields.io/github/issues/ketan-pednekar/ccart-india" />
  <img src="https://img.shields.io/github/stars/ketan-pednekar/ccart-india?style=social" />
</p>

**CCART v1.1 — Pan‑India 15‑Cyclone Calibrated Release**

A transparent, data‑driven platform for calibrated cyclone loss estimation to support climate risk decisions across India.

CCART is an open-source, modular engine for district-level tropical cyclone impact modelling across India.

Built on CLIMADA and anchored in transparent physical logic, CCART v1.0 introduces:

- **Multi‑cyclone calibration** (Amphan, Fani, Nisarga, Phailin, Tauktae)
- **District‑level hazard diagnostics**
- **Hazard–Weighted Exposure (HWE)** for spatial allocation
- **DLNA‑aligned calibration** for historical events
- **Reproducible, deterministic workflows** for hazard → exposure → vulnerability → impact

## What’s New in v1.1
- Added 15 calibrated historical cyclones (2009–2021)
- Added district_relationships_master.csv (full India, 15 events)
- Added cyclone_level_summary.csv (cross‑cyclone diagnostics)
- Added export‑enabled scripts for all cyclones
- Added SID‑anchored metadata for every event
- Standardized all cyclone workflows under CCART v1.0 engine
- Improved reproducibility and documentation

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

---

## 📁 Repository Structure

```
ccart/                      # Core Python package (hazard, exposure, impact, HWE, calibration)
    engine.py
    viz.py
    utils.py
    __init__.py

examples/                   # Fully reproducible cyclone scripts (all 15 events)
    run_aila.py
    run_laila.py
    run_phailin.py
    run_helen.py
    run_hudhud.py
    run_vardah.py
    run_ockhi.py
    run_titli.py
    run_gaja.py
    run_fani.py
    run_bulbul.py
    run_amphan.py
    run_nisarga.py
    run_tauktae.py
    run_yaas.py

data/                       # Lightweight sample + model outputs
    INDIA_DISTRICTS.geojson
    coastl_ind.shp
    cyclone_metadata.csv
    district_relationships_master.csv      # NEW in v1.1 (15‑cyclone calibrated dataset)
    cyclone_level_summary.csv              # NEW in v1.1 (cross‑cyclone diagnostics)

notebooks/                  # Example workflows and diagnostics
    CCART_Odisha_v0.9.ipynb
    CCART_PanIndia_Diagnostics.ipynb       # optional future addition

docs/                       # Documentation, figures, outreach materials

README.md
LICENSE
requirements.txt

```
---

## ⚙️ Key Features

- **CLIMADA-based hazard builder** (`IBTrACS → TropCyclone`)
- **District-level hazard diagnostics** (max/mean wind, centroid density)
- **LitPop exposure extraction** for any Indian state
- **Coastal tier classification** (Tier 1/2/3 + coastal score)
- **India-specific vulnerability curves** (Housing, Health, Infrastructure)
- **Raw CLIMADA impact engine**
- **DLNA calibration engine** (Fani v0.9 baseline)
- **Hazard–Exposure Weighting Engine (HWE)** for spatial allocation
- **Multi-cyclone runner** (historical + synthetic storms)

---
```
## Installation

```bash
pip install -r requirements.txt
```

## 🚀 Quickstart

Once installed, you can run a calibrated cyclone impact analysis with just a few lines of code:

```python
from ccart.engine import run_ccart

gdf = run_ccart(
    cyclone_name="Fani",
    storm_id="2019116N02090",
    ibtracs_path="data/IBTRACS.ALL.v04r01.nc",
    districts_path="data/INDIA_DISTRICTS.geojson",
    dlna_total=4.2e9,
    state_name="ODISHA"
)

print(gdf[["DIST_NAME", "loss_usd_raw", "loss_usd_calibrated"]])

```

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

To explore CCART in action, see `notebooks/CCART_Odisha_v0.9.ipynb` for a full example workflow.

A minimal example:

```python
from ccart import run_ccart_climada

gdf = run_ccart_climada("fani", dlna_total=1.2e9)
gdf.head()
```
---

## 🔬 Scientific Notes: Understanding ```raw_to_dlna_ratio```

CCART uses a transparent, reproducible calibration step to align CLIMADA’s **raw physical loss estimates** with **observed DLNA/PDNA totals** for each cyclone.

This is expressed through a simple but powerful scaling factor:
```
raw_to_dlna_ratio = DLNA_total / raw_climada_loss
```
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
- Compute the scaling factor ```raw_to_dlna_ratio```.
- Multiply each district’s raw loss by this factor:

```
loss_usd_calibrated = loss_usd_raw * raw_to_dlna_ratio
```

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
- ```district_relationships_master.csv```
- ```cyclone_level_summary.csv```
- All example scripts in ```examples/```
- The calibration module inside ```ccart/engine.py```
---

## ⚠️ Known Limitations

CCART v1.1 is a calibrated, reproducible cyclone‑impact toolkit, but several methodological and data‑driven constraints remain. These will be addressed in future releases.

**1. Hazard resolution and windfield assumptions**
- CLIMADA’s parametric windfield is used without event‑specific reanalysis corrections.
- Local terrain effects, micro‑scale wind variations, and sub‑district heterogeneity are not explicitly modelled.
- Hazard footprints are generated at a uniform grid resolution, which may smooth local extremes.

**2. Exposure data constraints (LitPop)**
- LitPop is a proxy for asset distribution and may under‑represent:
  - rural infrastructure
  - informal settlements
  - industrial clusters
- Exposure is static and does not reflect year‑specific economic growth or structural change.

**3. DLNA variability and reporting differences**
- DLNA/PDNA totals vary widely in methodology across states and years.
- Some DLNAs include indirect losses, while others focus on physical damage only.
- Calibration inherits these inconsistencies, which can influence the raw_to_dlna_ratio.

**4. District-level aggregation**
- All calibrated losses are aggregated to district boundaries.
- Sub‑district impacts (taluka/block/ward level) are not represented.
- Districts with large geographic area may show diluted spatial gradients.

**5. No explicit vulnerability curve tuning**
- CCART v1.1 uses CLIMADA’s default tropical cyclone vulnerability curves.
- No India‑specific or sector‑specific vulnerability calibration has been performed.
- This may affect absolute loss levels before DLNA scaling.

**6. Calibration is event-specific, not cross-event optimized**
- Each cyclone is calibrated independently to its DLNA total.
- No multi-event optimization or Bayesian calibration has been applied yet.
- Ratios may therefore reflect DLNA noise rather than structural model bias.

**7. No uncertainty quantification (yet)**
- CCART v1.1 provides deterministic outputs.
- Uncertainty ranges for hazard, exposure, and calibration are not included.
- Future versions may incorporate ensemble windfields or probabilistic scaling.

**8. Limited to historical cyclone tracks**
- CCART v1.1 does not include:
  - synthetic tracks
  - climate‑change‑adjusted hazard projections
  - return‑period curves
- These will be part of the planned multi-hazard expansion.


**9. Calibration is state-specific, not multi-state harmonized**
- DLNA/PDNA reports are issued at the state level, each with its own methodology, sector definitions, and valuation practices.
- CCART v1.1 calibrates each cyclone within the affected state(s) independently, without harmonizing cross‑state DLNA differences.
- For cyclones affecting multiple states, calibrated losses reflect state-by-state scaling, not a unified multi-state calibration.
- This may introduce discontinuities at state borders where DLNA methodologies differ.

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

## 🧭 Roadmap (v1.2 → v2.0)

### 1. Cross‑Cyclone Analysis Framework
- multi-event consistency checks: compare hazard footprints, exposure patterns, and calibrated ratios across all 15 events  
- bias diagnostics: identify systematic over/under-estimation patterns in raw CLIMADA losses  
- state-level harmonization signals: detect discontinuities arising from DLNA methodology differences  

### 2. Enhanced Exposure Diagnostics
- LitPop refinement: evaluate rural/industrial under‑representation and explore hybrid proxies  
- temporal exposure scaling: introduce year-specific economic scaling for historical events  
- sectoral exposure layers: optional modules for agriculture, infrastructure, and housing  

### 3. Vulnerability Curve Improvements
- India-specific tuning: explore empirical adjustments using DLNA sector splits where available  
- sectoral vulnerability options: allow users to select curves for residential, commercial, and infrastructure assets  

### 4. Calibration Architecture Upgrades
- multi-state harmonization (optional): unified calibration for cyclones affecting multiple states  
- border‑continuity adjustments: reduce artificial jumps in calibrated losses at state boundaries  
- probabilistic calibration: introduce uncertainty ranges for hazard, exposure, and scaling  
- Bayesian or multi-event optimization: reduce noise from DLNA variability  

### 5. Spatial Visualization & QGIS Integration
- ready-to-load layers: district-level calibrated losses, hazard footprints, and exposure diagnostics  
- shared colorbars: consistent visualization across all 15 cyclones  
- QGIS style templates: optional `.qml` files for hazard and impact layers  

### 6. Documentation & Usability Enhancements
- API-style documentation: clearer function-level explanations for hazard, exposure, and calibration modules  
- example notebooks: reproducible workflows for 2–3 representative cyclones  
- lightweight CLI: optional command-line interface for running full pipelines  

### 7. Multi-Hazard Expansion (post v2.0)
- flood module architecture (only after cyclone engine is fully validated)  
- heatwave and landslide placeholders for future integration  
- synthetic event generation: long-term goal for climate-conditioned hazard scenarios  

---

## 📂 Data Sources

CCART relies on a combination of open datasets and curated inputs.  
Large datasets are **not included** in this repository to keep the project lightweight.

### 🌪️ Tropical Cyclone Tracks (IBTrACS)

The full IBTrACS dataset can be downloaded from NOAA:  
https://www.ncei.noaa.gov/products/international-best-track-archive

Place the downloaded file in:

```
data/IBTRACS.ALL.v04r01.nc
```

### 🗺️ Administrative Boundaries

Odisha district boundaries (GeoJSON) should be placed in:

```
data/ODISHA_DISTRICTS.geojson
```

### 📊 DLNA / PDNA (Fani)

A cleaned version of the DLNA/PDNA file for Cyclone Fani should be placed in:

```
data/fani_impact_short.xlsx
```

(Full DLNA datasets are not included due to licensing considerations.)

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
Pednekar, K. (2026). CCART: Cyclone Calibration and Risk Toolkit (India) – 
Pan‑India 15‑Cyclone Calibrated Release (v1.1).
https://github.com/<your‑repo‑path>
```
For general reference to the methodology:
```
Pednekar, K. (2026). A transparent, reproducible framework for district‑level 
tropical cyclone impact modelling in India using CLIMADA, DLNA calibration, 
and Hazard‑Weighted Exposure (HWE).
```
If you use specific datasets from the repository (e.g., district_relationships_master.csv or cyclone_level_summary.csv), please cite:
```
CCART Dataset (2026). District‑level calibrated cyclone impact dataset for 
15 historical Indian cyclones (2009–2021). Part of CCART v1.1.
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

## 🚀 Releases

v1.1 – Pan‑India 15‑Cyclone Calibrated Release

- Added **15 calibrated historical cyclones** (2009–2021) covering both Bay of Bengal and Arabian Sea basins
- Added **district_relationships_master.csv** (full India, 15‑event calibrated dataset)
- Added **cyclone_level_summary.csv** (cross‑cyclone diagnostics: raw loss, calibrated loss, DLNA ratios)
- Added **export‑enabled scripts** for all 15 cyclones under a unified CCART v1.0 engine
- Added **SID‑anchored metadata** for every cyclone
- Standardized all cyclone workflows for reproducibility and transparency
- Improved documentation and repository structure for national‑scale analysis


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


      
