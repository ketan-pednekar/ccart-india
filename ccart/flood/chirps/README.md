# CCART-Floods — CHIRPS Subsystem

## Overview
The CHIRPS subsystem provides the rainfall ingestion, processing, and metric
computation pipeline for CCART-Floods. It transforms raw CHIRPS daily
precipitation data into scientifically robust rainfall metrics that feed
directly into the CCART hazard engine.

This subsystem is designed to be:
- **modular** — ingestion, metrics, and utilities are cleanly separated  
- **memory‑safe** — processes multi‑decadal rainfall without loading full stacks  
- **geospatially consistent** — all rasters aligned to the CHIRPS master grid  
- **scientifically defensible** — transparent, reproducible, and well‑documented  

---

## Components

### **1. `ingest_chirps.py`**
Handles all CHIRPS data ingestion tasks:
- inventories daily CHIRPS files  
- loads each day clipped to the India boundary  
- cleans invalid rainfall values  
- extracts the CHIRPS reference grid (shape, transform, CRS)  
- returns a metadata object used across the subsystem  

This module ensures that all rainfall data entering CCART is clean, aligned, and
ready for metric computation.

---

### **2. `compute_metrics.py`**
Computes rainfall‑based extreme metrics required by the hazard engine:

- **Rx2day** — maximum 2‑day rainfall per year  
- **P95** — 95th percentile of Rx2day across a baseline period  

All computations are performed year‑by‑year to minimise memory usage.  
Outputs are saved as `.npy` files for fast reuse.

These metrics quantify short‑duration extreme rainfall behaviour — a key driver
of flood hazard in India.

---

### **3. `raster_utils.py`**
Provides shared geospatial utilities for the CHIRPS subsystem:

- reproject rasters to the CHIRPS grid  
- mask rasters to the India boundary  
- create empty CHIRPS‑aligned rasters  
- check grid alignment  

This module ensures geospatial consistency across ingestion, metrics, and hazard
processing.

---

## Workflow Summary

The CHIRPS subsystem follows a clear, modular workflow:

1. **Ingest**  
   Load and clean daily CHIRPS rainfall clipped to India.

2. **Compute Metrics**  
   - Compute Rx2day for each year  
   - Compute P95 from the multi‑year Rx2day stack  

3. **Provide Inputs to Hazard Engine**  
   P95 and annual Rx2day values feed directly into the CCART flood hazard
   formulation.

This separation of concerns keeps the system clean, reproducible, and easy to
extend.

---

## Directory Structure

chirps/
│
├── ingest_chirps.py       # CHIRPS ingestion and grid extraction
├── compute_metrics.py     # Rx2day + P95 computation
├── raster_utils.py        # Shared geospatial utilities
├── ingest_chirps.md       # Documentation
├── compute_metrics.md     # Documentation
└── raster_utils.md        # Documentation

---


---

## Notes
- CHIRPS defines the **master grid** for all rainfall and hazard layers in CCART.  
- All modules are designed to be reusable and independent.  
- The subsystem is fully compatible with multi‑decadal CHIRPS archives.  
- Outputs are saved in `.npy` format for speed and reproducibility.  

---

## Status
The CHIRPS subsystem is **fully modularised** and ready for integration with the
hazard engine and CMIP6 downscaling workflows.

