# CCART‑Floods — FSI Rasteriser (`rasterise_fsi.py`)

## Purpose

`rasterise_fsi.py` converts the **gauge‑level Flood Susceptibility Index (FSI)** into a **continuous CHIRPS‑aligned raster** using **basin‑wise assignment** from HydroBASINS Level‑06 polygons.

This is the **canonical CCART‑Floods method** for generating a hydrologically meaningful susceptibility surface.

It replaces point burn‑in and ensures:

- complete India‑wide coverage
- hydrologically consistent susceptibility fields
- perfect alignment with the CHIRPS 0.05° grid
- suitability for downstream hazard modelling and CCART‑Number

---

## Pipeline Overview

1. Load HYBAS L06 polygons
2. Spatially join gauge‑level FSI → HYBAS basins
3. Aggregate FSI per basin (mean of gauges)
4. Merge aggregated FSI back into HYBAS polygons
5. Rasterise HYBAS polygons onto CHIRPS grid
6. Clean and rescale raster to 0–1
7. Return CHIRPS‑aligned susceptibility raster

This produces the **static FSI raster** used by the hazard engine.

---

## Inputs

| Input            | Description                                           |
|------------------|-------------------------------------------------------|
| `gdf_fsi`          | GeoDataFrame from compute_fsi() with FSI_masked       |
| `chirps_transform` | Affine transform of CHIRPS 0.05° grid                 |
| `shape`            | (rows, cols) of CHIRPS grid                           |
| `hybas_path`       | Path to HydroBASINS L06 polygons                      |

`gdf_fsi` must contain the columns: `FSI_masked`, `geometry`, and `HYBAS_ID` (added during compute_fsi_v1_2).

---

## Outputs

| Output        | Description                                              |
|---------------|----------------------------------------------------------|
| `fsi_rescaled`  | 2D float32 raster (0–1, NaN outside empirical basins)    |

This raster is:

- CHIRPS‑aligned
- hydrologically consistent
- rescaled to 0–1
- NaN outside India or proxy basins

---

## Key Features of This Implementation

**1. Robust HYBAS Basin ID Detection**
The module automatically detects the correct basin ID column:

`HYBAS_ID`, `HYBAS_ID_1`, `HYBAS_ID_12`, `HYBAS_ID_6`, `MAIN_BAS`, `PFAF_ID`

This makes the rasteriser dataset‑agnostic and resilient to HYBAS variants.

**2. CRS Safety**

If IndoFloods FSI and HYBAS polygons differ in CRS:

```python
gdf_fsi = gdf_fsi.to_crs(hybas.crs)
```
This ensures spatial joins are always correct.

**3. Basin‑wise Aggregation**
FSI is aggregated per basin:

```python
mean FSI_masked for all gauges in basin
```
This avoids point‑level noise and produces a hydrologically meaningful surface.

**4. Clean Rasterisation**
Rasterisation uses:

```python
rasterio.features.rasterize()
```
with:

- `NaN` fill
- `float32` dtype
- CHIRPS transform

**5. Rescaling to 0–1**
After rasterisation:

```python
fsi_rescaled = (fsi_raster - min) / (max - min)
```
Only valid pixels are rescaled; NaNs remain untouched.

---

## FSI Raster Characteristics

| Property        | Value / Description                         |
|-----------------|----------------------------------------------|
| Grid            | CHIRPS 0.05° grid                            |
| CRS             | EPSG:4326                                    |
| Data type       | float32                                      |
| Value range     | 0–1 (susceptibility)                         |
| Nodata          | NaN                                          |
| Method          | Basin‑wise rasterisation                     |
| Alignment       | Matches CHIRPS transform exactly             |

---

Function Overview

| Function                     | Purpose                                      |
|------------------------------|----------------------------------------------|
| `rasterise_clean_rescale_fsi` | Basin‑wise rasterisation + cleaning + scaling |

---

## Usage Example

```python
from ccart.flood.fsi.rasterise_fsi import rasterise_clean_rescale_fsi

fsi_rescaled = rasterise_clean_rescale_fsi(
    gdf_fsi=gdf_fsi,
    chirps_transform=transform,
    shape=(rows, cols),
    hybas_path="HYBAS_L06.shp"
)
```
---

## Notes

- FSI must already be computed and masked (FSI_masked column).
- HYBAS L06 is required for hydrologically meaningful basin assignment.
- This module produces the **canonical static FSI raster** used by:
    - hazard engine
    - CCART‑Number
    - future CMIP6 workflows