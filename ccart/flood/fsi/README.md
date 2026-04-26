# CCART‑Floods — Flood Susceptibility Index (FSI) Subsystem

**The Flood Susceptibility Index (FSI)** is the static component of the CCART‑Floods hazard model.
It represents the **intrinsic flood‑proneness** of each basin in India, independent of rainfall.

FSI is computed at IndoFloods gauge locations (v1.1 + v1.2), masked for ungauged basins, rasterised to the CHIRPS grid, and exported as a canonical GeoTIFF used by the hazard engine.

---

## 🌐 FSI Architecture Overview

```python
compute_fsi.py
    ├── FSI v1.1 (geomorphology + soils + climate)
    ├── FSI v1.2 (hydrology + proxy masking)
    └── FSI_masked (final gauge-level susceptibility)

rasterise_fsi.py
    └── Basin-wise rasterisation → CHIRPS grid → rescale 0–1

export_fsi_raster.py
    └── Write canonical GeoTIFF (float32, NaN nodata, LZW)

run_fsi_pipeline.py
    └── Orchestrates the entire static FSI workflow
```

---

## Final output:

`ccart_floods_fsi_static_chirps_rescaled.tif`

---

## 📘 1. FSI v1.1 — Empirical IndoFloods Susceptibility

### Inputs

| File                                   | Description                          |
|----------------------------------------|--------------------------------------|
| `catchment_characteristics_indofloods.csv` | IndoFloods geomorphology + soils     |
| `metadata_indofloods.csv`                | Gauge metadata                       |


### Variables Used

| Variable             | Why It Matters                                   |
|----------------------|--------------------------------------------------|
| Drainage Density     | Controls runoff concentration                    |
| Catchment Relief     | Steeper basins → flashier floods                |
| Ruggedness Number    | Terrain complexity                               |
| Elongation Ratio     | Basin shape → hydrograph response                |
| Form Factor          | Width/length ratio                               |
| Annual Precipitation | Climatic forcing                                 |
| Soil Type            | Infiltration/runoff behaviour                    |

All numeric variables are **min–max normalised**.
Soils are **one‑hot encoded** and averaged into `Soil_block`.

### FSI v1.1 formula

```python
FSI_v1_1 = mean([
    DrainageDensity_norm,
    CatchmentRelief_norm,
    Ruggedness_norm,
    Elongation_norm,
    FormFactor_norm,
    AnnualPrecip_norm,
    Soil_block
])
```
Output: **GeoDataFrame** with point geometry (EPSG:4326).

---

## 📘 2. FSI v1.2 — Hydrology‑Enhanced Susceptibility

### Inputs

| File              | Description                     |
|-------------------|---------------------------------|
| HYBAS_SHP         | HydroBASINS L06 polygons        |
| INDIA_SHP         | India boundary                  |
| Output of FSI v1.1| Gauge‑level susceptibility      |



### Hydrological Variables

| Variable  | Meaning                                | Why It Matters                                  |
|-----------|-----------------------------------------|--------------------------------------------------|
| UP_AREA   | Total upstream contributing area        | Larger upstream → more inflow → higher risk     |
| SUB_AREA  | Area of the basin polygon               | Basin size context                               |
| ORDER     | Strahler stream order                   | Maturity of river network                        |
| n_gauges  | Number of IndoFloods gauges in basin    | Indicates empirical support                      |
| Proxy_flag| 1 = no gauges, 0 = has gauges           | Used to mask ungauged basins                    |

### Steps

1. Filter HYBAS to India
2. Count gauges per basin → identify proxy basins
3. Assign hydrological attributes
4. Normalise hydrological variables
5. Compute FSI v1.2
6. Apply proxy mask

### FSI v1.2 formula

```python
FSI_v1_2 = 0.5 * FSI_v1_1 + 0.5 * UP_AREA_norm
```

### Proxy Mask

```python
FSI_masked = NaN if Proxy_flag == 1 else FSI_v1_2
```

### Final Output Columns

| Column       | Meaning                                                |
|--------------|--------------------------------------------------------|
| FSI_v1_1     | Empirical susceptibility                               |
| FSI_v1_2     | Hydrology‑enhanced susceptibility                      |
| FSI_masked   | Final recommended FSI (NaN for proxy basins)           |
| HYBAS_ID     | HydroBASINS Level‑06 basin ID                          |
| Proxy_flag   | 1 = ungauged basin                                     |
| geometry     | Point geometry                                         |

---

## 📘 3. Basin‑Wise Rasterisation (`rasterise_fsi.py`)

### Pipeline

- Load HYBAS L06 polygons
- Spatial join gauges → basins
- Aggregate FSI per basin
- Merge into HYBAS polygons
- Rasterise polygons to CHIRPS grid
- Rescale raster to 0–1

### Key Features

| Feature               | Description                                      |
|-----------------------|--------------------------------------------------|
| HYBAS ID detection    | Automatically detects correct basin ID column    |
| CRS safety            | Auto‑aligns CRS between gauges and HYBAS         |
| Basin‑wise assignment | Hydrologically meaningful susceptibility surface |
| NaN masking           | Proxy basins remain NaN                          |
| CHIRPS alignment      | Exact match to CHIRPS 0.05° grid                 |


### Output

| Output       | Description                                   |
|--------------|-----------------------------------------------|
| fsi_rescaled | 2D float32 raster (0–1, NaN outside India)    |

---

## 📘 4. Exporter (`export_fsi_raster.py`)

### Output Raster Characteristics

| Property        | Value / Description                         |
|-----------------|----------------------------------------------|
| Grid            | CHIRPS 0.05° grid                            |
| CRS             | EPSG:4326                                    |
| Data type       | float32                                      |
| Value range     | 0–1 (susceptibility)                         |
| Nodata          | NaN                                          |
| Compression     | LZW                                          |
| Alignment       | Matches CHIRPS transform exactly             |

This module **does not modify values** — it only writes the raster.

---

## 📘 5. Pipeline Runner (run_fsi_pipeline.py)

1. Runs the entire FSI workflow:
2. Load CHIRPS grid metadata
3. Compute FSI (v1.1 + v1.2 + masking)
4. Rasterise to CHIRPS
5. Rescale
6. Export GeoTIFF

### Output

`ccart_floods_fsi_static_chirps_rescaled.tif`

---

## ▶️ How to Run the FSI Pipeline

Because CCART‑Floods uses an **orchestrator**, you only need one command.

### Option 1 — Run from terminal

```bash
python run_fsi_pipeline.py
```
### Option 2 — Run from Python

```python
from ccart.flood.fsi.run_fsi_pipeline import main
main()
```
**No manual sequencing required**

The orchestrator automatically:

- loads CHIRPS metadata
- computes FSI v1.1 + v1.2
- applies proxy masking
- rasterises to CHIRPS
- rescales
- exports the GeoTIFF

You never need to call the submodules individually unless debugging.

---

## 🔄 Differences From Earlier FSI Versions

| Area | Earlier System | New Canonical System |
|------|----------------|----------------------|
| Architecture | Scattered scripts | Clean 3‑module design |
| FSI v1.1 | Inconsistent | Standardised + audited |
| Hydrology | Not included | Added via HYBAS L06 |
| Proxy basins | Not masked | Explicit NaN masking |
| Rasterisation | Point burn‑in | Basin‑wise polygons |
| HYBAS handling | Manual | Automatic ID detection |
| CRS | Sometimes mismatched | Auto‑aligned |
| Output | Inconsistent | Canonical CHIRPS GeoTIFF |
| Dead code | Present | Removed |


## 🧭 Notes

- FSI is static — it does not depend on rainfall.
- Hazard is computed later as:
  ```python
  Hazard = FSI × Rainfall Anomaly
  ```
FSI is required for:
  - hazard engine
  - CCART‑Number
  - CMIP6 workflows