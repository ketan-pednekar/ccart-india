# 🔍 CCART‑Heat Ingestion Validator

Deterministic, Transparent, Reproducible

The CCART‑Heat ingestion validator is a lightweight but essential diagnostic tool that confirms the integrity of the ingested tasmax/hurs datasets before they enter the WBT and exceedance engines.

It enforces CCART’s core principles of reproducibility, geospatial consistency, and scientific transparency.

## 🎯 Purpose

The validator ensures that the ingestion module has produced a dataset that is:

- geospatially aligned with the canonical 0.05° India grid
- physically valid for WBT computation
- free of missing coastal or NE pixels
- internally consistent across tasmax and hurs
- ready for hazard computation without manual inspection
- It is the final gate before the WBT engine.

## 🧪 What the Validator Checks

### 1. Variable Integrity

Ensures both tasmax and hurs exist and contain valid numerical ranges.
See: variable integrity checks

### 2. Time Alignment
Confirms that tasmax and hurs share identical time coordinates.
See: time alignment

### 3. Spatial Bounds

Verifies that the dataset matches the canonical CCART grid:

```
lat: 5.95 → 38.05  
lon: 67.95 → 98.05  
```
See: canonical grid bounds

### 4. Grid Spacing

Checks that:

```
dlat = 0.05  
dlon = 0.05
```
This guarantees perfect alignment with CCART‑Flood.

See: 0.05° spacing

### 5. Value Sanity

tasmax min/max in physically meaningful Kelvin range

hurs in [0, 100] after RH correction

See: RH validation logic

### 6. NaN Detection

Ensures no missing pixels after Big‑BBox regridding — especially:

- Tamil Nadu coast
- Gujarat coast
 -Sundarbans
- NE India

See: NaN detection

## 🧭 Why This Validator Matters

CCART’s ingestion pipeline is deterministic, but climate data is not always clean.

The validator ensures:

- no silent failures
- no misaligned grids
- no missing pixels
- no corrupted RH values
- no time mismatches

It is the scientific contract between ingestion and hazard engines.

## 📦 When to Run It

Run the validator:

- after a fresh ingestion
- after updating CMIP6 files
- after modifying paths.yaml
- after changing the canonical grid
- before running WBT exceedance cubes

It takes seconds and prevents hours of downstream debugging.

## 🧭 Next Step

Proceed to the WBT Engine, confident that ingestion is clean, aligned, and hazard‑ready.