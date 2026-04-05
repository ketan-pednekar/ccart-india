# CCART-Floods — Configuration Module (`config.py`)

## Purpose
The `config.py` module centralises all global settings, directory paths, and
constants used across the CCART‑Floods framework. By keeping configuration in a
single location, the entire pipeline becomes reproducible, portable, and easier
to maintain. All other modules import paths and constants from here, ensuring
that no hard‑coded paths or magic numbers appear inside scientific code.

This module is the backbone of the CCART‑Floods architecture.

---

## Scientific Background
CCART‑Floods integrates multiple datasets:
- INDOFLOODS (empirical flood susceptibility)
- HydroBASINS (hydrological context)
- CHIRPS (observed rainfall)
- CMIP6 (future rainfall extremes)

Each dataset lives in a different directory and uses different spatial
resolutions. A central configuration file ensures:
- consistent directory structure  
- reproducible file access  
- clean separation between *data* and *code*  
- easy switching between machines or environments  

This is essential for scientific reproducibility.

---

**Location:** `ccart/floods/config.py`

---

## Contents of This Module

| Variable | Description |
|---------|-------------|
| `PROJECT_ROOT` | Root folder for the CCART‑Floods project |
| `CATCHMENT_CSV` | INDOFLOODS catchment characteristics |
| `EVENTS_CSV` | INDOFLOODS flood event records |
| `META_CSV` | INDOFLOODS gauge metadata |
| `PRECIP_CSV` | INDOFLOODS precipitation variables |
| `HYBAS_SHP` | HydroBASINS polygons (level 6) |
| `INDIA_SHP` | India boundary shapefile |
| `CHIRPS_DAILY_DIR` | Directory containing CHIRPS daily rainfall |
| `CHIRPS_MONTHLY_DIR` | Directory containing CHIRPS monthly rainfall |
| `CMIP6_DIR` | CMIP6 rainfall (pre‑clipped to India) |
| `OUTPUT_DIR` | Root output directory |
| `FSI_OUTPUT_DIR` | Output folder for FSI rasters |
| `DYNAMIC_HAZARD_DIR` | Output folder for dynamic hazard results |
| `BASELINE_START/END` | Historical baseline window (1995–2024) |
| `FUTURE_START/END` | Future projection window (2027–2100) |
| `CHIRPS_RESOLUTION` | CHIRPS grid resolution (0.05°) |
| `IDW_RESOLUTION` | IDW interpolation resolution (0.10°) |
| `EPS` | Small constant to avoid divide‑by‑zero |
| `VERBOSE` | Global verbosity flag |

---

## Usage Example

```python
from ccart_floods.config import (
    CATCHMENT_CSV,
    HYBAS_SHP,
    CHIRPS_DAILY_DIR,
    BASELINE_START,
    BASELINE_END
)

print("Catchment file:", CATCHMENT_CSV)
print("CHIRPS daily directory:", CHIRPS_DAILY_DIR)
print("Baseline window:", BASELINE_START, BASELINE_END)
```
This ensures that all modules use the same paths and constants.

## Notes

- All paths are defined using pathlib.Path for OS‑agnostic behaviour.
- Only this file should contain absolute paths; all other modules must import from here.
- Changing the project root automatically updates all dependent paths.
- The baseline and future windows are defined here to ensure consistency across CHIRPS, CMIP6, and hazard modules.
- EPS is used in hazard calculations to avoid division by zero when computing relative rainfall extremes.