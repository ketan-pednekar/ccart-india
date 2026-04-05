# CCART‑Floods — FSI v1.2 Builder (`build_fsi_v1_2.py`)

## Purpose
`build_fsi_v1_2.py` constructs **Flood Susceptibility Index (FSI) v1.2** by
enhancing the empirical FSI v1.1 with **hydrological context** from
HydroBASINS Level‑6.  

FSI v1.2 introduces basin‑scale hydrological structure while preserving the
empirical foundation of FSI v1.1. It is the recommended susceptibility layer
for CCART‑Floods and serves as the input to the rasterisation pipeline.

---

## Scientific Background

FSI v1.2 extends FSI v1.1 by incorporating **hydrological descriptors** from
HydroBASINS, which provide a consistent, global, hierarchical representation of
river basins.

### **Hydrological descriptors included**
- **UP_AREA** — total upstream contributing area  
- **SUB_AREA** — local sub‑basin area  
- **ORDER** — Strahler stream order  

These variables capture how water accumulates and flows through the river
network, improving susceptibility estimates beyond pure geomorphology and soils.

### **Empirical vs Proxy Basins**
Each HydroBASINS polygon is classified as:

- **Empirical basin** → contains ≥1 INDOFLOODS gauge  
- **Proxy basin** → contains 0 gauges  

This ensures scientific honesty: CCART does not assign susceptibility values
where no empirical information exists.

### **Normalisation**

Hydrological variables are min–max normalised to ensure comparability.

### **FSI v1.2 formula**

To avoid overweighting hydrology, only **UP_AREA_norm** is used:

```python
FSI_v1_2 = 0.5 * FSI_v1_1 + 0.5 * UP_AREA_norm
```
This preserves the empirical foundation while adding hydrological realism.

### **Empirical Mask**

Proxy basins are masked:
`Proxy_flag = 1  →  FSI_masked = NaN`

This ensures that susceptibility exists only where empirical data supports it.

---
## Inputs

| Input | Type | Description |
|-------|------|-------------|
| `gdf_v1_1` | GeoDataFrame | Output of `build_fsi_v1_1()`, containing FSI_v1_1 and gauge coordinates |
| `HYBAS_SHP` | Shapefile | HydroBASINS Level‑6 polygons with hydrological attributes |
| `INDIA_SHP` | Shapefile | India boundary used to filter basins and gauges |

## Outputs

| Output Field | Type | Description |
|--------------|------|-------------|
| `FSI_v1_2` | float | Hydrologically‑enhanced susceptibility index (strict 0–1) |
| `FSI_masked` | float | FSI v1.2 masked to empirical basins (proxy basins → NaN) |
| `HYBAS_ID` | int | HydroBASINS basin ID |
| `UP_AREA` | float | Upstream contributing area (raw) |
| `SUB_AREA` | float | Local sub‑basin area (raw) |
| `ORDER` | int | Strahler stream order |
| `UP_AREA_norm` | float | Normalised upstream area (0–1) |
| `SUB_AREA_norm` | float | Normalised sub‑basin area (0–1) |
| `ORDER_norm` | float | Normalised stream order (0–1) |
| `Proxy_flag` | int | 1 = proxy basin, 0 = empirical basin |
| `geometry` | Point | EPSG:4326 gauge location |

This GeoDataFrame is passed directly to `rasterise_fsi.py`.

---

## Functions in This Module

`build_fsi_v1_2(gdf_v1_1)`

Main function that:

1. Loads HydroBASINS and India boundary
2. Identifies empirical vs proxy basins
3. Performs spatial join to attach hydrological attributes
4. Normalises hydrological variables
5. Computes FSI v1.2
6. Applies empirical mask (proxy basins → NaN)
7. Returns a GeoDataFrame ready for rasterisation.

`_normalise(series)`

Internal helper for min–max scaling.

---

## Usage Example

```Python
from ccart_floods.fsi.build_fsi_v1_1 import build_fsi_v1_1
from ccart_floods.fsi.build_fsi_v1_2 import build_fsi_v1_2

gdf_v1_1 = build_fsi_v1_1()
gdf_v1_2 = build_fsi_v1_2(gdf_v1_1)

print(gdf_v1_2[["GaugeID", "FSI_v1_2", "Proxy_flag"]].head())
```
---

## Notes

- HydroBASINS Level‑6 provides a balance between spatial detail and computational stability.
- Proxy basins are masked to NaN to avoid fabricating susceptibility where no empirical data exists.
- Only `UP_AREA_norm` is used in FSI v1.2 to prevent hydrological overweighting.
- FSI remains a susceptibility index, not a probability or hazard metric.
- Spatial joins use `within` to ensure correct basin assignment.