"""
CCART v1.0 — Hazard Module
--------------------------

This module contains all hazard-related functions for the CCART Cyclone
Impact Engine, including:

- Loading IBTrACS tracks
- Building a corridor centroid grid
- Generating CLIMADA TC hazard footprints
- Computing district-level hazard statistics

These functions are reusable across states and cyclones.
"""

import numpy as np
import geopandas as gpd
from scipy import sparse
from climada.hazard import TCTracks, TropCyclone, Centroids


def build_hazard(storm_id: str, ibtracs_path: str,
                 corridor_deg: float = 1.5,
                 grid_res_deg: float = 0.05):
    """
    Build CLIMADA tropical cyclone hazard from IBTrACS best-track data.

    Parameters
    ----------
    storm_id : str
        IBTrACS storm identifier (e.g., "2019116N02090" for Fani).
    ibtracs_path : str
        Path to IBTrACS NetCDF file.
    corridor_deg : float
        Half-width of the corridor around the track (degrees).
    grid_res_deg : float
        Resolution of the centroid grid (degrees).

    Returns
    -------
    TropCyclone
        CLIMADA hazard object with cleaned intensity matrix.
    """

    tracks = TCTracks.from_ibtracs_netcdf(
        provider=None,
        storm_id=[storm_id],
        file_name=ibtracs_path,
    )

    if len(tracks.data) == 0:
        raise ValueError(f"No track data found for storm_id={storm_id}")

    trk = tracks.data[0]
    trk_lats = np.array(trk.lat, dtype=float)
    trk_lons = np.array(trk.lon, dtype=float)

    lat_min = trk_lats.min() - corridor_deg
    lat_max = trk_lats.max() + corridor_deg
    lon_min = trk_lons.min() - corridor_deg
    lon_max = trk_lons.max() + corridor_deg

    lats = np.arange(lat_min, lat_max, grid_res_deg)
    lons = np.arange(lon_min, lon_max, grid_res_deg)
    lon_grid, lat_grid = np.meshgrid(lons, lats)

    cent = Centroids(
        lat=lat_grid.ravel(),
        lon=lon_grid.ravel(),
        crs="EPSG:4326"
    )

    haz = TropCyclone.from_tracks(tracks, centroids=cent)

    intensity_dense = haz.intensity.toarray()
    intensity_dense[intensity_dense < 0] = 0
    haz.intensity = sparse.csr_matrix(intensity_dense)
    haz.intensity_thres = haz.intensity.copy()

    if not isinstance(haz.fraction, sparse.csr_matrix):
        haz.fraction = sparse.csr_matrix(haz.fraction)

    haz.check()

    return haz


def compute_district_hazard_stats(haz, districts: gpd.GeoDataFrame):
    """
    Compute district-level hazard statistics from CLIMADA centroids.

    Parameters
    ----------
    haz : TropCyclone
        CLIMADA hazard object.
    districts : GeoDataFrame
        District polygons with a 'District' column.

    Returns
    -------
    DataFrame
        Columns:
        - District
        - WindSpeed_Max_mps
        - WindSpeed_Mean_mps
        - Centroid_Count
    """

    cent = gpd.GeoDataFrame(
        {
            "lat": haz.centroids.lat,
            "lon": haz.centroids.lon
        },
        geometry=gpd.points_from_xy(haz.centroids.lon, haz.centroids.lat),
        crs="EPSG:4326"
    )

    wind = haz.intensity.toarray()[0]
    cent["wind_speed"] = wind

    districts_clean = districts.drop(
        columns=["index_left", "index_right"], errors="ignore"
    )

    joined = gpd.sjoin(
        cent,
        districts_clean,
        how="inner",
        predicate="within"
    )

    hazard_stats = (
        joined.groupby("District")["wind_speed"]
        .agg(["max", "mean", "count"])
        .reset_index()
        .rename(
            columns={
                "max": "WindSpeed_Max_mps",
                "mean": "WindSpeed_Mean_mps",
                "count": "Centroid_Count"
            }
        )
    )

    return hazard_stats