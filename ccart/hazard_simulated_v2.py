import numpy as np
from scipy import sparse
from climada.hazard import Centroids, TropCyclone


def build_hazard_from_tc_tracks(
    tc_tracks,
    corridor_deg: float = 1.5,
    grid_res_deg: float = 0.025,
    min_peak_wind_kn: float = 20.0,
    verbose: bool = True,
):
    if tc_tracks.size != 1:
        raise ValueError("Expected TCTracks with exactly one storm.")

    trk = tc_tracks.data[0]

    # ---------------------------------------------------------
    # 0. FINAL SAFETY: ensure all key vars are 1D ("time",)
    # ---------------------------------------------------------
    for var in [
        "lat",
        "lon",
        "radius_max_wind",
        "radius_oci",
        "central_pressure",
        "environmental_pressure",
        "time_step",
        "max_sustained_wind",
    ]:
        if var in trk:
            arr = np.asarray(trk[var].values, dtype=float).reshape(-1)
            trk[var] = (("time",), arr)

    # RMW fallback if zero
    if "radius_max_wind" in trk:
        rmw = np.asarray(trk["radius_max_wind"].values, dtype=float).reshape(-1)
        if np.all(rmw == 0):
            print("DEBUG: RMW was zero inside TCTracks → applying fallback")
            trk["radius_max_wind"] = (("time",), np.full_like(rmw, 30.0))

    # radius_oci sanity
    if "radius_oci" in trk:
        oci = np.asarray(trk["radius_oci"].values, dtype=float).reshape(-1)
        oci[oci <= 0] = 150.0
        oci = np.clip(oci, 50.0, 300.0)
        trk["radius_oci"] = (("time",), oci)
    else:
        trk["radius_oci"] = (("time",), np.full(len(trk["time"]), 150.0))

    # pressure delta sanity
    cp = np.asarray(trk["central_pressure"].values, dtype=float).reshape(-1)
    ep = np.asarray(trk["environmental_pressure"].values, dtype=float).reshape(-1)
    pdelta = ep - cp
    pdelta[pdelta < 1.0] = 1.0
    trk["central_pressure"] = (("time",), ep - pdelta)

    # ---------------------------------------------------------
    # DEBUG: print shapes
    # ---------------------------------------------------------
    print("DEBUG shapes in TCTracks:")
    for var in ["radius_max_wind", "radius_oci",
                "central_pressure", "environmental_pressure",
                "max_sustained_wind"]:
        if var in trk:
            print(var, np.asarray(trk[var]).shape)

    # ---------------------------------------------------------
    # Basic diagnostics
    # ---------------------------------------------------------
    trk_lats = np.asarray(trk["lat"].values, dtype=float)
    trk_lons = np.asarray(trk["lon"].values, dtype=float)
    peak_wind = float(trk["max_sustained_wind"].max())

    if verbose:
        print(">>> build_hazard_from_tc_tracks v2.2")
        print(f"  Track SID: {trk.attrs.get('sid', 'N/A')}")
        print(f"  Track name: {trk.attrs.get('name', 'N/A')}")
        print(f"  Peak max_sustained_wind: {peak_wind:.1f} kn")

    # ---------------------------------------------------------
    # Weak storm → zero-intensity hazard
    # ---------------------------------------------------------
    if peak_wind < min_peak_wind_kn:
        lat_min = trk_lats.min() - corridor_deg
        lat_max = trk_lats.max() + corridor_deg
        lon_min = trk_lons.min() - corridor_deg
        lon_max = trk_lons.max() + corridor_deg

        lats = np.arange(lat_min, lat_max + grid_res_deg, grid_res_deg)
        lons = np.arange(lon_min, lon_max + grid_res_deg, grid_res_deg)
        lon_grid, lat_grid = np.meshgrid(lons, lats)

        cent = Centroids(lat=lat_grid.ravel(), lon=lon_grid.ravel(), crs="EPSG:4326")

        haz = TropCyclone.from_tracks(tc_tracks, centroids=cent)
        haz.intensity = sparse.csr_matrix(haz.intensity.shape)
        haz.intensity_thres = haz.intensity.copy()
        haz.fraction = sparse.csr_matrix(haz.fraction)
        haz.check()
        return haz

    # ---------------------------------------------------------
    # Normal storm → tight bounding box (±1°)
    # ---------------------------------------------------------
    lat_min = trk_lats.min() - 1.0
    lat_max = trk_lats.max() + 1.0
    lon_min = trk_lons.min() - 1.0
    lon_max = trk_lons.max() + 1.0

    lats = np.arange(lat_min, lat_max + grid_res_deg, grid_res_deg)
    lons = np.arange(lon_min, lon_max + grid_res_deg, grid_res_deg)
    lon_grid, lat_grid = np.meshgrid(lons, lats)

    cent = Centroids(lat=lat_grid.ravel(), lon=lon_grid.ravel(), crs="EPSG:4326")

    if verbose:
        print("  Centroid grid:")
        print(f"    lat: {lat_min:.2f} → {lat_max:.2f} (n={len(lats)})")
        print(f"    lon: {lon_min:.2f} → {lon_max:.2f} (n={len(lons)})")
        print(f"    total centroids: {len(cent.lat)}")

    haz = TropCyclone.from_tracks(tc_tracks, centroids=cent)

    intensity_dense = haz.intensity.toarray()
    intensity_dense[intensity_dense < 0] = 0
    haz.intensity = sparse.csr_matrix(intensity_dense)
    haz.intensity_thres = haz.intensity.copy()
    haz.fraction = sparse.csr_matrix(haz.fraction)
    haz.check()

    print("\n=== DEBUG: Hazard centroid spacing ===")
    print("Mean lat spacing:", np.mean(np.diff(np.unique(hazard.centroids.lat))))
    print("Mean lon spacing:", np.mean(np.diff(np.unique(hazard.centroids.lon))))


    return haz
