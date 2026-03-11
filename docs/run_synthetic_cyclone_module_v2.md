# CCART — Synthetic Cyclone End‑to‑End Driver (v2)
### Script: `run_synthetic_cyclone_v2.py`
**Module:** CCART–Cyclones (Synthetic Hazard Engine)  
**Purpose:** Execute the full synthetic cyclone pipeline — from synthetic track generation to hazard, exposure, vulnerability, impact, calibration, HWE, and final district/state outputs.

---

## 🌪️ Overview

`run_synthetic_cyclone_v2.py` is the **complete end‑to‑end synthetic cyclone impact model** in CCART.  
It integrates every subsystem:

- synthetic cyclone generator  
- synthetic hazard engine (v2)  
- exposure (LitPop)  
- vulnerability curves  
- raw impact modelling  
- district aggregation  
- DLNA scaling  
- calibration (coastal‑only)  
- HWE (Hazard‑Weighted Exposure)  
- district + state mapping  
- metadata export  

This script is the **scientific backbone** of CCART’s synthetic cyclone workflow.  
It transforms a synthetic storm into a fully calibrated, spatially resolved impact dataset.

---

## 🧩 Pipeline Summary

The end‑to‑end pipeline follows this sequence:

1. **Synthetic track generation**  
2. **TCTracks conversion**  
3. **Synthetic hazard (v2)**  
4. **Exposure loading (LitPop)**  
5. **Exposure–hazard clipping**  
6. **District hazard statistics**  
7. **Inland masking + hazard_mask**  
8. **Vulnerability curves**  
9. **Raw impact**  
10. **District aggregation**  
11. **DLNA scaling**  
12. **Calibration (coastal only)**  
13. **HWE weights**  
14. **District + state outputs**  
15. **Maps + metadata**  

This is the **complete CCART cyclone impact model**, fully automated.

---

## 🧠 Key Components

### **1. Synthetic Track Generation**
Uses `build_synthetic_cyclone()` with:

- clustering  
- PCA refinement  
- perturbation physics  
- scenario‑aware intensity logic  

Regenerates until the storm is sufficiently damaging:

- peak wind ≥ 45 kn  
- peak hazard intensity ≥ 30 m/s  

---

### **2. Synthetic Hazard (v2)**
Built using:

```python
build_hazard_from_tc_tracks(tc_tracks)
```
includes:
- intensity grid
- centroids
- event metadata

### **3. Exposure (LitPop)**
Loads national LitPop exposure and clips it to the synthetic hazard’s bounding box.  
This ensures that only assets within the storm’s spatial footprint are included in the impact calculation.

---

### **4. District Hazard Stats**
Computes district‑level hazard metrics, including:

- **maximum wind speed per district**  
- **distance to coastline** (in km)  
- **inland flag** based on distance threshold  
- **hazard_mask** defined as:  
  

\[
  \text{hazard\_mask} = (\text{wind} \ge \text{threshold}) \land \text{coastal} \land (\text{distance} \le \text{inland\_clip})
  \]



This mask is used for calibration and HWE.

---

### **5. Vulnerability**
Loads CCART’s tropical‑cyclone vulnerability curves, which map hazard intensity to expected fractional asset loss.

---

### **6. Raw Impact**
Computes point‑level losses using exposure × vulnerability × hazard intensity.  
Aggregates these losses to districts to produce **raw district‑level loss**.

---

### **7. DLNA Scaling**
Applies CCART’s synthetic DLNA scaling function:



\[
DLNA = \alpha \cdot (Loss_{raw})^b
\]



This produces a **synthetic total loss target** used for calibration.

---

### **8. Calibration**
Calibration is applied **only to coastal districts** (where `hazard_mask = True`).  
Inland districts are assigned:

- raw loss preserved  
- calibrated loss = 0  

This ensures realistic coastal concentration of calibrated impacts.

---

### **9. HWE (Hazard‑Weighted Exposure)**
Computes **Hazard‑Weighted Exposure (HWE)** weights per district based on:

- hazard severity  
- exposure distribution  
- inland masking  

Weights are normalized and used to allocate the DLNA total into an alternative loss distribution.

---

### **10. District + State Outputs**
Produces all final outputs required for analysis and visualization:

- **district‑level GPKG** with calibrated + HWE losses  
- **district‑level maps** (per affected state)  
- **state‑level maps** (district‑shaded)  
- **metadata.json** containing full synthetic storm diagnostics  

These outputs form the final deliverables of the synthetic cyclone pipeline.

---

## 🧠 Function Signatures

### **Main Driver**
```python
def main(
    run_dir_override=None,
    save_hazard=False,
    save_track=False,
    save_hazard_gpkg=False,
    save_track_csv=False
)
```
### Single‑Run Wrapper
```python
def run_single_synthetic(
    run_dir,
    save_hazard=False,
    save_track=False,
    save_hazard_gpkg=False,
    save_track_csv=False
)
```
Runs one complete synthetic cyclone simulation, saves outputs inside `run_dir`, and returns a summary dictionary (also written to `metadata.json`).

## 📥 Inputs

| Parameter           | Type | Description                          |
|--------------------|------|--------------------------------------|
| `run_dir_override` | str  | Output directory for batch mode.     |
| `save_hazard`      | bool | Save hazard HDF5.                    |
| `save_track`       | bool | Save track JSON.                     |
| `save_hazard_gpkg` | bool | Save hazard as GPKG.                 |
| `save_track_csv`   | bool | Save track CSV.                      |

---

## 📤 Outputs

Directory Structure
```
run_dir/
    impact.gpkg
    metadata.json
    track.csv (optional)
    hazard.gpkg (optional)
    maps/
        district/
        state/
```
---

## 📤 Returned Objects

### **`main()` returns**
- **`merged`** — district‑level GeoDataFrame containing:
  - calibrated losses  
  - HWE losses  
  - geometry  
  - district + state labels  
- **`state_loss`** — state‑level aggregated loss table  
- **`metadata`** — full synthetic storm metadata, including:
  - track perturbation parameters  
  - intensity modifiers  
  - scenario multipliers  
  - RMW, translation speed, rainfall scales  
  - DLNA totals  
  - district/state loss counts  

---

### **`run_single_synthetic()` returns**
- A **summary dictionary** containing key storm‑level metrics  
- This dictionary is also written to: `run_dir/metadata.json`

---

## 🔄 Processing Flow

1. **Load paths**  
   Initialize base directories, data sources, and output folders.

2. **Generate synthetic track**  
   Build a synthetic cyclone using clustering, perturbation physics, and scenario‑aware intensity logic.  
   Regenerate until the storm meets minimum intensity thresholds.

3. **Build synthetic hazard**  
   Convert the synthetic track into a TCTracks object and generate a full hazard intensity field (v2).

4. **Load districts**  
   Read district boundaries, normalize names, and ensure CRS consistency.

5. **Compute inland distance**  
   Measure centroid distance to coastline and classify inland vs coastal districts.

6. **Load exposure**  
   Load LitPop exposure for India and attach district labels.

7. **Clip exposure to hazard**  
   Restrict exposure points to the hazard bounding box for computational efficiency.

8. **Compute district hazard stats**  
   Calculate max wind per district and merge inland distance.  
   Build `hazard_mask` for calibration and HWE.

9. **Build vulnerability curves**  
   Load CCART’s tropical‑cyclone vulnerability functions.

10. **Compute raw impact**  
    Compute point‑level losses and aggregate to districts.

11. **Aggregate to districts**  
    Produce district‑level raw loss totals.

12. **Compute DLNA target**  
    Apply CCART’s synthetic DLNA scaling function to estimate total economic loss.

13. **Calibrate coastal districts**  
    Scale coastal district losses to match DLNA total.  
    Inland districts receive calibrated loss = 0.

14. **Build HWE weights**  
    Compute hazard‑weighted exposure and normalize weights.

15. **Merge district‑level outputs**  
    Combine geometry, calibrated loss, HWE loss, and labels into a final GeoDataFrame.

16. **Aggregate to states**  
    Summarize calibrated and HWE losses at the state level.
```
17. **Save GPKG**  
    Write district
```
18. **Build state loss table**  
    Join state‑level losses back to district geometries.

19. **Generate district + state maps**  
    Produce choropleths for all affected states.

20. **Write metadata.json**  
    Save full storm‑level metadata for batch harness.

---
