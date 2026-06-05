# 🔥 CCART‑Heat Wet Bulb Temperature (WBT) Engine

Deterministic, Transparent, Reproducible

The CCART‑Heat WBT Engine computes daily Wet Bulb Temperature using the Stull (2011) empirical approximation, applied over the canonical 0.05° India grid.
It provides a Dask‑parallelized, xarray‑native interface suitable for large‑scale climate hazard computation.

This module enforces CCART’s principles of scientific transparency, geospatial consistency, and reproducible climate diagnostics.

## 🎯 Purpose

The WBT engine ensures that daily WBT fields are:

- physically consistent with Stull (2011)
- aligned with the CCART ingestion grid
- computed lazily for large‑scale Dask workflows
- ready for exceedance engines, time‑slice cubes, and hazard maps
- reproducible across scenarios and CMIP6 models

It is the core physics engine of CCART‑Heat.

---

## 🧪 Scientific Basis: Stull (2011) Formula

The engine implements the widely used Stull (2011) empirical approximation for wet bulb temperature:

Tw = T * arctan(0.151977 * (RH + 8.313659)^(1/2)) + arctan(T + RH) - atan(RH - 1.676331) + 0.00391838 * RH^(3/2) * arctan(0.023101 * RH) - 4.686035

Where

`T`= dry bulb temperature in °C
`RH`= relative humidity in %
`Tw` = wet bulb temperature in °C

This approximation is:

- computationally efficient
- stable across tropical humidity regimes
- suitable for hazard‑mapping and operational diagnostics

---

## ⚙️ What the Engine Does

### 1. Dask‑Parallelized WBT Computation

Uses `xarray.apply_ufunc` with:

- lazy evaluation
- chunk‑safe broadcasting
- Dask parallelization

Enabling multi‑decade CMIP6 runs on national‑scale grids.

### 2. Time Alignment

Ensures tasmax and hurs share identical time coordinates:

- avoids silent mismatches
- guarantees deterministic WBT fields

### 3. Kelvin → Celsius Conversion

Converts CMIP6 tasmax from Kelvin to Celsius before applying Stull.

4. Clean Output
Returns a lazily evaluated `xr.DataArray`:

- name: "wbt"
- units: "°C"
- dims: [time, lat, lon]

Ready for:

- WBT exceedance cubes
- time‑slice aggregation
- CCART Number computation
- plant‑level sampling

---

## 🧭 Why This Engine Matters

WBT is the primary physical driver of:

- human heat‑stress exceedances
- cooling‑tower efficiency and condenser back‑pressure
- joint tasmax–WBT hazard metrics

The WBT engine ensures:

- no unit errors
- no misaligned humidity fields
- no silent broadcasting issues
- no non‑deterministic behavior

It is the physics foundation of CCART‑Heat.

---

## 📦 When to Run It

Run the WBT engine:

- after ingestion validation
- before exceedance computation
- before generating time‑slice cubes
- when adding new CMIP6 models or scenarios
- adding WBT to ingested cubes

It is the first physics step in the CCART‑Heat hazard pipeline.