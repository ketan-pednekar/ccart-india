# CCART v1.0 — Exposure Module

The exposure module provides all functions required to prepare exposure inputs
for the CCART Cyclone Impact Engine. It loads district boundaries, retrieves
LitPop exposure from the CLIMADA API, subsets it to a state, and aggregates
exposure to district level.

---

## 1. District Boundaries

### `load_districts(path, district_col="District", crs="EPSG:4326")`

Load and standardize district polygons for a state.

**Workflow:**
- Read GeoJSON/Shapefile
- Enforce EPSG:4326
- Standardize district name column
- Return only `District` and `geometry`

**Output:** GeoDataFrame of district boundaries.

---

## 2. LitPop Exposure for a State

### `load_litpop_for_state(country_code, districts, cached_litpop=None)`

Load LitPop exposure for a country and subset it to the districts of a state.

**Workflow:**
1. Load LitPop via CLIMADA API (or use cached version)
2. Reproject to match district CRS
3. Spatial join: assign each LitPop point to a district
4. Assign impact function ID (`impf_TC = 1`)
5. Aggregate exposure to district level

**Outputs:**
- `assets_state`: point-level LitPop exposure with district labels  
- `district_exp`: district-level exposure totals

---

## 3. District-Level Exposure Aggregation

### `compute_district_exposure(assets_state, value_col="value")`

Aggregate exposure values to district level.

**Workflow:**
- Group by `District`
- Sum exposure values
- Return clean DataFrame

**Output Columns:**
- `District`
- `Exposure_Value`
