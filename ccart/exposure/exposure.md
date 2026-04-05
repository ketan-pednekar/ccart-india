# CCART Exposure Module

This module provides all exposure‑related operations for the CCART Cyclone Impact Engine.
It handles loading district boundaries, retrieving LitPop exposure, subsetting exposure to a state, and computing district‑level exposure totals.

The design is reusable across states, cyclones, and future hazard modules.

---

## 🌍 Purpose

Exposure is a core component of CCART’s impact modelling framework.

This module provides a consistent workflow to:

- load district boundaries
- retrieve LitPop exposure via the CLIMADA API
- subset exposure points to a specific state
- aggregate exposure to district level
- assign vulnerability curve IDs (`impf_TC`)

These functions ensure that exposure is standardized and compatible with CCART’s hazard and vulnerability modules.

---

## 🔧 Functions

**`load_districts(path, district_col="District", crs="EPSG:4326")`**

Load district boundaries for a state and standardize the geometry.

**Parameters**

| Parameter     | Type   | Description                                                   |
|---------------|--------|---------------------------------------------------------------|
| path          | str    | Path to district boundary file (GeoJSON, Shapefile, etc.).   |
| district_col  | str    | Column containing district names.                             |
| crs           | str    | Coordinate reference system to enforce (default EPSG:4326).   |

**Returns**

A GeoDataFrame with:

- `District`
- `geometry`

**`load_litpop_for_state(country_code, districts, cached_litpop=None)`**

Retrieve LitPop exposure for a country and subset it to the provided district polygons.

**Parameters**

| Parameter      | Type            | Description                                                                 |
|----------------|-----------------|-----------------------------------------------------------------------------|
| country_code   | str             | ISO country code for LitPop retrieval.                                      |
| districts      | GeoDataFrame    | District polygons used for spatial subsetting.                              |
| cached_litpop  | GeoDataFrame or None | Optional preloaded LitPop to avoid repeated API calls.                |

**Returns**

A tuple:

- **assets_state** — GeoDataFrame of LitPop points within the state
- **district_exp** — DataFrame of district‑level exposure totals

**Notes**

Exposure points are assigned a default vulnerability curve ID:

```python
assets_state["impf_TC"] = 1
```

Spatial join uses `predicate="within"` to ensure correct district assignment.

**`compute_district_exposure(assets_state, value_col="value")`**

Aggregate exposure points to district‑level totals.

**Parameters**

| Parameter      | Type        | Description                                              |
|----------------|-------------|----------------------------------------------------------|
| assets_state   | DataFrame   | Exposure points with `District` and exposure values.     |
| value_col      | str         | Column representing exposure magnitude (default: value). |

**Returns**

A DataFrame with:

- `District`
- `Exposure_Value`

---

## 📘 Usage Example

```python
from ccart.exposure.exposure import (
    load_districts,
    load_litpop_for_state,
    compute_district_exposure
)

districts = load_districts("path/to/districts.geojson")

assets_state, district_exp = load_litpop_for_state(
    country_code="IND",
    districts=districts
)

exp_dist = compute_district_exposure(assets_state)
```
---

## 🧱 Dependencies

- `geopandas`
- `pandas`
- `climada.util.api_client.Client`

---

## 🎯 Summary

The CCART Exposure Module:

- standardizes district boundaries
- retrieves and subsets LitPop exposure
- assigns vulnerability curve IDs
- computes district‑level exposure totals
- provides a reusable, hazard‑agnostic exposure workflow

It integrates seamlessly with CCART’s hazard, vulnerability, and impact modules.