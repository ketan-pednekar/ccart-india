import numpy as np
from scipy import sparse
from climada.hazard import Centroids, TropCyclone


def build_hazard_from_tc_tracks(
    tc_tracks,
    corridor_deg: float = 1.5,
    grid_res_deg: float = 0.05,
    min_peak_wind_kn: float = 20.0,
    verbose: bool = True,
):
    """
    Build CLIMADA tropical cyclone hazard from a TCTracks object
    (synthetic or historical), restricted to a corridor around the track.

    Parameters
    ----------
    tc_tracks : TCTracks
        A TCTracks object containing exactly one storm.
    corridor_deg : float
        Half-width of the corridor around the track (degrees).
    grid_res_deg : float
        Resolution of the centroid grid (degrees).
    min_peak_wind_kn : float
        Minimum peak max_sustained_wind (knots) required to build a hazard.
        If the storm is weaker than this, returns a hazard with zero intensity.
    verbose : bool
        If True, print diagnostics.

    Returns
    -------
    TropCyclone
        CLIMADA hazard object with cleaned intensity matrix.
    """

    if tc_tracks.size != 1:
        raise ValueError("Expected TCTracks with exactly one storm.")

    trk = tc_tracks.data[0]

    # --- Basic track diagnostics ---
    trk_lats = np.array(trk.lat, dtype=float)
    trk_lons = np.array(trk.lon, dtype=float)
    peak_wind = float(trk["max_sustained_wind"].max()) if "max_sustained_wind" in trk else np.nan

    if verbose:
        print(">>> build_hazard_from_tc_tracks v2.1")
        print(f"  Track SID: {trk.attrs.get('sid', 'N/A')}")
        print(f"  Track name: {trk.attrs.get('name', 'N/A')}")
        print(f"  Peak max_sustained_wind: {peak_wind:.1f} kn")

    # --- Optional: skip very weak storms ---
    if not np.isnan(peak_wind) and peak_wind < min_peak_wind_kn:
        if verbose:
            print(f"  Peak wind < {min_peak_wind_kn} kn → building zero-intensity hazard.")
        # Build a minimal centroid grid around the track just for consistency
        lat_min = trk_lats.min() - corridor_deg
        lat_max = trk_lats.max() + corridor_deg
        lon_min = trk_lons.min() - corridor_deg
        lon_max = trk_lons.max() + corridor_deg

        lats = np.arange(lat_min, lat_max + grid_res_deg, grid_res_deg)
        lons = np.arange(lon_min, lon_max + grid_res_deg, grid_res_deg)
        lon_grid, lat_grid = np.meshgrid(lons, lats)

        cent = Centroids(
            lat=lat_grid.ravel(),
            lon=lon_grid.ravel(),
            crs="EPSG:4326"
        )

        haz = TropCyclone.from_tracks(tc_tracks, centroids=cent)
        # Force zero intensity
        n_events, n_centroids = haz.intensity.shape
        haz.intensity = sparse.csr_matrix((n_events, n_centroids))
        haz.intensity_thres = haz.intensity.copy()
        if not isinstance(haz.fraction, sparse.csr_matrix):
            haz.fraction = sparse.csr_matrix(haz.fraction)
        haz.check()
        if verbose:
            print(f"  Built zero-intensity hazard with {n_centroids} centroids.")
        return haz

    # --- Normal corridor-based hazard for non-weak storms ---
    lat_min = trk_lats.min() - corridor_deg
    lat_max = trk_lats.max() + corridor_deg
    lon_min = trk_lons.min() - corridor_deg
    lon_max = trk_lons.max() + corridor_deg

    lats = np.arange(lat_min, lat_max + grid_res_deg, grid_res_deg)
    lons = np.arange(lon_min, lon_max + grid_res_deg, grid_res_deg)
    lon_grid, lat_grid = np.meshgrid(lons, lats)

    cent = Centroids(
        lat=lat_grid.ravel(),
        lon=lon_grid.ravel(),
        crs="EPSG:4326"
    )

    if verbose:
        print(f"  Centroid grid:")
        print(f"    lat: {lat_min:.2f} → {lat_max:.2f} (n={len(lats)})")
        print(f"    lon: {lon_min:.2f} → {lon_max:.2f} (n={len(lons)})")
        print(f"    total centroids: {len(cent.lat)}")

    haz = TropCyclone.from_tracks(tc_tracks, centroids=cent)

    # Clean negative intensities
    intensity_dense = haz.intensity.toarray()
    intensity_dense[intensity_dense < 0] = 0.0
    haz.intensity = sparse.csr_matrix(intensity_dense)
    haz.intensity_thres = haz.intensity.copy()

    if not isinstance(haz.fraction, sparse.csr_matrix):
        haz.fraction = sparse.csr_matrix(haz.fraction)

    haz.check()

    if verbose:
        max_intensity = float(haz.intensity.max()) if haz.intensity.nnz > 0 else 0.0
        print(f"  Hazard built:")
        print(f"    events: {haz.event_id.size}")
        print(f"    centroids: {haz.centroids.size}")
        print(f"    max intensity: {max_intensity:.2f} (same units as input wind)")

    return haz

