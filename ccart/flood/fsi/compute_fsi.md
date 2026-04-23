# CCART‑Floods — Unified FSI Builder (`compute_fsi.py`)

## Purpose

`compute_fsi.py` constructs the **Flood Susceptibility Index (FSI)** used by the CCART‑Floods hazard engine.

It unifies two stages of susceptibility modelling:

- **FSI v1.1** — empirical IndoFloods geomorphology + soils
- **FSI v1.2** — hydrology‑enhanced susceptibility using HydroBASINS

The final output is a **0–1 susceptibility index** (with NaN for ungauged basins) that represents how **naturally flood‑prone each catchment is**, independent of rainfall.

This FSI is multiplied with rainfall anomalies to produce **climate‑conditioned flood hazard**.

---

## Scientific Background

FSI is a **catchment‑scale susceptibility index**, not a flood depth or inundation model.
It captures the *intrinsic* tendency of a basin to generate floods when rainfall occurs.

---

### Stage 1 — FSI v1.1 (IndoFloods empirical susceptibility)

IndoFloods provides catchment‑level descriptors for each gauge:

| Variable | Meaning | Why It Matters |
|----------|---------|----------------|
| Drainage Density | Total stream length / basin area | Higher density → faster runoff |
| Catchment Relief | Elevation difference | Steeper basins → flashier floods |
| Ruggedness Number | Relief × drainage density | Terrain complexity indicator |
| Elongation Ratio | Basin shape metric | Circular basins flood faster |
| Form Factor | Width/length ratio | Controls hydrograph shape |
| Annual Precipitation | Long-term rainfall | Climatic forcing |
| Soil Type | Categorical soil class | Controls infiltration/runoff |

Each variable is **min–max normalised** to 0–1.
Soil categories are one‑hot encoded and averaged into a composite `Soil_block`.

**FSI v1.1 formula:**

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
This produces a **0–1 empirical susceptibility score** for each gauge.

### Stage 2 — FSI v1.2 (Hydrology‑enhanced susceptibility)

HydroBASINS provides basin polygons and hydrological attributes:

| Variable | Meaning | Why It Matters |
|----------|---------|----------------|
| UP_AREA | Total upstream contributing area | Larger upstream → more inflow → higher susceptibility |
| SUB_AREA | Area of the basin polygon | Basin size context |
| ORDER | Strahler stream order | Maturity of river network |
| n_gauges | Number of IndoFloods gauges in basin | Indicates empirical support |
| Proxy_flag | 1 = no gauges, 0 = has gauges | Used to mask ungauged basins |

Each hydrological variable is **normalised to 0–1**.

Gauges are spatially joined to basins.

Basins with **no IndoFloods gauges** are marked as:

```python
Proxy_flag = 1
```
These basins are masked (set to NaN) to avoid false confidence.

**FSI v1.2 formula:**

```python
FSI_v1_2 = 0.5 * FSI_v1_1 + 0.5 * UP_AREA_norm
```

This blends empirical susceptibility with hydrological context.

**Final Output**

The recommended FSI for CCART‑Floods is:

```python
FSI = FSI_v1_2 (masked for proxy basins)
```
This is a **0–1 susceptibility raster** after spatialisation and rasterisation.

---

## Inputs

| File | Description |
|------|-------------|
| `CATCHMENT_CSV` | IndoFloods geomorphology + soil descriptors |
| `META_CSV` | Gauge metadata (coordinates, basin, state) |
| `HYBAS_SHP` | HydroBASINS polygons with hydrological attributes |
| `INDIA_SHP` | India boundary for masking and spatial filtering |


All paths are loaded from `paths.yaml` via `load_paths()`.

---

## Outputs

| Output | Description |
|--------|-------------|
| `GeoDataFrame` | Gauge-level susceptibility with FSI v1.1 and FSI v1.2 |
| `FSI_masked` | Final susceptibility (0–1, NaN for proxy basins) |
| `geometry` | EPSG:4326 point geometry for each gauge |

This output is ready for rasterisation and direct use in the hazard engine.

---

## Functions in This Module

`compute_fsi_v1_1()`

Builds empirical susceptibility using IndoFloods descriptors.

Steps:

1. Load catchment descriptors + metadata
2. Normalise geomorphology
3. Encode soil types
4. Compute Soil_block
5. Compute FSI v1.1 (0–1)
6. Return GeoDataFrame with point geometry

---

`compute_fsi_v1_2(gdf_v1_1)`

Adds hydrological context using HydroBASINS.

Steps:

1. Load HydroBASINS + India boundary
2. Identify proxy basins (no gauges)
3. Spatial join gauges → basins
4. Normalise hydrological variables
5. Compute FSI v1.2
6. Apply proxy mask
7. Return enhanced GeoDataFrame

---

`compute_fsi()`

Unified entry point.

Steps:

1. Compute FSI v1.1
2. Compute FSI v1.2
3. Return final susceptibility layer

---

## Usage Example

```python
from ccart.flood.fsi.compute_fsi import compute_fsi

gdf_fsi = compute_fsi()
print(gdf_fsi[["GaugeID", "FSI_masked"]].head())
```
---

## Notes

- FSI is a **susceptibility index**, not a flood depth or probability.
- All variables are **normalised** to ensure equal weighting.
- Proxy basins (no IndoFloods gauges) are masked to avoid over‑interpretation.
- FSI is rasterised to the CHIRPS grid before entering the hazard engine.
-  The final hazard is computed as:
    ```python
    Hazard = FSI × Rainfall Anomaly
    ```