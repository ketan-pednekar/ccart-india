# 🔥 CCART‑Heat — Exceedance Cube Builder

Clean WBT>35 Annual Exceedance Reconstruction (Strict Mask + DEM Mask via Engine)

---

## 🧭 Overview

This script performs a full clean rebuild of the CCART‑Heat WBT>35°C annual exceedance cubes for:

- Historical (1995–2014)
- SSP370 (2015–2100)
- SSP585 (2015–2100)

It deletes the existing `exceedance/` folder and regenerates only the WBT>35°C exceedance cubes, using the official CCART exceedance engine:

- `compute_annual_exceedances`
- `finalize_exceedance_cube` (strict mask + DEM mask)

This version is the final, modular, production‑ready exceedance builder.

---

## 🎯 Purpose

This script ensures that CCART‑Heat exceedance cubes are:

- clean
- mask‑correct
- free of NE contamination
- aligned with ingestion grid
- reproducible
- ready for time‑slice and hazard workflows

It is used when:

- ingestion was updated
- WBT was recomputed
- DEM mask changed
- strict India mask changed
- exceedance cubes need a clean rebuild

---

## ⚙️ What the Script Does

### ✔ 1. Deletes the entire exceedance/ folder

Ensures no stale cubes remain.

### ✔ 2. Loads DEM lowland mask

Used by `finalize_exceedance_cube`.

### ✔ 3. Loads ingested WBT cubes

From:

```
ingested/hist/
ingested/ssp370/
ingested/ssp585/
```

### ✔ 4. Computes annual exceedance counts

Using:

```
compute_annual_exceedances(Tw, 35, years)
```

### ✔ 5. Applies strict India mask + DEM mask

Handled inside:

```
finalize_exceedance_cube(da_raw, india_shp, dem_mask)
```
This ensures:

- center‑affine strict mask
- DEM lowland mask
- no NE contamination
- no high‑elevation artifacts

### ✔ 6. Saves clean Zarr cubes

One per scenario:

```
cube_hist_wbt35.zarr
cube_ssp370_wbt35.zarr
cube_ssp585_wbt35.zarr
```

### ✔ 7. Runs top‑100 validation

Ensures cubes are non‑empty and physically plausible.

## 📦 Inputs

- Ingested WBT cubes (`tasmax`, `hurs`, `wbt`)
- DEM lowland mask (≤500 m)
- India boundary (for strict mask)
- Scenario year ranges

## 📤 Outputs

Three clean exceedance cubes:

```
exceedance/cube_hist_wbt35.zarr
exceedance/cube_ssp370_wbt35.zarr
exceedance/cube_ssp585_wbt35.zarr
```
Each contains:

```
wbt35(year, lat, lon)
```
---

## 🧪 Safety Features

- Full folder reset  
    Guarantees no stale data.

- Strict mask + DEM mask inside engine  
    Ensures spatial purity.

- Scenario‑specific year ranges  
    Ensures correct temporal slicing.

- Top‑100 validation  
    Detects empty cubes or masking errors.

---

## 🧱 Code Summary (Annotated)

```python

# 1. Reset exceedance folder
shutil.rmtree(out_root)

# 2. Load DEM mask
dem_mask = load_dem_mask()

# 3. For each scenario:
Tw = ds["wbt"]
da_raw = compute_annual_exceedances(Tw, 35, years)

# 4. Apply strict mask + DEM mask
da_final = finalize_exceedance_cube(da_raw, india_shp, dem_mask)

# 5. Save cube
da_final.to_zarr(out_path, mode="w")

# 6. Validate
validate_top100(out_path, name)
```
---

## 🧭 When to Use This Tool

Run this script when:

- ingestion was regenerated
- WBT was recomputed
- DEM mask changed
- strict India mask changed
- exceedance cubes need a clean rebuild
- validating CCART‑Heat before GitHub release

This script is not part of ingestion and should be run manually.

---

## 📝 Notes

- Only WBT>35°C exceedances are computed here.
- No TIFFs or maps are generated.
- No other thresholds (28/30/32) are included.
- This script is deterministic and safe to run multiple times.
- It is the final, modular version using `finalize_exceedance_cube`.