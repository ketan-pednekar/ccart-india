# CCART Synthetic Cyclone Batch Runner  
### Script: `run_synthetic_batch_multi.py`  
**Module:** CCART–Cyclones (Synthetic Hazard Engine)  
**Purpose:** Execute large‑scale synthetic cyclone simulations across multiple climate scenarios, manage run directories, handle retries, and produce scenario‑level and master summaries.

---

## 🌪️ Overview

`run_synthetic_batch_multi.py` is the **batch‑execution layer** of the CCART synthetic cyclone engine.  
It automates the generation of synthetic storms across multiple climate scenarios:

- `baseline`  
- `warm_sst`  
- `high_end`  

For each scenario, the script:

- runs a configurable number of synthetic simulations  
- creates a clean folder structure  
- stores track + hazard outputs  
- records metadata for each run  
- produces scenario‑level and master summary CSVs  

This script is designed for **high‑volume ensemble generation**, enabling CCART to produce thousands of synthetic storms for hazard modelling, risk analysis, and scenario exploration.

---

## 🧩 Key Components

### **1. Scenario Management**
The script loops over all defined scenarios:

```python
SCENARIOS = ["baseline", "warm_sst", "high_end"]
```