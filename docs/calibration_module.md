# CCART v1.0 — Calibration Module

The Calibration Module scales CCART’s modeled losses to match official
DLNA/PDNA state-level totals. This ensures that CCART’s results remain
physically consistent (from CLIMADA) while also aligning with government-
validated impact assessments.

Calibration is applied **after** district-level losses have been computed
(either from raw CLIMADA or from HWE allocation).

---

## 1. Purpose

Raw CLIMADA losses rarely match official DLNA/PDNA totals because:

- LitPop is a proxy for real asset values  
- vulnerability curves are global, not India-specific  
- CLIMADA does not include indirect or infrastructure losses  
- hazard footprints may not capture local fragility  

Calibration provides a transparent way to reconcile these differences.

The calibration factor is:

**k = DLNA_total / raw_total**

District-level calibrated losses are:

**loss_calibrated_i = loss_raw_i × k**

This preserves the **relative spatial pattern** from CLIMADA or HWE while
ensuring the **statewide total** matches the official number.

---

## 2. Function: `calibrate_to_total()`

Scale district-level raw losses to match a given DLNA/PDNA total.

### **Inputs**
- `district_loss`: DataFrame with district-level raw losses  
- `dlna_total`: official state-level DLNA/PDNA loss (USD)  
- `loss_col`: column containing raw losses (default: `loss_usd`)  

### **Workflow**
1. Compute raw statewide total  
2. Compute calibration factor `k = dlna_total / raw_total`  
3. Multiply each district’s loss by `k`  
4. Return calibrated losses with transparency  

### **Output**
A DataFrame with:
- `District`  
- `loss_usd_raw`  
- `loss_usd_calibrated`  
- `calibration_factor`  

---

## 3. Notes

- Calibration preserves **spatial patterns** but adjusts **totals**.  
- Calibration is optional but recommended when DLNA/PDNA data exists.  
- Calibration should be applied **after** HWE allocation (if used).  
- CCART v1 uses a **single linear factor** for transparency and reproducibility.  
