# CCART: Cyclone Calibration and Risk Toolkit (India)

<p align="left">
  <img src="https://img.shields.io/badge/Python-3.10%2B-blue" />
  <img src="https://img.shields.io/badge/License-MIT-yellow" />
  <img src="https://img.shields.io/badge/Status-Active-brightgreen" />
  <img src="https://img.shields.io/github/last-commit/ketan-pednekar/ccart-india" />
  <img src="https://img.shields.io/github/issues/ketan-pednekar/ccart-india" />
  <img src="https://img.shields.io/github/stars/ketan-pednekar/ccart-india?style=social" />
</p>

Open, transparent, and reproducible cyclone impact modelling for India

CCART is an open-source, modular engine for **district-level tropical cyclone impact modelling across India**.

Built on **CLIMADA** and anchored in transparent physical logic, **CCART v0.9** introduces:

- **IBTrACS → CLIMADA hazard generation**
- **LitPop exposure extraction** for any Indian state
- **India-wide district boundaries**
- **Tropical cyclone vulnerability curves** (India-specific)
- **Raw CLIMADA impact modelling**
- **DLNA-based calibration** (Fani v0.9)
- **Hazard–Exposure Weighting Engine (HWE)** for spatial allocation

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
ccart/              # Python package (hazard, exposure, impact, HWE, calibration)
notebooks/          # Example notebooks (Odisha v0.9, diagnostics, pan-India)
data/               # Sample data (districts, DLNA, LitPop subsets)
docs/               # Documentation and outreach materials
examples/           # Minimal working demos
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

## Usage

To explore CCART in action, see `notebooks/CCART_Odisha_v0.9.ipynb` for a full example workflow.

A minimal example:

```python
from ccart import run_ccart_climada

gdf = run_ccart_climada("fani", dlna_total=1.2e9)
gdf.head()
```

---

## 🗺️ Roadmap

### **v0.9 — Odisha Prototype (Current Release)**
- Odisha baseline engine
- Fani DLNA calibration
- Hazard builder + exposure + vulnerability
- Raw CLIMADA impact engine
- District-level HWE allocation
- Reproducible, transparent workflow

---

### **v1.0 — Pan‑India Reproducible Module (Upcoming)**
- Pan‑India hazard engine (IBTrACS → CLIMADA)
- Pan‑India exposure extraction (LitPop + boundaries)
- Multi-state calibration framework
- Sectoral expansion (housing, health, education, power, transport)
- Unified CCART engine for any Indian cyclone
- Visual storytelling + dashboards for states
- Synthetic cyclone generator (baseline version)
- Multi-hazard integration (rainfall, surge)

---

### **v1.1 — QGIS + TCFD‑Ready Impact Layers**
- Export district-level impacts as GeoJSON / GPKG
- QGIS-ready hazard, exposure, and impact layers
- Company-wise and asset-class-wise reporting
- TCFD/ISSB-aligned physical risk outputs
- Higher-resolution exposure integration (LitPop 1 km or custom assets)
- Improved spatial accuracy for district and sub-district impacts

---

### **v2.0 — Data‑Driven Damage Estimation (Future)**
- Centroid-level ML models using satellite/QGIS features
- SAR/Nightlights-based damage detection for training labels
- Hybrid physical + ML vulnerability module
- Probabilistic impact distributions
- Scenario-based climate risk projections (CMIP6)
- Synthetic cyclone ensembles for adaptation planning

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
## 🤝 Contributing

CCART welcomes collaboration from:

- climate scientists  
- geospatial analysts  
- engineers  
- modellers  
- open-source contributors

---

Open an **Issue** or start a **Discussion** to get involved.

## 🚀 Releases

- **v0.9** – Fani baseline

      
