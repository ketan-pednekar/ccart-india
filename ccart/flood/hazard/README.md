# CCART-Floods — Hazard Subsystem

## Overview
The hazard subsystem implements the final stage of the CCART-Floods workflow.
It combines rainfall extremes (Rx2day, P95) with terrain-driven flood
susceptibility (FSI) to produce **climate‑conditioned flood hazard** for both
historical and future periods.

This subsystem is designed to be:
- **scientifically transparent** — explicit formulation and assumptions  
- **modular** — ingestion, computation, and utilities are cleanly separated  
- **memory‑safe** — processes one year at a time  
- **CHIRPS‑aligned** — all rasters share the same grid and CRS  

The hazard subsystem completes the CCART flood module.

---

## Scientific Formulation

The CCART flood hazard is defined as:



\[
H = \text{FSI} \times \max\left(\frac{\text{Rx2day}}{\text{P95}}, 0\right)
\]



Where:
- **FSI** — static Flood Susceptibility Index (0–1)  
- **Rx2day** — annual maximum 2‑day rainfall  
- **P95** — 95th percentile of Rx2day (1995–2024 baseline)  

This formulation expresses how rainfall extremes amplify existing
terrain‑driven susceptibility.

---

## Components

### **1. `ingest_fsi.py`**
Loads and prepares the Flood Susceptibility Index (FSI):

- loads raw FSI GeoTIFF  
- loads India boundary  
- reprojects FSI to the CHIRPS grid  
- cleans invalid values  
- returns a CHIRPS‑aligned FSI array  

This ensures perfect pixel‑level alignment with rainfall metrics.

---

### **2. `hazard_engine.py`**
Implements the core hazard computation and year‑by‑year loops.

Provides:
- `compute_hazard()` — pure hazard function  
- `compute_historical_hazard()` — CHIRPS 1995–2024  
- `compute_future_hazard()` — CMIP6 SSP3‑7.0 2027–2100  

All loops:
- load one year at a time  
- compute hazard  
- save `.npy`  
- free memory  

This keeps the pipeline safe on standard hardware.

---

### **3. `hazard_utils.py`**
Shared helper functions (normalisation, clipping, safe division, etc.).

This module keeps the engine clean and focused.

---

## Workflow Summary

The hazard subsystem follows a simple, modular workflow:

1. **FSI ingestion**  
   Load and reproject FSI to CHIRPS.

2. **Historical hazard**  
   - load annual Rx2day  
   - compute hazard  
   - save `hazard_hist_YYYY.npy`

3. **Future hazard**  
   - compute Rx2day from CMIP6  
   - reproject to CHIRPS  
   - compute hazard  
   - save `hazard_fut_YYYY.npy`

This completes the climate‑conditioned flood hazard pipeline.

---

## Directory Structure

hazard/
│
├── ingest_fsi.py          # Load + reproject FSI to CHIRPS grid
├── hazard_engine.py       # Core hazard computation + loops
├── hazard_utils.py        # Shared helper functions
├── ingest_fsi.md          # Documentation
├── hazard_engine.md       # Documentation
└── hazard_utils.md        # Documentation


---

## Notes
- Hazard is computed **pixel‑wise** and is fully CHIRPS‑aligned.  
- FSI is treated as a **static** layer.  
- CMIP6 rainfall is reprojected to CHIRPS using bilinear resampling.  
- This subsystem does **not** render frames or animations.  
- All loops are **resume‑friendly** — completed years are skipped automatically.  

---

## Status
The hazard subsystem completes the CCART-Floods module.  
Together with CHIRPS ingestion, rainfall metrics, and FSI ingestion, it forms a
fully modular, reproducible, and scientifically defensible flood hazard engine.

