# CCART Hazard Simulation Module v2  
### Function: `build_hazard_from_tc_tracks()`  
**Version:** 2.2  
**Module:** CCART–Cyclones (Hazard Engine v2)  
**Purpose:** Construct a CLIMADA `TropCyclone` hazard object from a *single* TC track, with deterministic preprocessing, physically meaningful fallbacks, and clean centroid generation.

---

## 🌪️ Overview

`build_hazard_from_tc_tracks()` converts a **single tropical cyclone track** (`TCTracks` object) into a **gridded wind‑intensity hazard field** suitable for CCART’s impact engine.

The function includes:

- strict single‑storm enforcement  
- deterministic bounding boxes  
- physically meaningful fallbacks  
- clean centroid generation  
- intensity cleaning  
- CLIMADA validation  

This is the core hazard‑builder for CCART v2 and is fully automation‑ready.

---

## ✅ Key Features

### **1. Strict single‑storm requirement**
Ensures the function is used only for one storm at a time:
- avoids multi‑storm ambiguity  
- simplifies automation  
- guarantees deterministic bounding boxes  

### **2. Full 1‑D variable sanitization**
All key track variables are reshaped to `("time",)`:
- `lat`, `lon`  
- `radius_max_wind`  
- `radius_oci`  
- `central_pressure`, `environmental_pressure`  
- `time_step`  
- `max_sustained_wind`  

Prevents shape mismatches inside CLIMADA.

### **3. Physically meaningful fallbacks**
- **RMW fallback:** if all values are zero → set to 30 km  
- **OCI fallback:** enforce range 50–300 km  
- **Pressure delta:** ensure minimum Δp = 1 hPa  

These avoid CLIMADA crashes and unrealistic wind fields.

### **4. Weak‑storm handling**
If peak wind < `min_peak_wind_kn`:
- build a corridor‑based grid  
- generate a zero‑intensity hazard  
- return early  

Prevents noise storms from polluting impact calculations.

### **5. Deterministic centroid grid**
For normal storms:
- bounding box = track extent ± 1°  
- grid resolution = `grid_res_deg`  
- centroids built via `np.meshgrid`  

Ensures reproducibility and automation compatibility.

### **6. Clean intensity matrix**
- convert to dense  
- clip negatives to zero  
- convert back to CSR sparse  

Ensures hazard intensity is physically valid.

### **7. Full CLIMADA validation**
`haz.check()` is called before returning.

---

## 🧠 Function Signature

```python
def build_hazard_from_tc_tracks(
    tc_tracks,
    corridor_deg: float = 1.5,
    grid_res_deg: float = 0.02,
    min_peak_wind_kn: float = 25.0,
    verbose: bool = True,
)
```
## 📥 Inputs

| Parameter          | Type       | Description |
|-------------------|------------|-------------|
| `tc_tracks`       | TCTracks   | Must contain exactly one storm. Required. |
| `corridor_deg`    | float      | Corridor width (degrees) for weak‑storm bounding box. Default: 1.5°. |
| `grid_res_deg`    | float      | Grid resolution for centroid generation. Default: 0.02°. |
| `min_peak_wind_kn`| float      | Storms with peak wind below this threshold are treated as weak and produce zero‑intensity hazards. Default: 25 kn. |
| `verbose`         | bool       | If True, prints diagnostics and debug information. |

---

## 📤 Outputs

### Returns  
A fully validated **TropCyclone hazard object** with:

- **centroids** — deterministic lat/lon grid  
- **intensity** — CSR sparse matrix of wind intensities  
- **intensity_thres** — same as intensity (CLIMADA requirement)  
- **fraction** — CSR sparse matrix (zeros for deterministic runs)  
- **metadata** — storm SID, name, and track attributes preserved  

Suitable for:

- CCART impact engine  
- calibration workflows  
- real‑time automation  
- historical event reconstruction  

---

## 🔄 Processing Flow

### **1. Validate track count**
Ensures `tc_tracks` contains exactly one storm.  
Raises `ValueError` otherwise.

### **2. Sanitize all track variables**
Reshapes key variables to 1‑D arrays (`("time",)`):

- lat, lon  
- radius_max_wind  
- radius_oci  
- central_pressure, environmental_pressure  
- time_step  
- max_sustained_wind  

Prevents CLIMADA dimension errors.

### **3. Apply physical fallbacks**
- RMW fallback (all zeros → 30 km)  
- OCI fallback (clip to 50–300 km)  
- Pressure delta fallback (Δp ≥ 1 hPa)  

Ensures physically meaningful wind fields.

### **4. Compute peak wind**
Used to determine weak‑storm vs normal‑storm branch.

### **5. Weak‑storm branch**
If `peak_wind < min_peak_wind_kn`:

- build corridor‑based bounding box  
- generate centroids  
- create zero‑intensity hazard  
- return early  

### **6. Normal‑storm branch**
- bounding box = track extent ± 1°  
- generate centroid grid  
- run `TropCyclone.from_tracks()`  
- clean negative intensities  
- convert back to CSR sparse  

### **7. Validate hazard**
Runs `haz.check()` to ensure CLIMADA compatibility.

### **8. Return hazard**
A clean, deterministic, automation‑ready hazard object.

---

## 🧪 Debug Outputs (when `verbose=True`)

### Track diagnostics
- storm SID  
- storm name  
- peak sustained wind  

### Variable shapes
For:

- radius_max_wind  
- radius_oci  
- central_pressure  
- environmental_pressure  
- max_sustained_wind  

### Centroid grid diagnostics
- lat range and count  
- lon range and count  
- total centroids  

### Hazard spacing
- mean lat spacing  
- mean lon spacing  

Useful for verifying grid resolution and track quality.

---

## ⚙️ Notes for Automation (CCART v3‑ready)

This function is **fully automation‑ready** because:

### **1. No GUI dependencies**
Pure Python — no QGIS, no manual clipping.

### **2. Deterministic behaviour**
- fixed bounding box logic  
- fixed grid resolution  
- fixed fallbacks  
- reproducible outputs  

Ideal for scheduled or real‑time pipelines.

### **3. CLIMADA‑native output**
Integrates directly with:

- CCART exposure module  
- CCART vulnerability module  
- CCART impact engine  

### **4. Safe for real‑time ingestion**
Handles:

- missing RMW  
- missing OCI  
- unrealistic pressure deltas  
- weak storms  
- negative intensities  

Prevents pipeline crashes.

### **5. Lightweight and fast**
Suitable for:

- cloud functions  
- cron jobs  
- API‑triggered workflows  
- real‑time cyclone updates  

---

## 🏁 Summary

`build_hazard_from_tc_tracks()` is the backbone of CCART’s cyclone hazard engine.  
It transforms raw TC tracks into clean, reproducible, physically meaningful hazard fields — ideal for both historical analysis and real‑time automated impact prediction.
