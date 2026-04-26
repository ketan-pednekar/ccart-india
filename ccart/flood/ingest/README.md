# CCART‑Floods — Ingestion Subsystem

**Canonical, reproducible ingestion of CHIRPS and CMIP6 datasets (Version 1.1)**

---

## 🌐 Overview

The **Ingestion Subsystem** of CCART‑Floods provides all rainfall and temperature inputs required by downstream hazard engines.
It ensures that **historical** and **future datasets** share:

- **A common spatial grid** (CHIRPS/FSI 0.05°)
- **Standardized units**
- **Consistent temporal structure**
- **Config‑driven paths**
- **Reproducible workflows**

The ingestion layer consists of three canonical modules:

- **CHIRPS Ingestion** — daily rainfall rasters
- **Historical CHIRPS Loader** — Zarr‑based historical dataset
- **CMIP6 Ingestion** — multi‑model, scenario‑aware future datasets

Together, they form the **foundation** for all CCART‑Floods hazard engines.

---

## 🧱 Modules

### 1. CHIRPS Ingestion (`chirps_ingest.py`)

Loads daily CHIRPS rainfall rasters and establishes the **canonical CHIRPS grid**.

**Capabilities:**

- Global or region‑clipped ingestion
- Cleans invalid rainfall values
- Extracts reference grid (`shape`, `transform`, `CRS`)
- Provides callable `load_day()`
- Fully config‑driven (paths.yaml)

**Outputs:**

- `file_df` — inventory of daily CHIRPS files
- `shape`, `lats`, `lons`
- `transform`, `crs`
- `region_geom`, `clip`
- `load_day(fp)`

### 2. Historical CHIRPS Loader (`ingest_chirps_hist.py`)

Loads the **pre‑processed CHIRPS India Zarr dataset** (`pr_hist`).

### Capabilities:

- CF‑compliant Zarr ingestion
- CHIRPS‑aligned grid
- No cleaning or preprocessing
- Provides historical rainfall for hazard engines

### Outputs:

- `xarray.Dataset` with variable `pr`
- Historical time range
- CHIRPS‑aligned grid


### 3. CMIP6 Ingestion (`ingest_cmip6.py`)

Multi‑model, scenario‑aware ingestion of CMIP6 rainfall and temperature.

### Capabilities:

- Reads daily `pr` and `tasmax` NetCDFs
- Converts units:
    - `pr`: kg m⁻² s⁻¹ → mm/day
    - `tasmax`: K → °C
- Regrids CMIP6 to CHIRPS 0.05° grid
- Provides year‑wise loaders
- Fully config‑driven (paths.yaml)

### Outputs:

- `pr_files`, `tasmax_files` (year‑indexed)
- `load_pr_year(path)`
- `load_tasmax_year(path)`
- CHIRPS‑aligned grid metadata

### ✅ CCART‑Floods — Ingestion Subsystem Block Diagram

+---------------------------------------------------------------+
|                     CCART‑FLOODS INGESTION                    |
|                 Canonical Climate Data Ingestion              |
+---------------------------------------------------------------+

        +----------------------+        +----------------------+
        |   CHIRPS Rasters     |        |  CHIRPS India Zarr   |
        |   (Daily GeoTIFF)    |        |   (pr_hist, Zarr)    |
        +----------+-----------+        +----------+-----------+
                   |                               |
                   |                               |
                   v                               v
        +----------------------+        +----------------------+
        |   CHIRPS Ingestion   |        | Historical CHIRPS    |
        |  (chirps_ingest.py)  |        | Loader               |
        +----------------------+        | (ingest_chirps_hist) |
        | - Clean values       |        +----------------------+
        | - Clip region        |        | - Load Zarr dataset  |
        | - Build grid         |        | - Validate `pr`      |
        | - load_day()         |        | - Return Dataset     |
        +----------+-----------+        +----------+-----------+
                   |                               |
                   |                               |
                   |                               |
                   |                               |
                   v                               v
        +------------------------------------------------------+
        |            Canonical CHIRPS Reference Grid           |
        |        (shape, lats, lons, transform, CRS)           |
        +------------------------------------------------------+

                                |
                                |
                                v

        +----------------------+        +----------------------+
        |   CMIP6 NetCDFs      |        |   CMIP6 Ingestion    |
        | (pr, tasmax, daily)  |        | (ingest_cmip6.py)    |
        +----------+-----------+        +----------------------+
                   |                    | - Inventory files    |
                   |                    | - Convert units      |
                   |                    | - Regrid to CHIRPS   |
                   |                    | - Year‑wise loaders  |
                   |                    +----------+-----------+
                   |                               |
                   v                               v

        +------------------------------------------------------+
        |     Future Rainfall & Temperature (Year‑wise Arrays) |
        |     pr (mm/day), tasmax (°C), CHIRPS‑aligned         |
        +------------------------------------------------------+

                                |
                                v

        +------------------------------------------------------+
        |      Outputs Ready for All CCART‑Floods Engines      |
        |  (Historical Hazard, Future Hazard, Hazard‑Max, etc.)|
        +------------------------------------------------------+


---

## 📦 What the Ingestion Layer Guarantees

- All datasets share the **same spatial grid**
- All rainfall is in **mm/day**
- All temperature is in **°C**
- All paths are resolved from **config**
- No hardcoded assumptions
- Historical and future datasets are **interoperable**
- Outputs are **directly consumable** by hazard engines