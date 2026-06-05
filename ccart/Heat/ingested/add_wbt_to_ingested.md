# 🔧 CCART‑Heat Utility — Add WBT to Ingested Zarr Stores

Post‑Ingestion Wet Bulb Temperature (WBT) Patch Tool

## 🧭 Overview

This utility script adds Wet Bulb Temperature (WBT) to already‑ingested CCART‑Heat Zarr datasets.

It is a post‑processing tool, used when ingestion has already produced:

- tasmax (K)
- hurs (0–100 %)

but WBT has not yet been computed or stored.

This script applies the official CCART WBT Engine (Stull 2011) to each scenario and appends the resulting wbt variable directly into the existing Zarr stores.

It is intentionally kept separate from the ingestion module to preserve CCART’s clean architecture:

```
Ingestion → WBT Engine → Exceedance → Time‑Slices → Hazard Maps
```
---

## 🎯 Purpose

This script ensures that all ingested datasets contain:

- tasmax
- hurs
- wbt  ← added by this tool

It is used when:

- WBT was not computed during ingestion
- WBT engine was updated and needs re‑running
- new CMIP6 scenarios were added
- existing Zarr stores need patching without re‑ingesting data

## ⚙️ What the Script Does

### ✔ 1. Iterates over all ingested scenario folders

```
ingested/hist  
ingested/ssp370  
ingested/ssp585
```

### ✔ 2. Opens each Zarr store lazily using xarray

### ✔ 3. Skips scenarios where WBT already exists

Prevents accidental overwriting.

### ✔ 4. Computes WBT using the CCART WBT Engine

Applies:

- Kelvin → Celsius conversion
- Stull (2011) approximation
- Dask‑parallelized computation

### ✔ 5. Appends wbt to the Zarr store in append mode

```
mode="a"
```

### ✔ 6. Leaves all other variables untouched

Safe, non‑destructive patching.

---

## 📦 Inputs

Existing CCART‑Heat ingested Zarr stores

- tasmax (K)
- hurs (0–100 %)
- CCART WBT Engine (`compute_wbt`)

---

## 📤 Outputs

Each Zarr store gains a new variable:

```
wbt(time, lat, lon)  # in °C
```
No other variables or metadata are modified.

---

## 🧪 Safety Features

- Skip if WBT exists  
    
    Prevents recomputation or accidental overwriting.

- Append‑only write mode  
    
    Ensures no data loss.

- Uses ingestion‑aligned grids  
    Guarantees perfect spatial consistency.

---

## 🧱 Code Summary (Annotated)

```python
ds = xr.open_zarr(store)

if "wbt" in ds:
    skip

tas = ds["tasmax"]
hur = ds["hurs"]

Tw = compute_wbt(tas, hur)

ds["wbt"] = Tw
ds.to_zarr(store, mode="a")
```
Simple, deterministic, and CCART‑consistent.

---

## 🧭 When to Use This Tool

Run this script:

- after ingestion, before exceedance
- when adding WBT to existing Zarr stores
- when updating the WBT engine
- when regenerating WBT for new CMIP6 models
- when validating ingestion outputs

It is not part of the ingestion pipeline and should not be run automatically.

---

## 📝 Notes

- This script is intentionally placed near the ingested Zarr stores for convenience.
- It may be moved to ccart/Heat/utils/ in future versions, but no change is required now.
- It is safe to run multiple times — scenarios with existing WBT are skipped.