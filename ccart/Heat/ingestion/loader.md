# CCART‑Heat Ingestion Module

## *0.05° India Grid — Big‑BBox Safe Version*

---

## 🧭 Overview

The CCART‑Heat ingestion module prepares CMIP6 daily **tasmax** and **hurs** data for downstream wet‑bulb temperature (WBT) and exceedance analysis.
This version implements the **Big‑BBox Safe Strategy**, which eliminates coastal pixel loss and ensures perfect alignment with the CCART‑Flood grid.

**✔ Key Guarantees**

- No Tamil Nadu coastal pixel loss
- No Northeast India pixel loss
- No regionmask clipping during ingestion
- Perfect alignment with CCART‑Flood (0.05° grid)
- Robust for ACCESS‑CM2 and other models with irregular coastal geometry

---

## 🗺️ Spatial Strategy

### 1. Big Raw Subset (Safe for ACCESS‑CM2)

Raw CMIP6 data is subset using a very large bounding box:

```
lon: 60 → 105°E  
lat:  0 → 40°N
```

This ensures all India‑adjacent pixels are included before interpolation.

### 2. Regrid to Canonical 0.05° India Grid

The canonical CCART grid:

```
lon: 67.95 → 98.05°E  
lat:  5.95 → 38.05°N  
res: 0.05°
```

This grid is shared with CCART‑Flood for cross‑hazard consistency.


### 3. Clip AFTER Regridding
Clipping is performed only after interpolation, preventing coastal loss.


## 📐 Big‑BBox → Canonical Grid Flow (Visual Diagram)

Raw CMIP6 (Big BBox)

┌──────────────────────────────┐
│ 60–105E, 0–40N               │
│   ↓ subset                   │
│   ↓ bilinear regrid          │
└──────────────┬───────────────┘
               ↓
Canonical CCART Grid (0.05°)
┌──────────────────────────────┐
│ 67.95–98.05E, 5.95–38.05N    │
└──────────────────────────────┘

---

## 🧭 Center‑Affine Georeferencing

All ingested datasets now include a center‑affine transform, ensuring perfect pixel‑center alignment with:

- strict India mask
- DEM mask
- WBT exceedance cubes
- CCART‑Flood rasters
- all downstream GeoTIFF outputs

This guarantees that every pixel corresponds to the true geographic center of the 0.05° grid cell.

The transform is written using:

```
Affine(dlon, 0, lon_min - dlon/2,
       0, dlat, lat_min - dlat/2)
```
This eliminates half‑pixel shifts and ensures reproducible raster alignment across all CCART modules.

---

## Strict India Mask Utility (Not Applied During Ingestion)

The ingestion module includes the strict India mask function, which:

- rasterizes the India boundary
- uses center‑affine alignment
- removes Bangladesh, Nepal, Bhutan, China, Myanmar, ocean pixels
- produces a clean, boolean mask aligned to the canonical grid

However:

The strict India mask is NOT applied during ingestion.  

It is applied only in the hazard engines (WBT exceedance, TXx anomalies, population exposure).

This keeps ingestion country‑agnostic, reusable, and free of political boundaries.

---

## 🧩 Module Architecture

### Inputs

- CMIP6 daily tasmax (K)
- CMIP6 daily hurs (%)
- India boundary (GeoPackage)
- Paths from paths.yaml

### Outputs

Zarr datasets for:

- ingested/hist/
- ingested/ssp370/
- ingested/ssp585/

Each contains:

```
tasmax(time, lat, lon)
hurs(time, lat, lon)
```
---

## 🧪 Relative Humidity Correction

Some CMIP6 models store hurs in 0–1 instead of 0–100.

The ingestion module:

- Detects this automatically
- Multiplies by 100 if needed
- Clips values to [0, 100]

This ensures WBT computation is physically valid.

### 🔧 Regridding Logic

Interpolation uses:

- Bilinear interpolation (method="linear")
- Target grid defined by canonical lat/lon arrays
- Chunking for performance (time=30, lat=200, lon=200)

This ensures:

- Smooth spatial transitions
- No aliasing
- Efficient Dask execution

---

## 🧱 Code Summary (Annotated)

Below is a structured explanation of the ingestion pipeline.

### 1. Load Paths

Paths are resolved via `load_heat_paths()`:

- `data_root/`
- `boundaries/`
- `ingested/hist/`
- `ingested/ssp370/`
- `ingested/ssp585/`

### 2. Define Grids

Big‑BBox for raw subset

```
60–105E, 0–40N
```
Canonical 0.05° India grid

```
67.95–98.05E  
5.95–38.05N  
resolution = 0.05°
```
### 3. Load India Boundary
Used only for downstream masking (not during ingestion).

### 4. Load Raw CMIP6 Files

Uses `open_mfdataset` with:

- `engine="h5netcdf"`
- `parallel=True`
- `chunks={"time": 365}`

This ensures fast, memory‑safe ingestion.

### 5. Fix Relative Humidity

Automatically detects 0–1 scaling and corrects it.

### 6. Regrid to Canonical Grid

Performed before clipping.

### 7. Clip to India Box

Performed after interpolation.

### 8. Save to Zarr

Each scenario is saved to:

```
ingested/hist/
ingested/ssp370/
ingested/ssp585/
```
---

## 🧪 Reproducibility Notes

- Ingestion is deterministic
- No regionmask is used
- All scenarios share the same grid
- Time alignment is enforced via intersection
- Zarr stores are chunked for downstream WBT computation

## 🧭 Recommended Validation

After ingestion, validate:

- Grid bounds
- Lat/lon spacing
- No missing coastal pixels
- No missing NE pixels
- RH values in [0, 100]
- Time alignment between tasmax and hurs

---

## 📦 Ready for Next Step

Continue to the WBT Engine