"""
CCART Synthetic Exposure Module
--------------------------------
Handles:
- loading district geometries (country-agnostic)
- normalizing administrative names
- computing distance to coastline
- inland masking
- clipping exposure to hazard bounding box

All inputs (districts, coastline, exposures) must be supplied by the caller.
"""

import geopandas as gpd
from climada.entity import Exposures


# ------------------------------------------------------------
# Utility: Normalize names
# ------------------------------------------------------------
def _normalize_name(series):
    """Normalize district/state names to uppercase, single-spaced strings."""
    return (
        series.astype(str)
              .str.strip()
              .str.upper()
              .str.replace(r"\s+", " ", regex=True)
    )


# ------------------------------------------------------------
# 1. Load districts
# ------------------------------------------------------------
def load_districts(
    districts_path,
    district_col="district",
    state_col="state"
):
    """
    Load district geometries and normalize names.

    Parameters
    ----------
    districts_path : str
        Path to district-level shapefile/GeoJSON.
    district_col : str
        Column containing district names.
    state_col : str
        Column containing state/region names.

    Returns
    -------
    GeoDataFrame
        Columns: District, state_norm, geometry
    """
    gdf = gpd.read_file(districts_path)

    if district_col not in gdf.columns or state_col not in gdf.columns:
        raise ValueError(
            f"District/state columns not found. "
            f"Expected '{district_col}' and '{state_col}'."
        )

    gdf["district_norm"] = _normalize_name(gdf[district_col])
    gdf["state_norm"] = _normalize_name(gdf[state_col])
    gdf["District"] = gdf["district_norm"]

    # Ensure WGS84
    if gdf.crs is None or gdf.crs.to_string() != "EPSG:4326":
        gdf = gdf.to_crs("EPSG:4326")

    return gdf[["District", state_col, "state_norm", "geometry"]].copy()


# ------------------------------------------------------------
# 2. Compute distance to coast
# ------------------------------------------------------------
def compute_distance_to_coast(
    districts_gdf,
    coastline_gdf,
    inland_clip_km
):
    """
    Compute centroid distance to coastline and mark inland districts.

    Parameters
    ----------
    districts_gdf : GeoDataFrame
        District polygons in EPSG:4326.
    coastline_gdf : GeoDataFrame
        Coastline geometry in EPSG:4326.
    inland_clip_km : float
        Threshold distance beyond which districts are marked inland.

    Returns
    -------
    GeoDataFrame
        Adds dist_to_coast_km and is_inland columns.
    """
    # Ensure CRS consistency
    if coastline_gdf.crs is None or coastline_gdf.crs.to_string() != "EPSG:4326":
        coastline_gdf = coastline_gdf.to_crs("EPSG:4326")

    # Project to metric CRS for distance computation
    districts_proj = districts_gdf.to_crs("EPSG:3857")
    coast_proj = coastline_gdf.to_crs("EPSG:3857")

    centroids_proj = districts_proj.geometry.centroid
    dist_m = centroids_proj.distance(coast_proj.unary_union)

    districts_gdf["dist_to_coast_km"] = dist_m / 1000.0
    districts_gdf["is_inland"] = districts_gdf["dist_to_coast_km"] > inland_clip_km

    return districts_gdf


# ------------------------------------------------------------
# 3. Clip exposure to hazard bounding box
# ------------------------------------------------------------
def clip_exposure_to_hazard(exposures, hazard):
    """
    Clip exposure points to the bounding box of a hazard.

    Parameters
    ----------
    exposures : Exposures
        CLIMADA Exposures object with point geometries (EPSG:4326).
    hazard : Hazard
        CLIMADA Hazard object with centroids.lat/lon.

    Returns
    -------
    Exposures
        Exposure points inside hazard bounding box.

    Raises
    ------
    ValueError
        If no exposure points remain after clipping.
    """
    haz_lat_min = float(hazard.centroids.lat.min())
    haz_lat_max = float(hazard.centroids.lat.max())
    haz_lon_min = float(hazard.centroids.lon.min())
    haz_lon_max = float(hazard.centroids.lon.max())

    gdf = exposures.gdf

    clipped = gdf[
        (gdf.geometry.y >= haz_lat_min) &
        (gdf.geometry.y <= haz_lat_max) &
        (gdf.geometry.x >= haz_lon_min) &
        (gdf.geometry.x <= haz_lon_max)
    ].copy()

    if clipped.empty:
        raise ValueError("No exposure points fall inside hazard bounding box.")

    return Exposures(clipped)
