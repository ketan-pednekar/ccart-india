# CCART v1.0 — Impact Module

The Impact Module computes cyclone losses using CLIMADA’s physical impact
engine. It takes exposure points, vulnerability curves, and the cyclone hazard
footprint, and produces both point-level and district-level loss estimates.

This module forms the core of the CCART loss engine.

---

## 1. Purpose

The Impact Module computes **physical economic losses** using CLIMADA’s
`ImpactCalc`, which combines:

- the cyclone hazard footprint,
- LitPop exposure values, and
- the selected vulnerability curve.

The output is a CLIMADA `Impact` object containing losses at each exposure
point. These point-level losses can then be aggregated to districts.

This is different from the HWE module, which **allocates statewide losses**.
The Impact Module computes **actual CLIMADA losses** directly from hazard,
exposure, and vulnerability.

---

## 2. Why raw CLIMADA district losses can be misleading

When CLIMADA computes point-level losses directly from LitPop exposure, the
loss at each point is:

**Loss = Exposure × DamageFraction(V)**

This creates a known distortion:

- Districts with **very high LitPop exposure** can show **very large losses**,
- even if **wind speeds are low** in that district.

As a result:

- High-exposure districts dominate the loss map
- Low-exposure but high-wind districts are under-represented
- The spatial pattern of losses becomes unrealistic
- District-level totals no longer reflect cyclone physics

This behaviour is expected because LitPop is highly uneven across districts.

---

## 3. Why CCART uses HWE for district allocation

To avoid these distortions, CCART Cyclone v1 uses **HWE (Hazard–Exposure**
**Weighting)** to allocate statewide losses across districts.

HWE ensures that a district receives a large share of the loss **only if**:

- wind speeds are high **and**
- exposure is high

This produces a physically meaningful and stable spatial distribution of
losses.

The Impact Module therefore provides the **statewide physical loss**, while the
HWE Module provides the **district-level allocation**.

---

## 4. Function: `compute_raw_impact()`

Compute raw CLIMADA impact at the exposure-point level.

### **Inputs**
- `assets_state`: GeoDataFrame or `Exposures` object  
- `impf_set`: vulnerability curves (`ImpactFuncSet`)  
- `hazard`: CLIMADA `TropCyclone` hazard object  

### **Workflow**
1. Convert exposure to CLIMADA `Exposures` format  
2. Ensure impact function ID (`impf_ = 1`)  
3. Run `ImpactCalc(exp, impf_set, hazard).impact()`  

### **Output**
- `Impact` object with point-level losses

---

## 5. Function: `attach_losses_to_points()`

Attach raw CLIMADA losses back to the exposure GeoDataFrame.

### **Workflow**
- Extract loss array from `impact_raw`
- Print diagnostics (total loss, max loss, non-zero points)
- Add `loss_usd` column to exposure points

### **Output**
- GeoDataFrame with `loss_usd` for each exposure point

---

## 6. Function: `aggregate_district_loss()`

Aggregate point-level losses to district-level totals.

### **Workflow**
1. Clean join artefact columns  
2. Spatial join exposure points with district polygons  
3. Sum `loss_usd` by district  

### **Output**
A DataFrame with:
- `District`
- `loss_usd`

---

## 7. Notes

- This module computes **physical CLIMADA losses**, not allocated losses.  
- District-level losses depend on the spatial distribution of exposure points.  
- HWE-based allocation is handled separately in the **HWE Module**.
- CCART v1 uses CLIMADA’s default TC vulnerability curve (impf_TC = 1).  
