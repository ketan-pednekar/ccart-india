# CCART Synthetic Cyclone Runner

***End‑to‑end orchestration of the synthetic cyclone modelling pipeline***

The `run_single_synthetic` function is the central orchestration engine of the CCART synthetic cyclone framework.
It ties together all modular components — exposure, hazard, impact, calibration, and HWE — and executes them in a clean, reproducible sequence for a single synthetic cyclone track.

This function is the backbone of both interactive runs and large‑scale batch simulations.

---

## 🌍 Purpose

Synthetic cyclone modelling requires a coordinated sequence of scientific steps:

- generating a synthetic track
- building a synthetic hazard field
- clipping exposure
- computing hazard statistics
- computing raw impact
- calibrating losses to DLNA totals
- computing HWE metrics
- saving outputs and metadata

`run_single_synthetic` performs all these steps in a single, reproducible, scenario‑aware workflow, producing scientific outputs and metadata suitable for batch runners and reproducible research workflows.

---

## 📁 Pipeline Overview

`run_single_synthetic` executes the following modules in order:

| Step | Module                             | Purpose                                      |
|------|------------------------------------|----------------------------------------------|
| 1    | `synthetic_generator`              | Generate synthetic cyclone track             |
| 2    | `hazard_from_tracks`               | Build hazard field from track                |
| 3    | `synthetic_exposure`               | Clip exposure to hazard bounding box         |
| 4    | `synthetic_impact`                 | Compute hazard stats + raw impact            |
| 5    | `synthetic_impact (aggregation)`   | Aggregate district losses                    |
| 6    | `synthetic_calibration`            | DLNA scaling + coastal calibration           |
| 7    | `synthetic_hwe`                    | Compute HWE metrics                          |
| 8    | —                                  | Save outputs + metadata                      |

This function does **no scientific computation itself** — it orchestrates the pipeline.

---

## 🔧 Function Documentation

`run_single_synthetic(run_dir, exposures, districts_gdf, coastline_gdf, wealth_df, impf_set, ...)`

Runs a complete synthetic cyclone modelling workflow for a single track.

**Required Inputs (all passed explicitly)**

| Parameter          | Description                                                   |
|--------------------|---------------------------------------------------------------|
| `run_dir`          | Folder where outputs for this run will be saved               |
| `exposures`        | CLIMADA Exposures object (EPSG:4326)                          |
| `districts_gdf`    | District polygons (EPSG:4326)                                 |
| `coastline_gdf`    | Coastline geometry (EPSG:4326)                                |
| `wealth_df`        | District-level wealth table                                   |
| `impf_set`         | CLIMADA impact function set                                   |
| `scenario`         | Scenario name (e.g., "baseline", "warm_sst")                  |
| `alpha`            | DLNA scaling parameter                                        |
| `b`                | DLNA exponent                                                 |
| `inland_clip_km`   | Distance threshold for inland masking                         |
| `save_track`       | Whether to save track output                                  |
| `save_hazard`      | Save hazard as HDF5                                           |
| `save_track_csv`   | Save track as CSV                                             |


---

## 🧩 Step‑by‑Step Workflow

**1. Generate synthetic track**

Scenario‑aware track generation.

**2. Build synthetic hazard**

Converts track into CLIMADA hazard.

**3. Clip exposure**

Bounding‑box clipping.

**4. Compute hazard statistics**

District‑level max intensity + inland mask.

**5. Compute raw impact**

Exposure × vulnerability × hazard.

**6. Aggregate district losses**

Sum raw losses to district level.

**7. DLNA calibration**

Coastal calibration + inland zeroing.

**8. Compute HWE metrics**

Loss share relative to wealth.

**9. Save outputs**

CSV + optional hazard + track.

**10. Write metadata**

Scenario, DLNA parameters, totals, timestamp.

---

## 📦 Outputs

### `run_single_synthetic` produces:

Files in `run_dir/`

- `track.csv` (optional)
- `hazard.hdf5` (optional)
- `district_loss_raw.csv`
- `district_loss_calibrated.csv`
- `district_hwe.csv`
- `metadata.json`

**Return Value**

A Python dictionary with scenario, DLNA parameters, totals, and timestamp.

---

## ⚠️ Notes & Caveats

- All spatial inputs must be in **EPSG:4326**.
- Coastline must be supplied as a **GeoDataFrame**. 
- All required inputs (exposures, districts, coastline, wealth, impf_set) must be passed explicitly; the runner does not load files internally.
- DLNA parameters (`alpha`, `b`) are provisional and should be recalibrated as more empirical data becomes available.
- This function is designed for single‑run orchestration; batch execution is handled by `run_batch.py`.
- No hard‑coded paths are used — all inputs are passed explicitly for full reproducibility.
- If the generated storm is too weak or produces zero impact, the function returns "RETRY" and writes no files. This enables clean numbering in batch mode.

---

## 🎯 Summary

`run_single_synthetic` is the core execution engine of the CCART synthetic cyclone framework.

It:

- orchestrates all scientific modules
- ensures reproducibility
- saves clean outputs
- writes metadata
- returns a summary for batch runners

This function transforms CCART’s modular components into a coherent, end‑to‑end synthetic modelling pipeline.