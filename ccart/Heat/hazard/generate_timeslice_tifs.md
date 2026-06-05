# 🔥 CCART‑Heat — Time‑Slice TIFF Generator

Hazard Map Export from Time‑Slice Cubes (WBT>35°C, 0.05° India Grid)

---

## 🧭 Overview

This module converts time‑slice Zarr cubes into center‑aligned GeoTIFF hazard maps for:

- Historical (1995–2014)
- Near‑Term (2027–2039)
- Mid‑Century (2040–2069)
- End‑Century (2081–2100)

Each TIFF represents:

```
Max annual exceedance (WBT > 35°C) across the time slice
```

These TIFFs are the official CCART‑Heat hazard layers used for:

- GIS visualization
- animations
- district‑level overlays
- exposure and risk analysis
- public‑facing maps

This script performs no scientific computation — it only exports validated time‑slice cubes into geospatially correct TIFFs.

---

## 🎯 Purpose

This module ensures that CCART‑Heat hazard maps are:

- perfectly aligned to the canonical 0.05° India grid
- center‑affine georeferenced
- masked cleanly to India’s strict boundary
- GIS‑ready and CLIMADA‑ready
- reproducible and deterministic

It is the final step before visualization and dissemination.

---

## ⚙️ What the Script Does

### ✔ 1. Loads time‑slice cubes

From:

```
outputs/timeslice_cubes/
```

Each cube contains:

```
wbt35(lat, lon)
```

### ✔ 2. Loads strict India boundary

Using:

```
districts.gpkg → dissolved → single India polygon
```
This ensures a clean, hole‑free national mask.


### ✔ 3. Builds a center‑aligned affine transform

Using:

```
dx = lon spacing
dy = lat spacing

Affine(
    dx, 0, lon_min - dx/2,
    0, -dy, lat_max + dy/2
)
```

This guarantees:

- perfect pixel‑center alignment
- compatibility with CCART‑Flood
- compatibility with ingestion grid

### ✔ 4. Ensures correct latitude orientation

If lat is ascending, the array is flipped:

```
if lat[0] < lat[-1]:
    arr = arr[::-1, :]
```

### ✔ 5. Rasterizes strict India mask on the TIFF grid

Using the same affine transform.

### ✔ 6. Applies the mask

Pixels outside India are set to 0.0.

### ✔ 7. Writes GeoTIFF hazard maps

Example output:

```
CCART_Hazard_WBT35_Historical_1995-2014.tif
```

TIFFs use:

- EPSG:4326
- LZW compression
- float32
- nodata = NaN
- center‑aligned transform

---

### 📦 Inputs

- Time‑slice cubes:

    - `cube_timeslice_wbt35_Historical_1995-2014.zarr`
    - `cube_timeslice_wbt35_NearTerm_2027-2039.zarr`
    - `cube_timeslice_wbt35_MidCentury_2040-2069.zarr`
    - `cube_timeslice_wbt35_EndCentury_2081-2100.zarr`

- Strict India boundary (districts dissolved)

---

## 📤 Outputs

Four GeoTIFF hazard maps:

```
CCART_Hazard_WBT35_Historical_1995-2014.tif
CCART_Hazard_WBT35_NearTerm_2027-2039.tif
CCART_Hazard_WBT35_MidCentury_2040-2069.tif
CCART_Hazard_WBT35_EndCentury_2081-2100.tif
```

Each TIFF contains:

```
float32 hazard raster
center‑aligned 0.05° grid
strict India mask applied
```

## 🧪 Safety Features

- Center‑aligned affine transform
- Strict India mask rasterized on the TIFF grid
- Latitude orientation correction
- Overwrites existing TIFFs
- Deterministic export
- No scientific computation (pure export layer)

---

## 🧱 Code Summary (Annotated)

```python
# Load time-slice cube
da = xr.open_zarr(cube_path)["wbt35"]

# Build center-aligned affine
transform = Affine(dx, 0, lon_min - dx/2,
                   0, -dy, lat_max + dy/2)

# Flip if lat ascending
if lat[0] < lat[-1]:
    arr = arr[::-1, :]

# Rasterize strict India mask
india_mask = rasterize([(india_poly, 1)], out_shape=arr.shape, transform=transform)

# Apply mask
arr[india_mask == 0] = 0.0

# Write TIFF
dst.write(arr, 1)
```
---

## 🧭 When to Use This Tool

Run this script:

- after time‑slice cubes are generated
- before GIS visualization
- before animations
- before exposure/risk analysis
- when preparing public‑facing hazard maps

This script is not part of ingestion, WBT computation, or exceedance computation.

---

## 📝 Notes

- Only WBT>35°C is exported here.
- No DEM mask or strict mask is computed — both are already applied upstream.
- This script is deterministic and safe to run multiple times.
- TIFFs produced here are the final hazard layers used in CCART‑Heat.