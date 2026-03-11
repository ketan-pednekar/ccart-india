# CCART v1.0 — HWE Module (Hazard–Exposure Weighting)

The HWE module provides a simple, transparent method for allocating cyclone
impact across districts using a combined hazard–exposure weight. It acts as the
bridge between hazard modelling and impact computation.

---

## 1. Purpose

In CCART Cyclone v1, CLIMADA computes the total economic loss for the entire
state using the cyclone hazard footprint, LitPop exposure, and the default
vulnerability curve. The HWE module does not compute losses itself. Instead, it
allocates this statewide loss across districts using a combined hazard–
exposure weight.

Districts with higher wind speeds (hazard) and higher exposure (LitPop value)
receive a larger share of the statewide loss. This ensures that the spatial
distribution of impact reflects both physical intensity and asset concentration.


Cyclone impact depends on both:
- **hazard intensity** (wind speed), and  
- **exposure** (LitPop asset value)

The HWE module constructs a district-level weight:



\[
w_i = H_i^\alpha \cdot E_i^\beta
\]



where:
- \(H_i\) = hazard intensity (e.g., max wind speed)
- \(E_i\) = exposure value
- \(\alpha, \beta\) = tuning parameters (default 1.0)

Weights are normalized to sum to 1.

HWE therefore acts as the spatial allocation layer: it converts a single
statewide impact value into district-level impact estimates based on the
relative strength of hazard and exposure in each district.

---

## 2. Function: `build_hwe_weights()`

### **Inputs**
- `hazard_stats`: district-level hazard metrics  
- `exp_dist`: district-level exposure totals  
- `alpha`, `beta`: exponents controlling hazard/exposure influence  
- `wind_col`: hazard column (default: `WindSpeed_Max_mps`)  
- `exp_col`: exposure column (default: `Exposure_Value`)  

### **Workflow**
1. Merge hazard and exposure by district  
2. Extract hazard and exposure terms  
3. Compute raw HWE weights  
4. Aggregate to district level  
5. Normalize weights to sum to 1  

### **Outputs**
A DataFrame with:
- `District`
- `H_i` (hazard term)
- `E_i` (exposure term)
- `HWE_weight` (raw weight)
- `HWE_weight_norm` (normalized weight)

---

## 3. Interpretation

- Districts with **higher wind speeds** get higher weights  
- Districts with **higher exposure** get higher weights  
- `alpha` and `beta` allow tuning:
  - `alpha > 1`: emphasize hazard  
  - `beta > 1`: emphasize exposure  
  - `alpha = beta = 1`: balanced weighting (default)

The normalized weights can be used to allocate:
- total economic loss  
- total affected population  
- relief resources  
- district-level impact estimates  

---

## 4. Notes

- HWE does **not** compute losses — it only allocates them.  
- Impact computation is handled in the **Impact Module**.  
- Vulnerability curves are defined in the **Vulnerability Module**.  
