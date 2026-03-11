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
---

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

A fully validated **TropCyclone hazard object** with:

- **centroids** — deterministic lat/lon grid  
- **intensity** — CSR sparse matrix of wind intensities  
- **intensity_thres** — same as intensity  
- **fraction** — CSR sparse matrix (zeros for deterministic runs)  
- **metadata** — storm SID, name, and track attributes preserved  

### Suitable for:

- CCART impact engine  
- calibration workflows  
- real‑time automation  
- historical event reconstruction  
---

## 🔄 Processing Flow

1. **Validate track count**  
   Ensures `tc_tracks` contains exactly one storm. Raises an error otherwise.

2. **Sanitize all track variables**  
   Reshapes key variables (`lat`, `lon`, `RMW`, `OCI`, pressures, etc.) to 1‑D arrays.

3. **Apply physical fallbacks**  
   - RMW fallback (30 km if all zeros)  
   - OCI fallback (clipped to 50–300 km)  
   - Pressure delta fallback (minimum Δp = 1 hPa)

4. **Compute peak wind**  
   Determines whether the storm is weak or normal.

5. **Weak‑storm branch**  
   - Build corridor‑based grid  
   - Generate zero‑intensity hazard  
   - Return early  

6. **Normal‑storm branch**  
   - Build bounding box (track extent ±1°)  
   - Generate centroid grid  
   - Run CLIMADA wind model  
   - Clean negative intensities  

7. **Validate hazard**  
   Runs `haz.check()` to ensure structural consistency.

8. **Return hazard**  
   Returns a fully validated `TropCyclone` object.
---

## 🧪 Debug Outputs (when `verbose=True`)

When `verbose=True`, the function prints:

- Storm SID  
- Storm name  
- Peak sustained wind  
- Shapes of key track variables  
- Centroid grid dimensions  
- Number of centroids  
- Mean latitude spacing  
- Mean longitude spacing  

These diagnostics help verify:

- track quality  
- grid resolution  
- bounding box correctness  
- CLIMADA wind‑model behaviour  
---

## ⚙️ Notes for Automation (CCART v3‑ready)

This function is fully automation‑ready because:

- It has **no GUI dependencies**  
- Bounding boxes are **deterministic**  
- Grid generation is **deterministic**  
- All fallbacks are **physically meaningful**  
- Output is **CLIMADA‑native**  
- It handles weak storms gracefully  
- It validates itself before returning  

This makes it suitable for:

- real‑time cyclone impact prediction  
- batch simulation pipelines  
- cloud‑based hazard engines  
- automated early‑warning systems  
---

## 🏁 Summary

`build_hazard_from_tc_tracks()` is the backbone of CCART’s cyclone hazard engine.  
It transforms raw TC tracks into clean, reproducible, physically meaningful hazard fields.

It is:

- deterministic  
- modular  
- automation‑ready  
- CLIMADA‑compatible  
- suitable for real‑time and historical modelling  

This function enables CCART to operate as a scalable, multi‑hazard impact platform.

---

## 🧭 Mermaid Flowchart — CCART Hazard Builder v2

```mermaid

flowchart TD

    %% --- Input Validation ---
    A[Start: TCTracks Input] --> B{Exactly One Storm?}
    B -- No --> Z[Error: Must Provide Single Storm]
    B -- Yes --> C["Sanitize Track Variables\nReshape to 1‑D ('time',)"]

    %% --- Physical Fallbacks ---
    C --> D[Apply Physical Fallbacks]
    D --> D1["RMW Fallback\n30 km if all zeros"]
    D --> D2["OCI Fallback\nClip 50–300 km"]
    D --> D3["Pressure Delta Check\nEnsure ≥ 1 hPa"]

    %% --- Peak Wind ---
    D3 --> E[Compute Peak Wind]

    %% --- Branching Logic ---
    E --> F{Peak Wind < Threshold?}

    %% --- Weak Storm Path ---
    F -- Yes --> G["Weak‑Storm Branch\nBuild Corridor Grid"]
    G --> H[Generate Zero‑Intensity Hazard]
    H --> Y[Return Hazard]

    %% --- Normal Storm Path ---
    F -- No --> I["Normal‑Storm Branch\nBounding Box ±1°"]
    I --> J["Generate Centroid Grid\nnp.meshgrid()"]
    J --> K["Run CLIMADA Wind Model\nTropCyclone.from_tracks()"]
    K --> L["Clean Intensities\nClip negatives → 0"]
    L --> M[Convert to CSR Sparse]

    %% --- Final Checks ---
    M --> N[haz.check()]
    N --> Y[Return Hazard]
```

