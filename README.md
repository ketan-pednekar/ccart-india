# CCART: Cyclone Calibration and Risk Toolkit (India)

![Python](https://img.shields.io/badge/Python-3.10+-blue)
![License](https://img.shields.io/badge/License-MIT-yellow)
![Status](https://img.shields.io/badge/Status-Active-brightgreen)

CCART (Cyclone Calibration and Risk Toolkit) is a modular, open‑source engine for district‑level cyclone impact modelling across India.  
Built on CLIMADA, it enables transparent hazard diagnostics, exposure extraction, calibrated impact modelling, and spatial allocation using the Hazard–Exposure Weighting Engine (HWE).

---

## Overview

CCART integrates:

- IBTrACS → CLIMADA hazard generation  
- LitPop exposure extraction  
- India‑wide district boundaries  
- Tropical cyclone vulnerability curves  
- Raw CLIMADA impact modelling  
- DLNA‑based calibration  
- Hazard–Exposure Weighting Engine (HWE) for spatial allocation  

The engine is designed to be transparent, reproducible, and extensible for multi‑cyclone, multi‑state analysis across India.

---

## Repository Structure
```
ccart/              # Python package (hazard, exposure, impact, HWE, etc.)
notebooks/          # Example notebooks (Odisha, pan-India, diagnostics)
data/               # Sample data (districts, DLNA, LitPop subsets)
docs/               # Documentation and outreach materials
examples/           # Minimal working demos
README.md
LICENSE
requirements.txt
```
---

## Features

- CLIMADA-based hazard builder (IBTrACS)
- District-level hazard diagnostics
- LitPop exposure extraction for any Indian state
- Vulnerability curves for tropical cyclones
- Raw impact engine (CLIMADA)
- DLNA calibration engine
- Hazard–Exposure Weighting Engine (HWE)
- Multi-cyclone, multi-state runner

---
```
## Installation

```bash
pip install -r requirements.txt
````
````
## Usage

See `notebooks/CCART_pan_india_v1.ipynb` for a full example workflow.
---
## Roadmap
- Fani v0.9 baseline (complete)
- DLNA calibration modules (in progress)
- Pan‑India hazard engine
- Sectoral expansion
- Outreach and visual storytelling

---
## Topics

`open-source` `geospatial` `cyclone` `india` `adaptation`  
`climada` `climate-risk` `disaster-risk` `impact-modelling` `hazard-modelling`

---
## Website

Visit [www.ccartghg.com](https://www.ccartghg.com) for updates and future outreach.

---
## License

This project is released under the MIT License. See LICENSE for details.
