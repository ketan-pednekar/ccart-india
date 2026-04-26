## FSI v1.1 — Empirical IndoFloods Susceptibility

### Inputs

- IndoFloods catchment descriptors (catchment_characteristics_indofloods.csv)
- IndoFloods metadata (metadata_indofloods.csv)

### New in v2

- Basin names are cleaned and standardised before merging
- A basin‑name audit prints unique names and counts (diagnostic only)

### Variables Used

| Variable             | Why It Matters                                   |
|----------------------|--------------------------------------------------|
| Drainage Density     | Controls runoff concentration                    |
| Catchment Relief     | Steeper basins → flashier floods                |
| Ruggedness Number    | Terrain complexity                               |
| Elongation Ratio     | Basin shape → hydrograph response                |
| Form Factor          | Width/length ratio                               |
| Annual Precipitation | Climatic forcing                                 |
| Soil Type            | Infiltration/runoff behaviour                    |

All numeric variables are **min–max normalised**.

Soils are **one‑hot encoded** and averaged into a composite `Soil_block`.

### FSI v1.1 formula

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
The output is a **GeoDataFrame** with point geometry (EPSG:4326).

---

## FSI v1.2 — Hydrology‑Enhanced Susceptibility

### Inputs

- HydroBASINS L06 polygons
- India boundary (for spatial filtering)
- Output of FSI v1.1

| File            | Description                                      |
|-----------------|--------------------------------------------------|
| CATCHMENT_CSV   | IndoFloods geomorphology + soil descriptors      |
| META_CSV        | Gauge metadata (coordinates, basin, state)       |
| EVENTS_CSV      | IndoFloods flood event metadata (not used here)  |
| PRECIP_CSV      | IndoFloods precipitation variables (not used)    |
| HYBAS_SHP       | HydroBASINS polygons with hydrological attributes|
| INDIA_SHP       | India boundary for spatial filtering             |


### Variables Used

| Variable  | Meaning                                | Why It Matters                                  |
|-----------|-----------------------------------------|--------------------------------------------------|
| UP_AREA   | Total upstream contributing area        | Larger upstream → more inflow → higher risk     |
| SUB_AREA  | Area of the basin polygon               | Basin size context                               |
| ORDER     | Strahler stream order                   | Maturity of river network                        |
| n_gauges  | Number of IndoFloods gauges in basin    | Indicates empirical support                      |
| Proxy_flag| 1 = no gauges, 0 = has gauges           | Used to mask ungauged basins                    |

### Steps

**1. Filter HydroBASINS to India**

Only basins intersecting India are retained.

**2. Identify empirical vs proxy basins**

A spatial join counts how many IndoFloods gauges fall inside each basin:

```python
n_gauges = number of IndoFloods gauges in basin
Proxy_flag = 1 if n_gauges == 0 else 0
```

Basins with no gauges are **proxy basins** and will be masked.

**3. Assign hydrological attributes**

Each gauge inherits:

- `UP_AREA`
- `SUB_AREA`
- `ORDER`
- `Proxy_flag`

**4. Normalise hydrological variables**

```python
UP_AREA_norm
SUB_AREA_norm
ORDER_norm
```

**5. Compute FSI v1.2**

```python
FSI_v1_2 = 0.5 * FSI_v1_1 + 0.5 * UP_AREA_norm
```

**6. Apply proxy mask**

```python
FSI_masked = NaN if Proxy_flag == 1 else FSI_v1_2
```

This ensures CCART does **not** assign false confidence to ungauged basins.

### Final Output

`compute_fsi()` returns a **GeoDataFrame** with the following key columns:

| Column       | Meaning                                                |
|--------------|--------------------------------------------------------|
| FSI_v1_1     | Empirical susceptibility (IndoFloods only)             |
| FSI_v1_2     | Hydrology‑enhanced susceptibility (IndoFloods + HYBAS) |
| FSI_masked   | Final recommended FSI (NaN for proxy basins)           |
| HYBAS_ID     | HydroBASINS Level‑06 basin ID                          |
| Proxy_flag   | 1 = ungauged basin, 0 = empirical basin                |
| geometry     | Point geometry (EPSG:4326)                             |

This output is ready for **rasterisation to the CHIRPS grid**.

---

## Functions in This Module

`compute_fsi_v1_1()`

Builds empirical susceptibility using IndoFloods descriptors.

`compute_fsi_v1_2(gdf_v1_1)`

Adds hydrological context and proxy masking.

`compute_fsi()`

Unified entry point returning the final susceptibility layer.

---

## Usage Example

```python
from ccart.flood.fsi.compute_fsi import compute_fsi

gdf_fsi = compute_fsi()
print(gdf_fsi[["GaugeID", "FSI_masked"]].head())
```
---

## Notes

- FSI is static and does not depend on rainfall.
- Proxy basins are masked to avoid over‑interpretation.
- FSI is rasterised to the CHIRPS grid before entering the hazard engine.
- Hazard is computed later as:

    ```python
    Hazard = FSI × Rainfall Anomaly
    ```