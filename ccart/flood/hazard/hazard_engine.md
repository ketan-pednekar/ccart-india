# CCART-Floods — Hazard Engine (`hazard_engine.py`)

## Purpose
`hazard_engine.py` implements the core scientific logic of the CCART-Floods
framework. It computes **climate‑conditioned flood hazard** by combining:

- **FSI** — static terrain-driven flood susceptibility  
- **Rx2day** — annual maximum 2‑day rainfall  
- **P95** — 95th percentile of historical Rx2day (1995–2024 baseline)

The hazard formulation is:



\[
H = \text{FSI} \times \max\left(\frac{\text{Rx2day}}{\text{P95}}, 0\right)
\]



This module provides:
- a clean hazard computation function  
- a historical hazard loop (CHIRPS)  
- a future hazard loop (CMIP6 → CHIRPS reprojection)  
- memory‑safe, year‑by‑year processing  

---

## What This Module Does

### **1. Computes hazard for a single year**
`compute_hazard()`:
- takes Rx2day, P95, and FSI (all CHIRPS‑aligned)  
- computes relative rainfall intensity  
- multiplies by FSI  
- masks invalid regions  
- returns a clean 2D hazard array  

This is the core scientific function of the flood module.

---

### **2. Computes historical hazard (1995–2024)**
`compute_historical_hazard()`:
- loads each saved CHIRPS Rx2day `.npy` file  
- computes hazard for that year  
- saves `hazard_hist_YYYY.npy`  
- frees memory before moving to the next year  

This loop is **resume‑friendly** and **memory‑safe**.

---

### **3. Computes future hazard (2027–2100)**
`compute_future_hazard()`:
- loads each CMIP6 daily rainfall `.nc` file  
- computes Rx2day via xarray rolling window  
- reprojects CMIP6 (0.25°) → CHIRPS grid (0.05°)  
- computes hazard  
- saves `hazard_fut_YYYY.npy`  

This loop is also **resume‑friendly** and **memory‑safe**.

---

## Functions in This Module

### **`compute_hazard(rx2day_grid, p95_grid, fsi_on_chirps)`**
Computes hazard using the CCART formulation.

Returns a 2D float32 array.

---

### **`compute_historical_hazard(rx2day_dir, p95_grid, fsi_on_chirps, out_dir)`**
Processes historical CHIRPS years one at a time.

Saves one `.npy` per year.

---

### **`compute_future_hazard(cmip_dir, p95_grid, fsi_on_chirps, chirps_shape, chirps_transform, out_dir, start_year, end_year)`**
Processes CMIP6 future years one at a time.

Steps:
1. Compute Rx2day via rolling window  
2. Reproject to CHIRPS grid  
3. Compute hazard  
4. Save `.npy`  

---

## Usage Example

```python
from pathlib import Path
from ccart_floods.hazard.hazard_engine import (
    compute_hazard,
    compute_historical_hazard,
    compute_future_hazard
)

# Inputs
rx2day_dir = Path("outputs/rx2day_annual")
p95_grid   = np.load("outputs/p95_rx2day_1995_2024.npy")
fsi        = np.load("outputs/fsi_on_chirps.npy")

# Historical hazard
compute_historical_hazard(
    rx2day_dir=rx2day_dir,
    p95_grid=p95_grid,
    fsi_on_chirps=fsi,
    out_dir=Path("outputs/hazard_hist")
)
```
---

## Notes

- Hazard is computed **pixel‑wise** and is fully CHIRPS‑aligned.
- All loops are **memory‑safe** and process one year at a time.
- CMIP6 rainfall is reprojected to CHIRPS using bilinear resampling.
- This module does not ingest FSI or CHIRPS — those are handled by their own subsystems.
- This module does not render frames or animations — those are intentionally excluded from CCART‑Floods.