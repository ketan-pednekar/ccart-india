# CCART Calibration Module

This module provides the functions required to calibrate raw CLIMADA losses to match state‑level DLNA/PDNA totals.
Calibration ensures that synthetic or model‑based district losses are consistent with official post‑disaster assessments.

The design is intentionally simple, transparent, and reproducible — suitable for both synthetic cyclone modelling and future flood/heat modules.

---

## 🌍 Purpose

Raw CLIMADA losses often underestimate or overestimate real‑world impacts.
To align modelled losses with observed totals, CCART applies a single calibration factor:

```python
k = DLNA_total / raw_total
```

District‑level calibrated losses are then:

```python
loss_calibrated_i = loss_raw_i * k
```
This preserves the spatial pattern of losses while matching the official total.

---

## 🔧 Functions

`calibrate_to_total(district_loss, dlna_total, loss_col="loss_usd")`

Scales district‑level raw losses to match a given DLNA/PDNA total.

**Parameters for `calibrate_to_total`**

| Parameter      | Type        | Description                                                                 |
|----------------|-------------|-----------------------------------------------------------------------------|
| district_loss  | DataFrame   | Must contain `District` and a raw loss column specified by `loss_col`.      |
| dlna_total     | float       | State‑level DLNA/PDNA total loss (USD) used as the calibration target.      |
| loss_col       | str         | Column name for raw losses (default: `"loss_usd"`).                         |

**Returns**

A DataFrame with:

- `District`
- `loss_usd_raw`
- `loss_usd_calibrated`
- `calibration_factor`

**Raises**

`ValueError` if raw total loss is zero or negative.

---

## 📘 Usage Example

```python
from ccart.calibration.calibration import calibrate_to_total

df_cal = calibrate_to_total(
    district_loss=df_raw,
    dlna_total=1.2e9,   # DLNA total in USD
    loss_col="loss_usd"
)
```
---

## 🧱 Dependencies

`pandas`

## 🎯 Summary

The CCART calibration module:

- provides a **transparent, reproducible** method for aligning modelled losses with DLNA/PDNA totals
- preserves **relative spatial patterns** while matching official totals
- is **hazard‑agnostic** and will be reused for flood, heat, and multi‑hazard modules
- integrates seamlessly with CCART’s synthetic cyclone pipeline