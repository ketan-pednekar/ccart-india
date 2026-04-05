# CCART Historical Cyclone Hazard Module

***IBTrACS → CLIMADA → District‑Level Hazard Statistics***

This module provides all functions required to reconstruct historical tropical cyclone hazards using:

- IBTrACS best‑track data
- CLIMADA’s TropCyclone engine
- CCART’s district‑level hazard aggregation tools

It is country‑agnostic and suitable for any region with IBTrACS coverage and administrative boundaries.

---
## 🔧 Prerequisites

- Python 3.10+
- CLIMADA installed
- District boundaries in **EPSG:4326**
- IBTrACS NetCDF file containing the requested storm ID

---

## 🌍 Purpose

Historical cyclone analysis requires:

- loading best‑track data
- building a centroid grid around the storm
- generating CLIMADA windfield footprints
- cleaning and validating hazard matrices
- aggregating intensities to districts

This module performs all these steps in a clean, reproducible workflow.

---

## 📁 Module Contents

| Function                     | Purpose                                         |
|------------------------------|-------------------------------------------------|
| `build_hazard`               | Builds a CLIMADA cyclone hazard from IBTrACS track data |
| `compute_district_hazard_stats` | Aggregates centroid‑level intensities to district‑level statistics |

---

## 🔧 Function‑Level Documentation

**`build_hazard(storm_id, ibtracs_path, corridor_deg=1.5, grid_res_deg=0.05)`**

Builds a CLIMADA `TropCyclone` hazard object from a single IBTrACS storm.

Steps:

1. Load IBTrACS track
2. Build corridor bounding box
3. Construct centroid grid
4. Run CLIMADA windfield model
5. Clean negative intensities
6. Convert matrices to CSR
7. Validate hazard (`haz.check()`)

**Returns:**  

A CLIMADA TropCyclone hazard object.

**`compute_district_hazard_stats(haz, districts)`**

Computes district‑level hazard statistics:

- max wind speed
- mean wind speed
- number of centroids per district

Uses a spatial join (`within`) between centroids and district polygons.

**Returns:**  

A DataFrame with:

- `District`
- `WindSpeed_Max_mps`
- `WindSpeed_Mean_mps`
- `Centroid_Count`

---

## 🧩 How It Fits Into the CCART Pipeline

Historical workflow:

```python
haz = build_hazard(storm_id, ibtracs_path)
stats = compute_district_hazard_stats(haz, districts)
```

Outputs can be used for:

- validation
- historical impact modelling
- comparison with synthetic events

---

## ⚠️ Notes

IBTrACS file must contain the requested storm ID

- Districts must be in EPSG:4326
- Hazard intensity matrix is assumed to be shape (1, N)
- No country‑specific logic is used

---

## 🎯 Summary
This module provides a clean, reproducible workflow for reconstructing historical cyclone hazards using IBTrACS and CLIMADA. It is the historical counterpart to CCART’s synthetic cyclone pipeline.
