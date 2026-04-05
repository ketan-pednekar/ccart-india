# CCART‑Floods — Flood Susceptibility Index (FSI) Subsystem

The **FSI subsystem** provides the foundational susceptibility layers used in
CCART‑Floods. It transforms raw INDOFLOODS catchment descriptors and
HydroBASINS hydrological structure into a continuous, national‑scale
susceptibility raster aligned with CHIRPS resolution.

FSI is **not** a flood probability or hazard metric.  
It is a **structural susceptibility index** that reflects how catchments respond
to rainfall based on long‑term geomorphology, soils, and basin organisation.

---

## Overview of the FSI Pipeline

The subsystem consists of four clean, modular stages:

1. **FSI v1.1 — Empirical Susceptibility**  
   Purely geomorphological and soil‑based susceptibility derived from
   INDOFLOODS catchment descriptors.

2. **FSI v1.2 — Hydrologically Enhanced Susceptibility**  
   Adds HydroBASINS upstream area and empirical/proxy basin classification.

3. **Rasterisation**  
   Converts point‑based FSI v1.2 into a CHIRPS‑aligned raster  
   **without interpolation**, preserving empirical honesty.

4. **Export**  
   Writes the final susceptibility raster to GeoTIFF with correct metadata.

This pipeline produces the canonical susceptibility layer used in the CCART
hazard engine.

---

## Files in This Module

| File | Purpose |
|------|---------|
| `build_fsi_v1_1.py` | Computes FSI v1.1 from INDOFLOODS geomorphology + soils |
| `build_fsi_v1_2.py` | Enhances FSI v1.1 using HydroBASINS hydrological context |
| `rasterise_fsi.py` | Rasterises, cleans, and rescales FSI v1.2 to CHIRPS grid |
| `export_fsi_raster.py` | Writes the final susceptibility raster to GeoTIFF |
| `utils_fsi.py` | Normalisation, soil encoding, spatial joins, raster masking |
| `config.py` | Paths and constants used across the subsystem |

Each `.py` file has a corresponding `.md` documentation file.

---

## FSI v1.1 — Empirical Susceptibility

FSI v1.1 uses only INDOFLOODS catchment descriptors:

- Drainage density  
- Catchment relief  
- Ruggedness number  
- Elongation ratio  
- Form factor  
- Annual precipitation  
- Soil type (one‑hot encoded → `Soil_block`)

All variables are min–max normalised and averaged:

```python
FSI_v1_1 = mean([geomorphology_norm, Soil_block])
```
This produces a **0–1 empirical susceptibility index**.

---

## FSI v1.2 — Hydrological Enhancement

FSI v1.2 integrates HydroBASINS Level‑6 hydrological structure:

- `UP_AREA` — upstream contributing area  
- `SUB_AREA` — local sub‑basin area  
- `ORDER` — Strahler order  
- `Proxy_flag` — 1 if basin has no INDOFLOODS gauges  

To avoid overweighting hydrology, only `UP_AREA_norm` is used:

```python
FSI_v1_2 = 0.5 * FSI_v1_1 + 0.5 * UP_AREA_norm
```
Proxy basins are masked:
`Proxy_flag = 1 → FSI_masked = NaN`

This ensures susceptibility exists only where empirical data supports it.

---

## Rasterisation

FSI v1.2 is computed at gauge points.  
To combine it with rainfall hazards (CHIRPS, CMIP6), it must be aligned to the
same grid.

`rasterise_fsi.py` performs:

- Rasterisation of `FSI_masked` to the CHIRPS grid  
- Cleaning (retain only 0–1 values, else NaN)  
- Min–max rescaling to full 0–1 range  

**No interpolation is performed.**  
This preserves hydrological honesty and avoids fabricating values in proxy basins.

Output:

- `fsi_rescaled` — final susceptibility raster (0–1, NaN outside empirical basins)

---

## Export

`export_fsi_raster.py` writes the final susceptibility raster to GeoTIFF with:

- float32 precision  
- NaN nodata  
- EPSG:4326 CRS  
- CHIRPS grid alignment  
- LZW compression  

This file is consumed directly by the hazard engine.

---

## Utilities

`utils_fsi.py` provides:

- `normalise()` — min–max scaling  
- `encode_soils()` — one‑hot + soil block  
- `spatial_join_points_to_polygons()` — wrapper for within joins  
- `mask_to_boundary()` — polygon masking for rasters  

These utilities keep the subsystem modular and reproducible.

---

## Running the Full Pipeline

```python
from ccart_floods.fsi.build_fsi_v1_1 import build_fsi_v1_1
from ccart_floods.fsi.build_fsi_v1_2 import build_fsi_v1_2
from ccart_floods.fsi.rasterise_fsi import rasterise_clean_rescale_fsi
from ccart_floods.fsi.export_fsi_raster import export_fsi_raster

gdf_v1_1 = build_fsi_v1_1()
gdf_v1_2 = build_fsi_v1_2(gdf_v1_1)

fsi_rescaled = rasterise_clean_rescale_fsi(
    gdf_fsi_v1_2=gdf_v1_2,
    chirps_transform=chirps_transform,
    shape=shape
)

export_fsi_raster(fsi_rescaled, chirps_transform, "ccart_floods_fsi_v1_2_rescaled.tif")
```
---

## Notes

- FSI is a susceptibility index, not a hazard or probability.
- Proxy basins remain NaN throughout the pipeline.
- HydroBASINS Level‑6 provides a balance between detail and stability.
- All rasters use EPSG:4326 and CHIRPS resolution.
- The pipeline is fully reproducible and open‑source.
