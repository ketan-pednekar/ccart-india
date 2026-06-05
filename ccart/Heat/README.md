# CCART‑Heat — Climate Change Adaptation & Risk Toolkit (Heat Module)

## Overview

CCART‑Heat is a modular, end‑to‑end pipeline for generating wet‑bulb temperature (WBT) exceedance hazards for India using CMIP6 climate model outputs.
It ingests raw CMIP data, computes WBT, generates exceedance cubes, produces time‑slice hazards, exports GeoTIFFs, and provides a full suite of validation tools.

The system is designed for:

- Developers maintaining or extending CCART‑Heat
- Researchers using hazard outputs for climate‑risk analysis
- Policy and planning teams relying on validated, reproducible hazard layers

---

## Folder Structure & Purpose

```
ccart/
  Heat/
    config/
    config_data/
    ingestion/
    ingested/
    hazard/
    utils/
    outputs/
    viz/
```

### config/

Configuration loader.

Loads paths and environment settings used across the module.

### config_data/

Static configuration files.

Defines all filesystem paths (CMIP directories, output folders, masks, etc.).

### ingestion/

Scripts to ingest CMIP6 data (tas, hurs, sfcWind, etc.), regrid if needed, and prepare clean, analysis‑ready datasets.

### ingested/

Stores ingested Zarr cubes for:

- `hist`
- `ssp370`
- `ssp585`

Also contains scripts to add WBT to ingested datasets.

### hazard/

Core hazard engines:

- Compute WBT exceedances for all CMIP scenarios
- Generate exceedance cubes using strict masks
- Produce time‑slice cubes (e.g., 2081–2100)
- Export time‑slice TIFFs

#### Engines included:

- wbt_engine.py
- exceedance_engine.py
- generate_timeslice_cubes.py
- generate_timeslice_tifs.py
- run_exceedance.py

### utils/

- Validation and QA tools:
- Validate exceedance cubes
- Validate time‑slice cubes
- Validate time‑slice TIFFs
- Generate strict India masks
- Orientation diagnostics
- District‑level exceedance checks

This folder ensures every hazard output is spatially correct.

### outputs/

Final hazard products:

- Exceedance cubes
- Time‑slice cubes
- Time‑slice TIFFs

Organized by scenario and threshold.

---

## Pipeline Summary

### 1. Ingestion

- Load CMIP6 variables
- Standardize lat/lon
- Ensure consistent grid
- Save to Zarr under `ingested/`

### 2. Add WBT

- Compute wet‑bulb temperature using WBT engine
- Append to ingested cubes

### 3. Exceedance Computation

- Compute daily exceedance (Tw > 35°C)
- Aggregate to annual exceedance
- Build exceedance cubes for:
  - hist
  - ssp370
  - ssp585

### 4. Time‑Slice Generation

- Extract 20‑year windows (e.g., 2081–2100)
- Compute max exceedance
- Save as Zarr cubes

### 5. TIFF Export

- Convert time‑slice cubes to GeoTIFF
- Apply strict India mask
- Ensure correct orientation

### 6. Validation

- Using tools in `utils/`:
- District‑level exceedance checks
- Hard coordinate checks
- Orientation verification
- TIFF vs Zarr consistency

This ensures no flipped maps, no misaligned grids, no CRS issues.

---

## Orientation Rules (Summary)

### Ingested cubes

- Lat ascending
- Array stored upside‑down
- → Flip array (np.flipud)
- → Use positive dy transform

### Time‑slice cubes

- Lat descending
- Array stored upside‑down
- → Flip array
- → Use negative dy transform

### TIFF time‑slices

- Transform correct
- Array stored upside‑down
- → Flip array
- → Keep transform unchanged

### Strict India mask

- Always rasterized north‑up
- Works for both ascending/descending lat

---

## How to Run the Full Pipeline

- Ingest CMIP6 data
- Add WBT to ingested cubes
- Run exceedance engine
- Generate time‑slice cubes
- Export time‑slice TIFFs
- Run validators
- Publish outputs

Each step has its own script + README inside the relevant folder.

---

## Who This README Is For

This top‑level README is written for a mixed audience:

- Developers maintaining CCART‑Heat
- Researchers using hazard outputs
- Analysts validating spatial layers

It avoids code‑level detail but provides enough structure to navigate the system confidently.