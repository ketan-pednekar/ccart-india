# CCART Synthetic Calibration Module

***DLNA scaling, coastal calibration, inland zeroing, and calibrated loss assembly***

The `synthetic_calibration.py` module provides all calibration‑related steps required to convert raw district‑level losses into calibrated synthetic losses consistent with a DLNA‑style total. It handles:

- computing the DLNA synthetic total
- splitting coastal vs inland districts
- calibrating coastal districts to match the DLNA total
- zeroing inland districts
- merging calibrated and inland losses into a unified table

This module forms the **calibration engine** of the synthetic pipeline.

---

## 🌍 Purpose

Synthetic cyclone modelling requires:

- **DLNA‑style total loss** for the event
- **coastal calibration** to match this total
- **inland zeroing** to ensure realistic spatial distribution
- **a unified calibrated loss table** for HWE and mapping

This module centralizes all calibration‑related logic, keeping the synthetic driver clean and modular.

---

## 📁 Module Contents

| Function                     | Purpose                                                |
|-----------------------------|--------------------------------------------------------|
| `compute_dlna_total`        | Computes DLNA synthetic total using power-law scaling  |
| `split_coastal_inland`      | Splits districts into coastal vs inland using mask     |
| `calibrate_coastal_losses`  | Calibrates coastal losses to match DLNA total          |
| `zero_inland_losses`        | Sets inland calibrated losses to zero                  |
| `combine_calibrated_losses` | Merges coastal and inland calibrated losses            |

---

## 🔧 Function‑Level Documentation

### `compute_dlna_total(raw_district_total, alpha, b)`

Computes the DLNA synthetic total using the power‑law relationship:

`DLNA_total = 𝛼 ⋅ (raw_total)^𝑏`

Inputs:

- `raw_district_total` — sum of raw district losses
- `alpha` — DLNA scaling parameter
- `b` — DLNA exponent

**Returns:**  

A single float representing the DLNA synthetic total.

### `split_coastal_inland(district_loss_raw, hazard_stats)`

Splits districts into:

- **coastal** — where hazard_mask = True
- **inland** — where hazard_mask = False

This ensures that calibration is applied only to coastal districts.

**Returns:**  

`coastal_df`, `inland_df`

### `calibrate_coastal_losses(coastal_df, dlna_total)`

Calibrates coastal district losses so that their sum matches the DLNA synthetic total.

Steps:

1. Rename raw loss column
2. Apply CCART’s `calibrate_to_total`
3. Rename calibrated column to `loss_usd_cal`

**Returns:**  

A DataFrame of calibrated coastal losses.

### `zero_inland_losses(inland_df)`

Sets inland calibrated losses to zero.

Adds:

- `loss_usd_cal = 0`
- `calibration_factor = 0`

Raw losses remain unchanged for diagnostics.

**Returns:**  

A DataFrame of inland districts with zero calibrated loss.

### `combine_calibrated_losses(coastal_cal, inland_cal)`

Concatenates coastal and inland calibrated losses into a single table.

**Returns:**  

A unified DataFrame of calibrated district losses.

---

## 🧩 How This Module Fits Into the Synthetic Pipeline

This module is used immediately after raw district losses are computed:

```python
raw_total = district_loss_raw["loss_usd"].sum()
dlna_total = compute_dlna_total(raw_total, alpha, b)

coastal_df, inland_df = split_coastal_inland(district_loss_raw, hazard_stats)

coastal_cal = calibrate_coastal_losses(coastal_df, dlna_total)
inland_cal = zero_inland_losses(inland_df)

district_loss_cal = combine_calibrated_losses(coastal_cal, inland_cal)
```
It prepares all calibrated inputs for:

- HWE
- mapping
- metadata assembly

This keeps the synthetic driver focused on orchestration rather than calibration logic.

---

## ⚠️ Notes & Caveats

- Calibration applies only to coastal districts; inland districts are always zeroed.
- DLNA parameters (`alpha`, `b`) must be chosen consistently across scenarios.
- Calibration uses CCART’s `calibrate_to_total`, ensuring reproducibility.
- This module does not compute HWE — that is handled in `synthetic_hwe.py`.

---

## 📌 Additional Note on DLNA Parameters

The DLNA parameters `alpha` and `b` are derived from the limited historical loss data currently available.
They should be treated as provisional and must be re‑estimated as additional high‑quality impact datasets become available in the future.
Calibration results will improve as the empirical basis expands.

---

## 🎯 Summary

`synthetic_calibration.py` provides all calibration‑related steps for synthetic cyclone impact modelling:

- DLNA total computation
- coastal calibration
- inland zeroing
- unified calibrated loss table

It is the third major building block in the modular synthetic pipeline.