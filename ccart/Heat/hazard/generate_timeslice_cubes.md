# 🔥 CCART‑Heat — Time‑Slice Cube Generator

Max Annual WBT>35°C Exceedance (0.05° India Grid)

## 🧭 Overview

The CCART‑Heat Time‑Slice Cube Generator converts annual exceedance cubes into four authoritative time‑slice hazard cubes:

- Historical (1995–2014)
- Near‑Term (2027–2039)
- Mid‑Century (2040–2069)
- End‑Century (2081–2100)

Each time‑slice cube contains the maximum annual exceedance (WBT>35°C) across the slice.

These cubes are the official source for:

- TIFF hazard maps
- animations
- GIS exports
- district‑level validation

This script performs no masking, no transforms, no TIFF writing.

It keeps the scientific pipeline clean and reproducible.

---

## 🎯 Purpose

This module ensures that CCART‑Heat time‑slice layers are:

- derived from validated exceedance cubes
- consistent across scenarios
- aligned with the canonical 0.05° India grid
- reproducible and deterministic
- ready for hazard visualization and analysis

It is the final preprocessing step before hazard map generation.

---

## ⚙️ What the Script Does

### ✔ 1. Loads validated exceedance cubes

From:

```
cube_hist_wbt35.zarr
cube_ssp370_wbt35.zarr
```

These cubes already include:

- strict India mask
- DEM mask
- lat‑orientation fix

### ✔ 2. Selects the correct scenario for each time slice

- Historical slices use the hist cube
- Future slices use the SSP370 cube


### ✔ 3. Extracts the time window

Example:

```
da.sel(year=slice(2027, 2039))
```

### ✔ 4. Computes the maximum annual exceedance

This produces a single hazard layer per slice:

```
max(WBT>35 exceedance days) across the slice
```

### ✔ 5. Adds metadata

Including:

- description
- year range
- source scenario
- grid definition

### ✔ 6. Saves each slice as a Zarr cube

Example:

```
cube_timeslice_wbt35_Historical_1995-2014.zarr
```

Each cube contains:

```
wbt35(lat, lon)
```

---

## 📦 Inputs

Annual exceedance cubes:

- `cube_hist_wbt35.zarr`
- `cube_ssp370_wbt35.zarr`

Time‑slice definitions:

- 1995–2014
- 2027–2039
- 2040–2069
- 2081–2100

---

## 📤 Outputs

Four time‑slice cubes:

```
cube_timeslice_wbt35_Historical_1995-2014.zarr
cube_timeslice_wbt35_NearTerm_2027-2039.zarr
cube_timeslice_wbt35_MidCentury_2040-2069.zarr
cube_timeslice_wbt35_EndCentury_2081-2100.zarr
```

Each contains:

```
wbt35(lat, lon)
```
with metadata describing the slice.

---

🧪 Safety Features

- Overwrites existing time‑slice cubes
- Uses validated exceedance cubes only
- No masking or transforms applied here
- Deterministic max‑aggregation
- Clean separation from TIFF generation

---

## 🧱 Code Summary (Annotated)

```python
# Load exceedance cubes
ds_hist = xr.open_zarr(CUBE_HIST)
ds_ssp  = xr.open_zarr(CUBE_SSP370)

# Select scenario
da = da_hist if cube_type == "hist" else da_ssp

# Slice years
da_slice = da.sel(year=slice(start, end)).max("year")

# Save as Zarr
da_slice.to_dataset(name="wbt35").to_zarr(out_path)
```
---

## 🧭 When to Use This Tool

Run this script:

- after exceedance cubes are rebuilt
- before generating TIFF hazard maps
- before animations or GIS exports
- when validating CCART‑Heat outputs
- when adding new time‑slice definitions

This script is not part of ingestion or exceedance computation.