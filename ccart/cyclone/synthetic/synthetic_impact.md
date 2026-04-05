# CCART Synthetic Impact Module

***District hazard statistics, raw impact computation, and district‑level aggregation***

The `synthetic_impact.py` module provides all computational steps required to translate a synthetic cyclone hazard field into district‑level raw losses. It handles:

- computing district‑level hazard statistics (max and mean intensity)
- merging inland distance and inland mask
- computing raw impact using exposure × vulnerability × hazard
- attaching losses to exposure points
- aggregating losses to districts

This module forms the core impact engine of the synthetic pipeline.

---

## 🌍 Purpose

Synthetic cyclone modelling requires:

- **hazard statistics** at the district level  
- **raw impact** at the exposure level  
- **district‑level** aggregation for calibration and HWE  

This module centralizes all impact‑related computations, keeping the synthetic driver clean and modular.

---

## 📁 Module Contents

| Function                       | Purpose                                                |
|-------------------------------|--------------------------------------------------------|
| `compute_hazard_stats`        | Computes district-level max & mean wind intensity      |
| `merge_inland_mask`           | Merges inland distance and inland flag into stats      |
| `compute_raw_impact_pipeline` | Computes raw impact and attaches losses to exposures   |
| `aggregate_district_losses`   | Aggregates exposure-level losses to district totals    |

---

## 🔧 Function‑Level Documentation

### `compute_hazard_stats(hazard, districts_gdf)`

Computes district‑level hazard statistics using CLIMADA hazard centroids.

Outputs include:

- `max_intensity` — maximum wind speed per district  
- `mean_intensity` — mean wind speed per district  
- centroid‑level spatial join using `intersects` for robustness  

**Returns:**  
A DataFrame of district hazard statistics.

---

### `merge_inland_mask(hazard_stats, districts_gdf)`

Merges inland distance and inland mask into the hazard statistics table.

Adds:

- `dist_to_coast_km`  
- `is_inland`  

This ensures that downstream calibration and HWE can correctly zero out inland districts.

**Returns:**  
Updated hazard statistics DataFrame.

---

### `compute_raw_impact_pipeline(exposures, impf_set, hazard)`

Computes raw impact using:

- exposure points  
- vulnerability curves  
- hazard intensity  

Steps:

1. Compute raw impact using CLIMADA  
2. Attach losses to exposure points  

**Returns:**  
- `exp_with_loss` — Exposures object with loss column  
- `impact_raw` — CLIMADA Impact object  

---

### `aggregate_district_losses(exp_with_loss, districts_gdf)`

Aggregates exposure‑level losses to district totals.

Outputs include:

- `District`  
- `loss_usd` (raw)  

This is the input for calibration and HWE.

**Returns:**  
A DataFrame of district‑level raw losses.

---

## 🧩 How This Module Fits Into the Synthetic Pipeline

This module is used immediately after exposure clipping and hazard generation:

```python
hazard_stats = compute_hazard_stats(hazard, districts)
hazard_stats = merge_inland_mask(hazard_stats, districts)

exp_with_loss, impact_raw = compute_raw_impact_pipeline(exposure, impf_set, hazard)
district_loss_raw = aggregate_district_losses(exp_with_loss, districts)
```
It prepares all impact‑related inputs for:

- DLNA
- calibration
- HWE
- mapping

This keeps the synthetic driver focused on orchestration rather than computation.

---

## ⚠️ Notes & Caveats

Hazard statistics depend on district geometry quality; ensure districts are cleaned and normalized.

Raw impact uses CLIMADA’s impact functions; vulnerability curves must be pre‑loaded.

This module does **not** perform calibration — that is handled in `synthetic_calibration.py`.

This module does **not** compute HWE — that is handled in `synthetic_hwe.py`.

---

## 🎯 Summary

`synthetic_impact.py` provides the core computational steps for synthetic cyclone impact modelling:

- district hazard statistics
- raw impact
- exposure‑level losses
- district‑level aggregation

It is the second major building block in the modular synthetic pipeline.