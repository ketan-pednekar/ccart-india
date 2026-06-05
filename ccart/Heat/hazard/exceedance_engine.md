# 🔥 CCART‑Heat Exceedance Engine

Annual WBT>Threshold Exceedance Computation + Strict Mask + DEM Mask Finalization

---

## 🧭 Overview

The CCART‑Heat Exceedance Engine converts daily Wet Bulb Temperature (WBT) fields into annual exceedance cubes on the canonical 0.05° India grid.
It is the first hazard‑layer generator in the CCART‑Heat pipeline and forms the scientific bridge between:

```
Ingestion → WBT Engine → Exceedance Engine → Time‑Slices → Hazard Maps
```
This module provides two core functions:

`compute_annual_exceedances`  
→ Converts daily WBT into raw annual exceedance counts.

`finalize_exceedance_cube`  
→ Applies strict India mask, DEM mask, and lat‑orientation fixes.

Together, these functions produce clean, hazard‑ready exceedance cubes.

---

## 🎯 Purpose

The Exceedance Engine ensures that annual exceedance cubes are:

- geospatially aligned with ingestion
- masked cleanly to India’s strict boundary
- corrected for DEM‑invalid terrain
- consistent across scenarios and years
- ready for time‑slice aggregation and GeoTIFF export

It is the deterministic backbone of CCART‑Heat hazard generation.

---

## ⚙️ Engine Components

### 1. `compute_annual_exceedances(Tw, threshold, years)`

🔍 What it does

- Takes daily WBT (`Tw`)
- Applies threshold exceedance (`Tw > threshold`)
- Groups by `time.year`
- Sums exceedance days per year
- Selects only the requested year range


#### 📦 Output

- 1. A raw exceedance cube:

    ```
    [year, lat, lon]
    ```
    with no masks applied.


- ✔ Deterministic

    Uses xarray’s `groupby("time.year")` for reproducible annual grouping.


### 2. `finalize_exceedance_cube(da_raw, india_shp, dem_mask)`

This function transforms the raw exceedance cube into a hazard‑ready cube.

#### 🔧 Steps performed

- ✔ A. Latitude orientation fix

    Ensures north→south ordering for GIS compatibility.

- ✔ B. Strict India mask
    
    Applies CCART’s center‑affine strict boundary mask to remove:

    - ocean pixels
    - Bangladesh
    - Nepal
    - Bhutan
    - China
    - Myanmar

- ✔ C. DEM mask
    
    Zeroes out exceedances in high‑elevation terrain (>500 m).

- ✔ D. Variable rename

    Sets the final variable name:

    ```
    wbt35
    ```

#### 📦 Output

A clean, masked, hazard‑ready cube:

```
wbt35(year, lat, lon)
```

---

## 🧩 How the Engine Is Called (Important)

The Exceedance Engine is not run directly.

It is called by the scenario rebuild script:

`run_exceedance.py`

This script:

- Deletes the exceedance/ folder
- Loads ingested WBT cubes
- Calls:
    ```
    da_raw = compute_annual_exceedances(Tw, 35, years)
    da_final = finalize_exceedance_cube(da_raw, india_shp, dem_mask)
    ```

- Saves:
    ```
    cube_hist_wbt35.zarr
    cube_ssp370_wbt35.zarr
    cube_ssp585_wbt35.zarr
    ```
- Runs top‑100 validation

This separation keeps the engine pure and the rebuild script modular.

---

## 🧭 Why This Engine Matters

It guarantees:

- no misaligned rasters
- no missing pixels
- no DEM‑invalid exceedances
- no NE contamination
- no threshold inconsistencies
- no scenario‑specific surprises

It is the scientific contract between climate data and hazard layers.

---

## 📦 When to Use the Exceedance Engine

Use this engine when:

- rebuilding exceedance cubes
- adding new scenarios
- adding new thresholds
- updating DEM mask
- updating strict India mask
- validating hazard layers before release

---

## 🧭 Next Step

Proceed to the Time‑Slice Engine, which converts annual exceedance cubes into:

- historical
- near‑term
- mid‑century
- end‑century

hazard layers.