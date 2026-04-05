# CCART-Floods — CHIRPS Rainfall Metrics (`compute_metrics.py`)

## Purpose
`compute_metrics.py` computes the rainfall‑based metrics required by the CCART
hazard engine. These metrics quantify short‑duration extreme rainfall behaviour
using CHIRPS daily precipitation data.

This module currently implements:

- **Rx2day** — the maximum 2‑day rainfall total for each year  
- **P95** — the 95th percentile of Rx2day across a baseline period  

Both metrics are computed in a **memory‑safe, year‑by‑year** manner, following
the design of the dynamic hazard pipeline.

---

## Why These Metrics Matter

### **Rx2day (Maximum 2‑day rainfall)**
Floods in India are often triggered by short, intense bursts of rainfall rather
than long wet spells. Rx2day captures the strongest 2‑day rainfall event each
year at every pixel.

It represents the **rainfall shock** used in the hazard formula.

### **P95 (95th percentile of Rx2day)**
By computing Rx2day for many years (e.g., 1995–2024), we can estimate the
95th‑percentile threshold of extreme rainfall.

P95 becomes the **baseline extreme rainfall level** against which future climate
scenarios are compared.

---

## What This Module Does

### **1. Computes Rx2day for a single year**
- Loads daily CHIRPS rasters one at a time  
- Uses a sliding 2‑day window  
- Tracks the maximum 2‑day accumulation  
- Returns a 2D array (rows × cols)  
- Optionally saves the result as `rx2day_{year}.npy`

### **2. Computes Rx2day for a baseline period**
- Loops through all years in the baseline  
- Computes Rx2day year‑by‑year  
- Saves each year’s result  
- Memory usage stays low (only one year in RAM)

### **3. Computes pixel‑wise P95**
- Loads all saved Rx2day arrays  
- Stacks them safely  
- Computes the 95th percentile at each pixel  
- Optionally saves `p95_rx2day.npy`

### **4. Provides a high‑level wrapper**
`compute_baseline_metrics()` runs the entire baseline workflow:
- load CHIRPS metadata  
- compute Rx2day for all baseline years  
- compute P95  

---

## Functions in This Module

### **`compute_rx2day_for_year(year, chirps_meta, rx2day_dir=None)`**
Computes the maximum 2‑day rainfall for a single year.

Returns a 2D float32 array.

### **`compute_rx2day_baseline(chirps_meta, start_year, end_year, rx2day_dir)`**
Computes Rx2day for all years in the baseline period.

Saves one `.npy` file per year.

### **`compute_p95_from_rx2day(rx2day_dir, out_path=None)`**
Loads all Rx2day arrays and computes the pixel‑wise 95th percentile.

Returns a 2D float32 array.

### **`compute_baseline_metrics(start_year, end_year, rx2day_dir, p95_path=None)`**
High‑level helper that:
1. Loads CHIRPS metadata  
2. Computes Rx2day for baseline years  
3. Computes P95  

---

## Usage Example

```python
from pathlib import Path
from ccart_floods.chirps.compute_metrics import compute_baseline_metrics

rx2day_dir = Path("outputs/rx2day")
p95_path   = Path("outputs/p95_rx2day.npy")

p95 = compute_baseline_metrics(
    start_year=1995,
    end_year=2024,
    rx2day_dir=rx2day_dir,
    p95_path=p95_path
)

print("P95 shape:", p95.shape)
```
---

## Notes
- All computations are memory‑safe: only one year of CHIRPS data is loaded at a time.
- Rx2day arrays are saved as `.npy` files for fast reuse.
- P95 uses `np.nanpercentile` to avoid bias from zero‑rainfall pixels.
- This module does not compute hazard — that is handled by the hazard subsystem.
- CHIRPS ingestion (loading, clipping, cleaning) is handled by `ingest_chirps.py`.