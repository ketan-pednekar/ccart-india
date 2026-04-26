# CCART‑Floods — Static FSI Pipeline Runner (`run_fsi_pipeline.py`)

## Purpose

This script orchestrates the **entire static Flood Susceptibility Index (FSI) pipeline**, producing the **canonical CHIRPS‑aligned susceptibility raster** used by the CCART‑Floods hazard engine.

It connects all FSI components:

```python
FSI (gauges, FSI_masked)
    → HYBAS basin assignment
    → basin‑wise rasterisation to CHIRPS grid
    → clean + rescale (0–1)
    → export GeoTIFF
```
The final output is the **static FSI raster**:

`ccart_floods_fsi_static_chirps_rescaled.tif`

This raster is used by:

- the dynamic hazard engine
- CCART‑Number
- future CMIP6 workflows

---

## Pipeline Overview

1. Load CHIRPS India grid metadata (transform, shape, CRS)
2. Compute unified FSI at IndoFloods gauges (FSI v1.1 + v1.2 + masking)
3. Perform basin‑wise rasterisation using HYBAS L06 polygons
4. Clean and rescale susceptibility raster to 0–1
5. Export CHIRPS‑aligned GeoTIFF (canonical static FSI)

This script ensures the entire FSI workflow is reproducible and grid‑consistent.

---

## Inputs

| Input             | Description                                           |
|-------------------|-------------------------------------------------------|
| CHIRPS template   | Reference CHIRPS raster for transform + shape + CRS   |
| HYBAS L06 polygons| Hydrological basins for basin‑wise FSI assignment     |
| IndoFloods data   | Used indirectly via compute_fsi()                     |
| `paths.yaml`        | Provides all project paths                            |

---

Outputs

| Output Path | Description                                                |
|-------------|------------------------------------------------------------|
| `fsi_static`  | CHIRPS‑aligned static FSI raster (0–1, NaN outside India)  |

The output raster has:

- CHIRPS 0.05° grid
- EPSG:4326 CRS
- `float32` values
- `NaN` nodata
- LZW compression

---

## Key Components Used

| Module                        | Purpose                                      |
|-------------------------------|----------------------------------------------|
| `compute_fsi()`                 | Builds FSI v1.1 + v1.2 + proxy masking       |
| `rasterise_clean_rescale_fsi()` | Basin‑wise rasterisation + cleaning + scaling|
| `export_fsi_raster()`           | Writes final GeoTIFF                         |
| `load_chirps_grid()`            | Extracts CHIRPS transform, shape, CRS        |

---

## FSI Pipeline Characteristics

| Property        | Description                                             |
|-----------------|---------------------------------------------------------|
| Grid            | CHIRPS India 0.05°                                      |
| CRS             | EPSG:4326                                               |
| Method          | Basin‑wise rasterisation (HYBAS L06)                    |
| Value range     | 0–1 (susceptibility)                                    |
| Nodata          | NaN                                                     |
| Output format   | GeoTIFF (LZW compressed)                                |
| Alignment       | Exact match to CHIRPS transform                         |

---

## Usage

Run directly:

```bash
python fsi_pipeline.py
```
Or import and call:

```python
from ccart.flood.fsi.fsi_pipeline import main
main()
```
## Notes

- This script produces the **canonical static FSI raster** for CCART‑Floods.
- FSI computation and rasterisation are fully reproducible via paths.yaml.
- HYBAS L06 is required for hydrologically meaningful susceptibility fields.
- The output raster is used by all downstream hazard and climate‑risk modules.