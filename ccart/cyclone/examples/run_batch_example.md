# CCART Synthetic Cyclone Batch Example

***Minimal working example for running multi‑scenario synthetic cyclone ensembles***

This script demonstrates how to call `run_batch()` with user‑supplied:

- district boundaries
- coastline geometry
- wealth table
- LitPop exposure
- vulnerability curves
- cleaned historical tracks

It is intended as a **quick‑start template** for users running CCART synthetic cyclone ensembles.

---
## 🔧 Prerequisites
- Python 3.10+
- CLIMADA installed
- CCART installed (`pip install -e .`)
- All spatial files in EPSG:4326
- Adequate RAM (synthetic runs can be memory‑intensive)

---

## 🚀 What This Script Does

1. Loads all required spatial and tabular inputs
2. Loads LitPop exposure for India
3. Builds vulnerability curves
4. Calls `run_batch()` with:
    - 3 scenarios (baseline, warm_sst, high_end)
    - 5 valid runs per scenario
5. Writes outputs to a clean folder structure:
    ```python
    outputs/
        synthetic_runs/
            baseline/
            warm_sst/
            high_end/
        master_summary.csv
    ````
---

## 🌡️ Scenarios Used in This Example
CCART currently supports three synthetic cyclone scenarios:

- **baseline** — historical SST distribution  
- **warm_sst** — moderate SST warming perturbation  
- **high_end** — extreme tail SST perturbation  

These are generated automatically inside `run_batch()`.

---

## 📁 Required Inputs

You must edit the paths at the top of the script:

- `DISTRICTS` — district boundaries (GeoPackage/GeoJSON)
- `COASTLINE` — mainland coastline shapefile
- `WEALTH` — district‑level wealth table
- `TRACKS` — cleaned historical tracks (HDF5)
- `OUTPUT_ROOT` — where results will be written
- All spatial inputs must be in **EPSG:4326**.

## 🧩 How It Fits Into CCART

This script is a thin wrapper around:

- `run_batch()`
- `run_single_synthetic()`
- the synthetic generator
- hazard, exposure, impact, calibration, HWE modules

It is the recommended entry point for:

- ensemble studies
- scenario analysis
- sensitivity testing
- reproducible research

---

## 📝 Example Usage

After editing the paths:


```python 
run_synthetic_batch_example.py
```
The script will:

- generate synthetic storms
- compute hazards
- compute impacts
- calibrate losses
- compute HWE
- write scenario + master summaries

---

## 🎯 Summary

This example script provides a ready‑to‑run template for executing CCART’s synthetic cyclone ensemble pipeline. It is the fastest way to get started with multi‑scenario synthetic modelling.