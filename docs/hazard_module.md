"""
# CCART v1.0 — Cyclone Hazard Module

This document describes the logic, assumptions, and workflow behind the
cyclone hazard engine implemented in `hazard.py`.

## Overview

The hazard module builds single-event tropical cyclone footprints from
IBTrACS best-track data using CLIMADA, and aggregates them to district level.

It contains two main functions:
- `build_hazard()`: construct a CLIMADA TropCyclone hazard object
- `compute_district_hazard_stats()`: compute district-level hazard metrics

## 1. Hazard Construction Workflow

### 1.1 Load IBTrACS Track
- Reads best-track data for a single storm
- Validates storm_id
- Extracts lat/lon arrays

### 1.2 Build Corridor Grid
- Defines bounding box around the track
- Expands by `corridor_deg`
- Creates regular centroid grid at `grid_res_deg`

### 1.3 Generate CLIMADA Hazard
- Calls `TropCyclone.from_tracks`
- Cleans intensity matrix (no negatives, CSR format)
- Ensures fraction matrix is CSR
- Runs `haz.check()`

### Output: A single-event TropCyclone hazard object.

## 2. District-Level Hazard Statistics

### 2.1 Convert Centroids to GeoDataFrame
- Uses lat/lon from hazard centroids
- Attaches wind speed from intensity matrix

### 2.2 Spatial Join with District Polygons
- Drops join artefact columns
- Performs point-in-polygon join

### 2.3 Aggregate Metrics
- Max wind speed
- Mean wind speed
- Number of centroids per district

### Output: DataFrame with district-level hazard metrics.
"""
