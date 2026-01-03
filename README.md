# CCART: Cyclone Calibration and Risk Toolkit (India)

![Python](https://img.shields.io/badge/Python-3.10%2B-blue)
![License](https://img.shields.io/badge/License-MIT-yellow)
![Status](https://img.shields.io/badge/Status-Active-brightgreen)


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
````
````
## Usage

See `notebooks/CCART_Odisha_v0.9.ipynb` for a full example workflow.

A minimal example:
```
from ccart import run_ccart_climada

gdf = run_ccart_climada("fani", dlna_total=1.2e9)
gdf.head()


---
## 🗺️ Roadmap

**v0.9 (Current Release)**
- Odisha baseline
- Fani DLNA calibration
- Hazard builder + exposure + vulnerability
- Raw impact engine
- HWE allocation

**v1.0 (Upcoming)**
- Pan-India hazard engine
- Pan-India exposure extraction
- Multi-state calibration
- Sectoral expansion (education, power, transport)
- Visual storytelling + dashboards
- Synthetic cyclone generator
- Multi-hazard integration (rainfall, surge)

---
## Topics

`open-source` `geospatial` `cyclone` `india` `adaptation`  
`climada` `climate-risk` `disaster-risk` `impact-modelling` `hazard-modelling`

---
## Website

Visit [www.ccartghg.com](https://www.ccartghg.com) for updates and future outreach.

---
## License

This project is released under the MIT License. See `LICENSE` for details.

---
## Contributing

CCART welcomes collaboration from:

- climate scientists
- geospatial analysts
- engineers
- modellers
- open‑source contributors

Open an `Issue` or start a `Discussion` to get involved.

---
## Releases

- [v0.9 – Fani baseline](https://github.com/ketan-pednekar/ccart-india/releases)

      
