# CCART Synthetic Cyclone Generator

***Modular, scenario‑aware synthetic track engine for India landfalling cyclones***

This module implements the **full synthetic cyclone generation pipeline** used in CCART.
It transforms cleaned historical tracks into **realistic, perturbed, scenario‑aware synthetic cyclones**, ready for hazard modelling with CLIMADA.

The generator includes:

- landfall filtering
- DBSCAN clustering
- cluster-size-weighted sampling
- PCA‑based analog refinement
- genesis jitter
- track perturbation
- intensity variety
- scenario logic
- RMW and rainfall variety
- CLIMADA‑safe variable enforcement

The output is a **single synthetic cyclone track** as an `xarray.Dataset`, fully compatible with CCART’s hazard builder.

---

## 🌊 Overview

The synthetic generator follows a structured workflow:

1. Load cleaned historical tracks
2. Filter for India‑relevant, landfalling storms
3. Cluster tracks using DBSCAN
4. Select clusters using weighted sampling
5. Refine analogs using PCA + cosine similarity
6. Select one representative analog
7. Apply scenario‑aware perturbations
8. Enforce CLIMADA‑safe constraints
9. Return a fully synthetic track

This module is country‑agnostic, but currently configured for India landfall using a mainland coastline mask.

---

## 📁 Module Contents

**Track Loading & Filtering**

-`load_clean_tracks`
-`track_makes_landfall`
- `resample_track`

**Clustering & Analog Selection**

- `cluster_tracks`
- `refine_analogs`

**Perturbation Components**

-`jitter_genesis`
- `perturb_track`
- `enforce_minimum_spacing`
- `translation_speed_variety`

**Intensity & Structure Variety**

- `intensity_variety`
- `rmw_variety`
- `rainfall_variety`

**Scenario Logic**

- `apply_scenario_modifiers`

**Main Generator**
`build_synthetic_cyclone`

---

## 🌍 Coastline Handling

The synthetic generator requires a **mainland coastline shapefile**, supplied by the caller.
This coastline is used to:

- identify India‑relevant landfalling storms  
- ensure genesis jitter remains over ocean  
- construct a 20 km buffer for safe landfall detection  

The generator applies the following preprocessing steps internally:

- exclude Andaman & Nicobar  
- exclude Lakshadweep  
- union mainland geometry  
- build a 20 km buffer for landfall detection  


---

## 🔍 Key Scientific Features

**Weighted cluster sampling**

Clusters are selected with probability proportional to their size:

- preserves climatological frequency
- avoids over‑sampling rare tracks
- improves realism of synthetic ensembles

**Genesis jitter**

Small, ocean‑only displacement of the genesis point.

**Track perturbation**

Gaussian noise + spline smoothing + curvature index.

**Minimum spacing enforcement**

Ensures each step moves ≥ 5 km to avoid CLIMADA zero‑motion errors.

**Intensity variety**

Peak scaling, decay scaling, and timing shifts.

**Scenario logic**

Modifies:

- peak intensity
- decay rate
- track perturbation sigma

**RMW & rainfall variety**

Adds structural diversity.

**CLIMADA‑safe constraints**

Ensures:

- radius_max_wind exists
- radius_oci exists
- ΔP is positive
- all arrays are 1D

## 🔍 Function‑Level Documentation (Expanded)

Below is the full CCART‑grade documentation for each function.

### `load_clean_tracks(file_path, min_wind=35)`

Load historical tracks from an HDF5 file and filter storms with peak wind ≥ min_wind.

**Returns:**  

A list of `TCTracks` entries.

### `track_makes_landfall(trk)`

Checks whether a track:

- intersects the 20 km coastline buffer
- has peak wind ≥ 40 kt
- has meaningful latitudinal extent

**Returns:** `True` or `False`.

### `cluster_tracks(tracks, eps=12.0, min_samples=2)`

Resamples each track to 50 points, normalizes, concatenates lat/lon, and applies DBSCAN.

**Returns:**  

Cluster labels for each track.

### `refine_analogs(tracks, labels, target_cluster, top_n=5)`

Within the target cluster:

1. Resample tracks
2. Reduce dimensionality with PCA
3. Compute cosine similarity
4. Compute centrality
5. Select `top_n` analogs using **probability weighted by centrality**

**Returns:**  

A list of refined analog tracks.

### `jitter_genesis(lat0, lon0, max_jitter_deg=0.3, ocean_mask=None)`

Applies a small random displacement to the genesis point, ensuring it remains over ocean.

**Returns:**  
`(new_lat, new_lon, jitter_deg)`.

### `perturb_track(lat, lon, sigma_deg=0.15, smooth_factor=3.0)`

Applies Gaussian noise to mid‑track points and smooths with a spline.

**Returns:**  
`(lat_smooth, lon_smooth, curvature_index)`.

### `enforce_minimum_spacing(lat, lon, min_dist_km=5)`

Ensures each step in the track moves at least `min_dist_km` to avoid CLIMADA crashes.

### `translation_speed_variety(lat, lon, speed_scale_range=(0.9, 1.1))`
Scales forward motion by adjusting time spacing.

### `intensity_variety(wind, peak_scale_range, decay_scale_range, shift_max)`

Applies:

- peak multiplier
- decay multiplier
- timing shift

**Returns:**  
`(new_wind, metadata)`.

### `apply_scenario_modifiers(scenario)`
Returns scenario‑specific multipliers for:

- peak intensity
- decay rate
- track perturbation sigma

Supported scenarios:

- `baseline`
- `warm_sst`
- `high_end`

### `rmw_variety(rmw, scale_range)`

Applies multiplicative variety to radius of maximum wind.

### `rainfall_variety(scale_range)`

Returns a random rainfall scaling factor.

---

## 🌪️ Main Function

### `build_synthetic_cyclone(...)`

The full synthetic cyclone generator.

**Inputs**

- `file_path` — cleaned historical tracks (HDF5)
- `coastline_path` — path to mainland coastline shapefile (user-supplied)
- `min_wind` — minimum storm intensity
- `cluster_eps`, `cluster_min_samples` — DBSCAN parameters
- `top_n` — number of analogs to refine
- `wind_boost` — global intensity multiplier
- `scenario` — scenario name


**Outputs**

A fully synthetic cyclone track (`xarray.Dataset`) with:

- lat/lon
- max sustained wind
- central pressure
- environmental pressure
- radius of maximum wind
- radius of outer closed isobar
- metadata for all perturbations

**Key Steps**

1. Load & filter tracks
2. Cluster & refine analogs
3. Select base track
4. Apply scenario logic
5. Apply perturbations
6. Apply intensity variety
7. Apply RMW & rainfall variety
8. Enforce CLIMADA‑safe constraints
9. Return synthetic track

---

## 🧩 Metadata Stored in Output

The synthetic track includes metadata fields such as:

- `genesis_jitter_deg`
- `track_sigma_deg`
- `track_curvature_index`
- `translation_speed_scale`
- `intensity_peak_scale`
- `intensity_decay_scale`
- `intensity_timing_shift`
- `rmw_scale`
- `rainfall_scale`
- scenario multipliers

This makes synthetic tracks **fully traceable** and **reproducible**.

---

## ⚠️ Notes & Caveats

- This module is optimized for **India landfalling cyclones**.
- Requires a mainland coastline shapefile.
- Outputs are compatible with CCART hazard generation.
- All arrays are reshaped to 1D before return.
- Pressure deltas are enforced to avoid CLIMADA failures.
- Track spacing is enforced to avoid zero‑motion errors.

---

## 🎯 Summary

`synthetic_generator.py` is the **core synthetic cyclone engine** of CCART.

It combines:

- statistical analog selection
- weighted cluster sampling 
- physical perturbations
- scenario logic
- structural variety
- CLIMADA‑safe constraints

into a single, clean, reproducible pipeline.
