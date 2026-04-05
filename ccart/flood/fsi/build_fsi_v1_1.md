# CCART‑Floods — FSI v1.1 Builder (`build_fsi_v1_1.py`)

## Purpose
`build_fsi_v1_1.py` constructs **Flood Susceptibility Index (FSI) v1.1** using
only INDOFLOODS catchment descriptors and soil information.  

FSI v1.1 represents the **pure empirical susceptibility layer** based on
geomorphology, soils, and long‑term catchment characteristics — without any
hydrological context.  

It forms the foundation for the enhanced **FSI v1.2**.

---

## Scientific Background

FSI v1.1 uses INDOFLOODS catchment‑scale descriptors that influence how rainfall
is converted into runoff and how catchments respond to extreme rainfall.

### **Geomorphological descriptors**
- Drainage Density  
- Catchment Relief  
- Ruggedness Number  
- Elongation Ratio  
- Form Factor  
- Annual Precipitation  

These variables capture terrain shape, steepness, drainage efficiency, and
climatological forcing.

### **Soil type**
Soil categories are one‑hot encoded and averaged into a composite  
**`Soil_block`** score representing infiltration capacity and runoff potential.

### **Normalisation**
All numerical variables are min–max normalised to ensure comparability across
different units and magnitudes.

### **FSI v1.1 formula**

```python
FSI_v1_1 = mean([
    DrainageDensity_norm,
    CatchmentRelief_norm,
    Ruggedness_norm,
    Elongation_norm,
    FormFactor_norm,
    AnnualPrecip_norm,
    Soil_block
])
```
This produces a **0–1 susceptibility index**.

---

## Inputs

| File | Description |
|------|-------------|
| `CATCHMENT_CSV` | INDOFLOODS catchment‑scale geomorphology + soils |
| `META_CSV` | Gauge metadata (coordinates, basin, state) |

Both paths are imported from `ccart_floods.config`.

---

## Outputs

| Output | Description |
|--------|-------------|
| `GeoDataFrame` | Contains FSI_v1_1 and all intermediate variables |
| `geometry` | EPSG:4326 point geometry for each gauge |

This output is passed directly to `build_fsi_v1_2.py`.

---

## Functions in This Module

### **`build_fsi_v1_1()`**
Main function that:

1. Loads INDOFLOODS catchment descriptors and metadata  
2. Normalises geomorphological variables  
3. Encodes soil types into dummy variables  
4. Computes the composite `Soil_block` score  
5. Computes FSI v1.1 (strict 0–1)  
6. Joins metadata and returns a GeoDataFrame  

### **`_normalise(series)`**
Internal helper for min–max scaling with safe handling of constant columns.

---

## Usage Example

```python
from ccart_floods.fsi.build_fsi_v1_1 import build_fsi_v1_1

gdf = build_fsi_v1_1()
print(gdf[["GaugeID", "FSI_v1_1"]].head())
```
---

## Notes

- FSI v1.1 does not include hydrological attributes (UP_AREA, SUB_AREA, ORDER).
  These are added in **FSI v1.2**.
- Soil types are encoded using one‑hot vectors and averaged into a single score.
- FSI is a **susceptibility index**, not a probability or hazard metric.
- All variables are normalised to ensure equal weighting.
- Missing or constant columns are handled safely during normalisation.