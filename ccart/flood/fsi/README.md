# README — CCART‑Floods FSI Pipeline

## Overview

The CCART‑Floods FSI pipeline converts gauge‑based Flood Susceptibility Index (FSI) values into a **CHIRPS‑aligned, float32, NaN‑aware GeoTIFF** suitable for hazard multiplication and downstream risk modelling.

This pipeline is fully modular:

```python
compute_fsi.py  →  rasterise_fsi.py  →  export_fsi_raster.py
```
and is orchestrated by:

```python
run_fsi_pipeline.py
```
All paths are loaded from `paths.yaml` to ensure portability and reproducibility.

---

## Purpose

The pipeline produces the canonical CCART‑Floods susceptibility layer:

```python
ccart_floods_fsi_rescaled.tif
```
This raster:

- aligns exactly with the CHIRPS grid
- uses float32 with NaN nodata
- is rescaled to 0–1
- is masked to empirical flood basins
- is ready for hazard multiplication (FSI × rainfall anomaly)

---

## Pipeline Steps

1. Compute FSI (`compute_fsi.py`)
Generates a unified GeoDataFrame of gauge‑based FSI values, masked to empirical flood basins.

2. Rasterise + Clean + Rescale (`rasterise_fsi.py`)
Converts point‑based FSI into a CHIRPS‑aligned raster:

- rasterisation
- NaN cleaning
- empirical masking
- 0–1 rescaling

3. Export GeoTIFF (`export_fsi_raster.py`)

Writes the final susceptibility raster:

- float32
- NaN nodata
- CHIRPS transform
- LZW compression
- tiled GeoTIFF

---

## Inputs

| Input Name        | Description                                      | Source / Path Key                     |
|-------------------|--------------------------------------------------|----------------------------------------|
| FSI gauges        | Gauge-level susceptibility values                | compute_fsi.py                         |
| HYBAS basins      | Level-06 hydrological basins for masking         | paths.yaml → data.hybas                |
| India boundary    | Optional administrative mask                     | paths.yaml → data.india_boundary       |
| CHIRPS template   | Provides grid, transform, CRS for rasterisation  | paths.yaml → chirps.template           |

---

## Outputs

| Output File                        | Description                                      | Location (paths.yaml)          |
|------------------------------------|--------------------------------------------------|--------------------------------|
| `ccart_floods_fsi_rescaled.tif`      | Final CHIRPS-aligned susceptibility raster       | outputs.fsi                    |
| Console logs                       | Step-by-step pipeline progress                   | stdout                         |
| Intermediate arrays                | In-memory only                                   | not written                    |

---

## Module Responsibilities

| Module                  | Responsibility                                 | Output Type            |
|-------------------------|-------------------------------------------------|------------------------|
| `compute_fsi.py`          | Load + unify gauge FSI                          | GeoDataFrame           |
| `rasterise_fsi.py`        | Rasterise + clean + rescale FSI                 | 2D float32 NumPy array |
| `export_fsi_raster.py`    | Write CHIRPS-aligned GeoTIFF                    | GeoTIFF file           |
| `run_fsi_pipeline.py`     | Orchestrate full pipeline (config-driven)       | Final raster           |

---

## Execution

Run the pipeline from project root:

```bash
python -m ccart.flood.fsi.run_fsi_pipeline
```
The script automatically:

- loads `paths.yaml`
- loads CHIRPS grid metadata
- computes FSI
- rasterises
- exports GeoTIFF

No hardcoded paths are used.

---

## Dependencies

The FSI pipeline requires the following Python packages:

| Package     | Purpose                                |
|-------------|------------------------------------------|
| rasterio    | Reading/writing GeoTIFFs, CHIRPS grid    |
| geopandas   | Handling gauge shapefiles and HYBAS      |
| numpy       | Array operations                         |
| shapely     | Geometry operations                      |
| pyproj      | CRS handling                             |

These are already part of the CCART environment specification.

---

## Configuration (`paths.yaml`)

The pipeline expects:

```yaml
project_root: "C:/CMIP_data/cmip6/Climada/Projects/ccart-india"

chirps:
  daily_dir: "D:/Climate Risk Data/CHIRPS_daily"
  template: "D:/Climate Risk Data/CHIRPS_daily/chirps_2020_01.tif"

outputs:
  fsi: "ccart/flood/outputs/fsi"
```
---

## File Structure

```python
ccart/
  flood/
    fsi/
      compute_fsi.py
      rasterise_fsi.py
      export_fsi_raster.py
      run_fsi_pipeline.py
      README.md   ← this file
```
---

## Diagnostics

| Check                     | Expected Value / Behaviour                   | Notes                                  |
|---------------------------|-----------------------------------------------|----------------------------------------|
| CHIRPS grid shape         | Matches template raster                       | Printed at pipeline start              |
| FSI gauge count           | > 0                                           | Printed after compute_fsi()            |
| Output dtype              | float32                                       | Enforced in export_fsi_raster.py       |
| Output nodata             | NaN                                           | Enforced                               |
| Output CRS                | EPSG:4326                                     | Inherited from CHIRPS template         |
| Output compression        | LZW                                           | Set in export_fsi_raster.py            |
| Output tiling             | Yes                                           | Set in export_fsi_raster.py            |

---

## Troubleshooting

| Issue                          | Cause                                      | Fix                                           |
|--------------------------------|---------------------------------------------|-----------------------------------------------|
| Output raster is empty         | CHIRPS template path incorrect              | Check `paths.yaml → chirps.template`          |
| FSI gauges = 0                 | INDOFLOODS path incorrect                   | Check `paths.yaml → data.indofloods`          |
| CRS mismatch warning           | Template not EPSG:4326                      | Use any CHIRPS file as template               |
| Raster looks all zeros         | Rescaling step received only NaNs           | Check HYBAS mask and gauge coverage           |
| Pipeline crashes on rasterise  | CHIRPS template unreadable or corrupted     | Replace template with any valid CHIRPS file   |

---

## Notes

- This pipeline produces the **canonical susceptibility layer** for CCART‑Floods.
- All downstream hazard modules assume this raster exists and is CHIRPS‑aligned.
- The pipeline is intentionally simple and transparent to maintain scientific defensibility.