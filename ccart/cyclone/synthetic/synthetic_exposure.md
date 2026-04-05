# CCART Synthetic Exposure Module

***District loading, coastal distance computation, and exposure–hazard clipping***

The synthetic_exposure.py module provides all preprocessing steps required to prepare district geometries and exposure points for synthetic cyclone impact modelling. It handles:

- loading and normalizing district boundaries
- computing centroid distance to coastline
- identifying inland districts
- clipping exposure points to the hazard footprint

These steps ensure that downstream hazard, impact, calibration, and HWE computations operate on a clean, spatially consistent dataset.

---

## 🌍 Purpose

Synthetic cyclone modelling requires:

- **District geometries** for aggregation
- **Coastal distance** to determine inland masking
- **Exposure points** clipped to the hazard footprint

This module centralizes all of these tasks, keeping the synthetic driver clean and modular.

---

## 📁 Module Contents

| Function                   | Purpose                                           |
|---------------------------|---------------------------------------------------|
| `_normalize_name`         | Standardizes district/state names                 |
| `load_districts`          | Loads and normalizes district geometries          |
| `compute_distance_to_coast` | Computes centroid distance to coastline and inland mask |
| `clip_exposure_to_hazard` | Clips exposure points to the hazard bounding box  |

---



## 🔧 Function‑Level Documentation

### `_normalize_name(series)`

Standardizes district/state names by:

- stripping whitespace
- converting to uppercase
- collapsing multiple spaces

Used internally by `load_districts`.


### `load_districts(districts_path, district_col="district", state_col="state")`

Loads district boundaries from a GeoJSON/GeoPackage file and returns a clean GeoDataFrame with:

- `District` normalized name
- `state_norm` normalized state/region name
- `geometry` district polygon

Ensures CRS is **EPSG:4326**.

**Returns:**

A GeoDataFrame with normalized district geometries.

**Country‑agnostic:**  
Column names can be customized for any administrative dataset.

### `compute_distance_to_coast(districts_gdf, coastline_gdf, inland_clip_km)`

Computes the centroid distance (in km) from each district to the coastline.

Steps:

1. Reproject districts and coastline to **EPSG:3857**
2. Compute centroid distance to coastline union
3. Convert meters → km
4. Mark districts as inland if:

`dist_to_coast_km > inland_clip_km`

Adds two columns:

- `dist_to_coast_km`
- `is_inland`

**Returns:**  

Updated districts GeoDataFrame.

**Note:**  
Coastline must be supplied as a GeoDataFrame (consistent with the synthetic generator).

### `clip_exposure_to_hazard(exposures, hazard)`

Clips exposure points to the bounding box of the hazard footprint.

Bounding box is computed from hazard centroids:

- `lat_min`, `lat_max`
- `lon_min`, `lon_max`

Exposure points outside this box are removed.

**Returns:**

A new `Exposures` object containing only clipped points.

**Raises:**

ValueError if no exposure points remain after clipping.

---

## 🧩 How This Module Fits Into the Synthetic Pipeline

This module is used in the synthetic driver immediately after hazard generation:

```Python

districts = load_districts(...)
districts = compute_distance_to_coast(districts, coastline_gdf, INLAND_CLIP_KM)
exposure = clip_exposure_to_hazard(exposure_all, hazard)
```
It prepares all spatial inputs for:

- hazard masking
- impact computation
- calibration
- HWE
- mapping

This keeps the synthetic driver clean and focused on orchestration rather than preprocessing.

---

## ⚠️ Notes & Caveats

- District geometries must be in **EPSG:4326**; the module enforces this.
- Coastline must be supplied as a **GeoDataFrame**
- Exposure clipping is purely bounding‑box based; hazard masking happens later.
- Exposure points must be point geometries in **EPSG:4326**.
- This module does not load **LitPop** — that remains in `ccart.exposure`.

## 🎯 Summary

`synthetic_exposure.py` provides all spatial preprocessing required for synthetic cyclone impact modelling:

- clean district geometries
- coastal distance
- inland masking
- exposure clipping

It is the first major spatial building block in the modular synthetic pipeline, ensuring that all downstream computations operate on a clean, consistent, country‑agnostic dataset.