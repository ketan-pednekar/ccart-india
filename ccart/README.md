# CCART: Cyclone Calibration and Risk Toolkit (India)

CCART is an open-source, district-level cyclone impact engine for India.  
It integrates:

- IBTrACS → CLIMADA hazard generation  
- LitPop exposure extraction  
- India-wide district boundaries  
- Tropical cyclone vulnerability curves  
- Raw CLIMADA impact modelling  
- DLNA-based calibration  
- Hazard–Exposure Weighting Engine (HWE) for spatial allocation  

The engine is designed to be transparent, reproducible, and extensible for
multi-cyclone, multi-state analysis across India.

## Repository Structure

```
ccart/
    ccart/              # Python package (hazard, exposure, impact, HWE, etc.)
    notebooks/          # Example notebooks (Odisha, pan-India, diagnostics)
    data/               # Sample data (districts, DLNA, LitPop subsets)
    README.md
    LICENSE
    requirements.txt
```


## Features

- CLIMADA-based hazard builder (IBTrACS)
- District-level hazard diagnostics
- LitPop exposure extraction for any Indian state
- Vulnerability curves for tropical cyclones
- Raw impact engine (CLIMADA)
- DLNA calibration engine
- Hazard–Exposure Weighting Engine (HWE)
- Multi-cyclone, multi-state runner

## Installation

```bash
pip install -r requirements.txt
```

## Usage

See `notebooks/CCART_pan_india_v1.ipynb` for a full example.

## License

This project is released under the MIT License.

