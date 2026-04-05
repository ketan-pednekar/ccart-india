# CCART Batch Runner

***Multi‑scenario orchestration for large‑scale synthetic cyclone ensembles***

The `run_batch.py` module executes multiple synthetic cyclone simulations across multiple scenarios, using the `run_single_synthetic` engine.

It is the top‑level orchestration layer of the CCART synthetic modelling framework.

This module enables:

- large‑scale ensemble generation
- scenario‑stratified runs
- reproducible folder structures
- resume‑safe execution
- scenario‑level and master summaries

It is the backbone of CCART’s synthetic ensemble capability.

---

## 🌍 Purpose

Large‑scale synthetic cyclone modelling requires:

- looping over multiple scenarios
- generating many **valid** synthetic storms
- retrying weak/offshore storms safely 
- storing each valid run in a clean folder
- writing metadata for reproducibility
- producing scenario‑level summaries
- producing a master summary

`run_batch.py` automates this entire process in a clean, modular, reproducible way.

---

## 📁 Batch Structure

The batch runner creates the following folder layout:

```
outputs/
    synthetic_runs/
        baseline/
            run_001/
            run_002/
            ...
            scenario_summary.csv
        warm_sst/
            run_001/
            ...
        high_end/
            run_001/
            ...
    master_summary.csv
```
Each `run_xxx/` folder contains:

- raw losses
- calibrated district losses
- HWE metrics
- optional hazard + track files
- metadata.json

---

## 🔧 Function Documentation

### `run_batch(.....)`

Runs synthetic cyclone ensembles across all defined scenarios.

| Parameter                     | Description                                                   |
|-------------------------------|---------------------------------------------------------------|
| `n_runs_per_scenario`         | Number of **valid** synthetic storms per scenario             |
| `exposures`                   | CLIMADA Exposures object (EPSG:4326)                          |
| `districts_gdf`               | District polygons (EPSG:4326)                                 |
| `coastline_gdf`               | Coastline geometry (EPSG:4326)                                |
| `wealth_df`                   | District‑level wealth table                                   |
| `impf_set`                    | CLIMADA impact function set                                   |
| `clean_tracks_path`           | Path to cleaned historical tracks (HDF5)                      |
| `coastline_path_for_generator`| Path to coastline shapefile for the track generator           |
| `output_root`                 | Root folder for all outputs                                   |
| `max_retries_per_scenario`    | Safety limit to avoid infinite retries                        |


---

## 🧩 Workflow

**1. Loop over scenarios**

Scenarios are defined in:

```Python
SCENARIOS = ["baseline", "warm_sst", "high_end"]
```
**2. For each scenario:**

- create scenario folder
- initialize counters:
    - `valid_count` (valid storms)
    - `retry_count` (weak/offshore storms)
- loop until `valid_count == n_runs_per_scenario`
- call `run_single_synthetic(run_dir=None)`
- if result is `"RETRY"` → skip and continue
- if valid → assign clean folder name (`run_001`, `run_002`, …)
- re‑run pipeline with `run_dir` to write outputs
- store metadata

**3. Write scenario summary**

A CSV containing:

| Field           | Description                         |
|-----------------|-------------------------------------|
| run_id          | Run folder name                     |
| scenario        | Scenario name                       |
| raw_total       | Sum of raw district losses          |
| dlna_total      | DLNA synthetic total                |
| timestamp       | Run timestamp                       |
| alpha, b        | DLNA parameters                     |
| max intensity   | Maximum hazard intensity in event   |

**4. Write master summary**

Aggregates all scenarios into one CSV.

---

## 📦 Outputs

**Scenario‑level**
```
scenario_summary.csv
run_001/
run_002/
```
Each run folder contains:

- `district_loss_raw.csv`
- `district_loss_calibrated.csv`
- `district_hwe.csv`
- `hazard.hdf5` (optional)
- `track.csv` (optional)
- `metadata.json`

**Master‑level**

`master_summary.csv`

---

## ⚠️ Notes & Caveats

- The batch runner does **not** load exposures, districts, coastline, wealth, or impact functions — these must be passed explicitly.
- Only valid storms receive folders; weak/offshore storms return `"RETRY"` and leave no trace. 
- Synthetic runs remain **local and private**; nothing is uploaded or published.
- `run_single_synthetic` must return a metadata dictionary.
- Resume logic prevents overwriting existing runs.
- Scenarios can be customized by editing the `SCENARIOS` list.
- Clean numbering ensures reproducibility and easy post‑processing.
- `max_retries_per_scenario` prevents infinite loops if the generator becomes too restrictive.
- All spatial inputs must be in **EPSG:4326**.

---

## 🎯 Summary

`run_batch.py` is the **ensemble engine** of CCART:

- runs multiple scenarios
- generates large synthetic ensembles
- saves structured outputs
- writes metadata
- produces scenario + master summaries
- supports reproducible research workflows

It transforms CCART from a modelling pipeline into a scalable synthetic cyclone simulation platform.