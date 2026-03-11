# CCART Synthetic Cyclone Generator Module  
This module implements CCART’s synthetic cyclone engine — a hybrid statistical–physical generator that produces realistic, India‑relevant tropical cyclones for hazard simulation, ensemble modelling, and climate‑scenario analysis.  

It combines clustering, PCA refinement, geospatial filtering, and controlled perturbation physics to create storms that are both statistically grounded and physically plausible.

---
### Function: `build_synthetic_cyclone()`  
**Module:** CCART–Cyclones (Synthetic Hazard Engine)  
**Purpose:** Generate realistic, landfalling, India‑relevant synthetic tropical cyclones using clustering, PCA refinement, perturbation physics, and scenario‑aware intensity logic.

## 🌪️ Overview

`build_synthetic_cyclone()` creates a **single synthetic tropical cyclone track** by learning from historical storms and applying controlled, physically meaningful perturbations.

This generator is the core innovation of CCART — enabling:

- large synthetic ensembles  
- scenario‑based hazard exploration  
- climate‑conditioned cyclone behaviour  
- reproducible stochastic modelling  
- realistic landfalling storms for India  

The generator blends **machine learning**, **geospatial filtering**, and **physical perturbations** to produce storms that are both statistically grounded and physically plausible.

## 🧩 Key Components

### **1. Historical Track Loading**
Loads cleaned NI basin tracks from HDF5 and filters storms with:

- peak wind ≥ `min_wind`  
- track entering the India bounding box  
- confirmed landfall within 20 km of coastline  

This ensures only relevant, impactful storms are used as analogs.

---

### **2. DBSCAN Clustering**
Tracks are resampled to a fixed length and normalized.  
DBSCAN groups storms by **shape similarity**:

- no need to pre‑specify number of clusters  
- robust to noise  
- ideal for cyclone track geometry  

The largest cluster becomes the “analog family”.

---

### **3. PCA Refinement**
Within the target cluster:

- PCA reduces dimensionality  
- cosine similarity identifies central storms  
- selection is **probabilistic**, weighted by centrality  

This avoids over‑using the same analogs and increases diversity.

---

### **4. Genesis Jitter (Ocean‑Only)**
A small random displacement is applied to the genesis point:

- max jitter = 0.3°  
- constrained to ocean using coastline mask  
- preserves physical realism  

Metadata is stored for reproducibility.

---

### **5. Track Perturbation (Gaussian + Spline)**
The track is perturbed using:

- Gaussian noise (scenario‑scaled)  
- spline smoothing  
- curvature index calculation  
- minimum‑spacing enforcement (≥ 5 km)  

This produces smooth, realistic trajectories without CLIMADA crashes.

---

### **6. Translation Speed Variety**
Forward speed is modified by scaling the time‑space relationship:

- preserves track shape  
- adjusts storm progression  
- metadata stored  

---

### **7. Intensity Variety**
Wind intensity is modified using:

- peak multiplier  
- decay multiplier  
- timing shift  
- scenario‑aware scaling  

Ensures realistic intensity evolution while allowing controlled variability.

---

### **8. RMW Variety**
Storm size is modified by scaling the radius of maximum winds:

- multiplicative factor (0.9–1.1)  
- fallback ensures RMW never collapses to zero  

---

### **9. Rainfall Variety**
A simple multiplicative factor introduces rainfall diversity.

---

### **10. Scenario Logic**
Three scenarios modify storm behaviour:

| Scenario   | Peak | Decay | Track Curvature |
|------------|------|--------|-----------------|
| baseline   | 1.0  | 1.0    | 1.0             |
| warm_sst   | 1.05 | 0.95   | 1.1             |
| high_end   | 1.10 | 0.90   | 1.2             |

This allows climate‑conditioned synthetic storms.

---

## 🧠 Function Signature

```python
def build_synthetic_cyclone(
    file_path,
    min_wind=35,
    cluster_eps=12.0,
    cluster_min_samples=2,
    top_n=5,
    wind_boost=1.0,
    scenario="baseline",
)
```
---

# ✅ **Inputs**

## 📥 Inputs

| Parameter            | Type   | Description |
|---------------------|--------|-------------|
| `file_path`         | str    | Path to cleaned historical NI tracks (HDF5). |
| `min_wind`          | float  | Minimum peak wind for analog selection. Default: 35 kn. |
| `cluster_eps`       | float  | DBSCAN epsilon for track‑shape clustering. |
| `cluster_min_samples` | int  | Minimum samples required to form a DBSCAN cluster. |
| `top_n`             | int    | Number of PCA‑refined analogs to sample from. |
| `wind_boost`        | float  | Global multiplier applied to intensity before perturbation. |
| `scenario`          | str    | One of: `baseline`, `warm_sst`, `high_end`. Controls intensity + curvature. |

---

## 📤 Outputs

A single **synthetic cyclone** returned as an `xarray.Dataset` containing:

- **lat(time)** — perturbed, smoothed track  
- **lon(time)** — perturbed, smoothed track  
- **max_sustained_wind(time)** — scenario‑aware intensity  
- **radius_max_wind(time)** — storm size variety applied  
- **radius_oci(time)** — cleaned and validated  
- **central_pressure(time)** — ΔP ≥ 1 hPa enforced  
- **environmental_pressure(time)** — preserved  

### Metadata includes:

- genesis jitter (distance + coordinates)  
- curvature index  
- translation speed scale  
- intensity modifiers (peak, decay, timing shift)  
- scenario multipliers  
- rainfall scale  
- RMW scale  

This metadata ensures full reproducibility and supports calibration workflows.

---

## 🔄 Processing Flow

1. Load historical tracks  
2. Filter for India + landfall  
3. Resample tracks to fixed length  
4. Cluster using DBSCAN  
5. Select largest cluster  
6. PCA refinement of analogs  
7. Weighted analog selection  
8. Apply genesis jitter (ocean‑only)  
9. Track perturbation (Gaussian + spline)  
10. Enforce minimum spacing (≥ 5 km)  
11. Apply translation‑speed variety  
12. Apply intensity variety (peak, decay, shift)  
13. Apply RMW variety  
14. Apply rainfall variety  
15. Enforce physical sanity checks (RMW, OCI, ΔP)  
16. Reshape variables to 1‑D  
17. Return synthetic cyclone  

---

## 🧪 Debug Outputs

When enabled, the generator prints:

- RMW array shape  
- central & environmental pressure shapes  
- jitter distance  
- curvature index  
- scenario multipliers  
- translation speed scale  

These diagnostics help validate:

- track quality  
- perturbation behaviour  
- physical consistency  
- scenario effects  

---

