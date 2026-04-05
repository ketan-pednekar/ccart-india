# CCART Synthetic HWE Module

***Hazard–Wealth–Exposure (HWE) computation and calibrated loss integration***

The `synthetic_hwe.py` module takes calibrated district‑level losses and combines them with district‑level wealth or exposure metrics to compute HWE‑style indicators. It is the final analytical step in the synthetic pipeline before mapping and reporting.

It handles:

- aligning calibrated losses with district wealth/exposure
- computing HWE metrics (e.g., loss as a share of wealth)
- preparing a clean table for mapping and analysis
- attaching HWE metrics back to district geometries

This module forms the **distributional impact layer** of the synthetic pipeline.

---

## 🌍 Purpose

Synthetic cyclone modelling requires not just absolute losses, but **contextualised losses**:

- losses relative to **wealth**
- losses relative to **exposure**
- indicators that allow comparison across districts and events

This module centralizes these computations so that the synthetic driver remains clean and orchestration‑focused.

---

## 📁 Module Contents

| Function                        | Purpose                                                     |
|---------------------------------|-------------------------------------------------------------|
| `prepare_hwe_inputs`            | Aligns calibrated losses with district wealth/exposure      |
| `compute_hwe_metrics`           | Computes HWE-style indicators (e.g., loss/wealth)           |
| `attach_hwe_to_districts`       | Merges HWE metrics back to district geometries              |

---

## 🔧 Function‑Level Documentation

### `prepare_hwe_inputs(district_loss_cal, wealth_df)`

Aligns calibrated district‑level losses with district‑level wealth or exposure data.

Inputs:

- `district_loss_cal` — must contain `District` and `loss_usd_cal`
- `wealth_df` — must contain `District` and `wealth_usd`

Performs:

- key alignment on `District`
- one‑to‑one validation for safety

**Returns:**  
A merged DataFrame with calibrated losses and wealth/exposure.

---

### `compute_hwe_metrics(hwe_df, loss_col="loss_usd_cal", wealth_col="wealth_usd")`

Computes HWE‑style indicators such as:

- `loss_share = loss_usd_cal / wealth_usd`

Division‑by‑zero is safely handled by replacing zero wealth with `NA`.

**Returns:**  
A DataFrame with additional HWE metrics.

---

### `attach_hwe_to_districts(hwe_df, districts_gdf)`

Merges HWE metrics back onto district geometries for mapping and spatial analysis.

Inputs:

- `hwe_df` — DataFrame with HWE metrics by `District`
- `districts_gdf` — GeoDataFrame with district geometries

**Returns:**  
A GeoDataFrame ready for:

- choropleth mapping  
- spatial statistics  
- export to GeoPackage/GeoJSON  

---

## 🧩 How This Module Fits Into the Synthetic Pipeline

```python
hwe_input = prepare_hwe_inputs(district_loss_cal, wealth_df)
hwe_metrics = compute_hwe_metrics(hwe_input)
districts_hwe = attach_hwe_to_districts(hwe_metrics, districts)
```

It prepares all distributional impact outputs for:

- HWE analysis
- equity‑focused mapping
- reporting and communication

---

## ⚠️ Notes & Caveats

- HWE metrics are only as good as the underlying wealth/exposure data; data gaps should be documented.
- Wealth/exposure definitions must be consistent across events and scenarios.
- Extreme ratios (e.g., very small wealth denominators) may need capping or filtering.

This module does **not** perform calibration — that is handled in `synthetic_calibration.py`.

## 🎯 Summary

`synthetic_hwe.py` provides the final analytical layer in the synthetic cyclone pipeline:

- aligns calibrated losses with wealth/exposure
- computes HWE‑style indicators
- attaches metrics to district geometries

It turns calibrated losses into interpretable, distributional risk metrics that can be mapped, compared, and cited.