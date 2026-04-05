# CCART‑Floods — FSI Utilities (`utils_fsi.py`)

## Purpose
`utils_fsi.py` contains a focused set of shared helper functions used across the Flood Susceptibility Index (FSI) subsystem. These utilities support:

- Min–max normalisation  
- Soil type encoding  
- Spatial join wrappers  
- Raster masking to administrative boundaries  

By centralising these common operations, the FSI subsystem remains modular, readable, and scientifically reproducible.

---

## Functions in This Module

### **1. `normalise(series)`**
Performs min–max normalisation with safe handling of constant columns.  
Used in both **FSI v1.1** and **FSI v1.2**.

**Returns:**  
A `pd.Series` scaled to the range **[0, 1]**.

---

### **2. `encode_soils(df, col="Soil type")`**
One‑hot encodes soil categories and computes a composite `Soil_block` score.  
Used in **FSI v1.1**.

**Returns:**  
A DataFrame containing soil dummy variables and a soil block score.

---

### **3. `spatial_join_points_to_polygons(points_gdf, poly_gdf, how="left")`**
Wrapper around `geopandas.sjoin` using the `within` predicate.  
Used in **FSI v1.2** to assign HydroBASINS attributes to INDOFLOODS gauge points.

**Returns:**  
A GeoDataFrame with polygon attributes joined to point features.

---

### **4. `mask_to_boundary(raster, boundary_gdf, transform)`**
Applies a polygon mask (e.g., India boundary) to a raster.  
Pixels outside the boundary become `NaN`.

Useful for:
- future FSI v1.3 (proxy hydrology)  
- hazard masking  
- general raster clipping  

**Returns:**  
A masked raster with `NaN` outside the boundary.

---

## Usage Example

```python
from ccart_floods.fsi.utils_fsi import (
    normalise,
    encode_soils,
    spatial_join_points_to_polygons,
    mask_to_boundary
)
```
## Notes

- This module now contains only utilities actively used in the FSI subsystem.
- IDW interpolation and FSI cleaning utilities have been removed to avoid duplication and maintain hydrological consistency.
- All utilities are lightweight, reusable, and designed to support the modular FSI architecture.