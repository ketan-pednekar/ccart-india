# CCART v2 — District-Level Choropleth Visualization Module

This module provides a robust, geometry-safe choropleth plotting function for district-level climate risk outputs.  
It is designed to work seamlessly with CCART’s cyclone, flood, and heat modules, producing clean, publication-ready maps.

---

## 🎯 Purpose

`ccart_choropleth_v2` creates a district-level choropleth map by merging:

- a **district GeoDataFrame** (boundaries)
- a **loss/exposure DataFrame** (numeric values)

It is engineered to handle messy real-world data, including:

- duplicate geometry columns (`geometry_x`, `geometry_y`)
- duplicate loss columns (`loss_x`, `loss_y`)
- invalid or empty geometries
- missing districts
- optional state filtering

This makes it ideal for India-wide or state-specific climate risk mapping.

---

## 🧩 Function Signature

```python
ccart_choropleth_v2(
    gdf_districts: gpd.GeoDataFrame,
    df_losses,
    district_col: str = "District",
    loss_col: str = "loss_usd_hwe",
    state_filter=None,
    title: str = "",
    save_path: str | None = None,
    cmap: str = "Reds",
)
```
## 📥 Inputs

| Parameter       | Type          | Description                                      |
|-----------------|---------------|--------------------------------------------------|
| `gdf_districts` | GeoDataFrame  | District boundaries with a valid `geometry` column |
| `df_losses`     | DataFrame     | Must contain `district_col` + `loss_col`          |
| `district_col`  | str           | Merge key (default: `"District"`)                 |
| `loss_col`      | str           | Column to visualize (default: `"loss_usd_hwe"`)   |
| `state_filter`  | str or list   | Optional filter for specific states               |
| `title`         | str           | Plot title                                        |
| `save_path`     | str           | Optional file path to save PNG                    |
| `cmap`          | str           | Matplotlib colormap (default: `"Reds"`)           |

---
## 📤 Outputs

- Displays a district-level choropleth map  
- Saves a PNG file if `save_path` is provided  
- Returns nothing (plot only)  
- Missing districts appear in light grey  
- Colorbar is automatically included  

---

## 🔧 Internal Processing Steps

### **1. Validate and normalize geometry**
- Ensures `gdf_districts` is a proper GeoDataFrame  
- Forces the active geometry column to `"geometry"`  
- Removes accidental geometry columns from `df_losses`

### **2. Merge districts + losses**
- Left-join on `district_col`  
- Ensures all districts appear even if loss data is missing  

### **3. Resolve duplicate columns**
Handles cases like:

- `loss_col_x`, `loss_col_y`  
- `geometry_x`, `geometry_y`  

Always prefers the loss column from `df_losses`.

### **4. Clean geometry**
- Fixes invalid polygons using `buffer(0)`  
- Drops empty or invalid geometries  
- Ensures CRS is preserved  

### **5. Optional state filtering**
Supports:

```python
state_filter="Odisha"
state_filter=["Odisha", "Andhra Pradesh"]
```
Also removes dummy states ("0") and nulls.

---
### **6. Plot**

- District boundaries drawn in **black**  
- Missing data shown in **light grey**  
- Colorbar automatically included  
- Aspect ratio preserved for accurate geography  
- Optional PNG export when `save_path` is provided  

**🗺 Example Usage**
```python
from ccart_viz import ccart_choropleth_v2

ccart_choropleth_v2(
    gdf_districts=gdf_india_districts,
    df_losses=df_cyclone_losses,
    district_col="District",
    loss_col="loss_usd_hwe",
    state_filter="Andhra Pradesh",
    title="Cyclone Losses — Vizag Region",
    save_path="vizag_cyclone_losses.png",
    cmap="Reds",
)
```

## ⚠️ Notes & Best Practices

- Ensure district names match between `gdf_districts` and `df_losses`  
- Use consistent CRS across all GeoDataFrames before merging  
- For highly skewed loss values, consider log-transforming the loss column prior to plotting  
- Missing districts will appear in light grey  
- Very small or invalid polygons may be dropped during geometry cleaning  
- When filtering by state, ensure the `state` column exists in the district GeoDataFrame  
- Use high DPI (e.g., 300) when exporting PNGs for reports or publications  

---

## 📌 Status

This visualization module is **stable** and actively used in CCART cyclone case studies.  
It will be extended and integrated with flood and heat hazard outputs in **CCART v3**, ensuring consistent, publication-ready mapping across all hazard types.
