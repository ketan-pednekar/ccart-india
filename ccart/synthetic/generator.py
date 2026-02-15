"""
CCART Synthetic Cyclone Generator (v2, clean)

- Loads cleaned NI tracks
- Filters for India landfall
- DBSCAN clustering
- PCA refinement
- Optional intensity modifiers
- Returns ONE synthetic track (xarray Dataset)
"""

import pandas as pd
import numpy as np
from sklearn.cluster import DBSCAN
from sklearn.decomposition import PCA
from sklearn.metrics.pairwise import cosine_similarity
from scipy.interpolate import UnivariateSpline

from climada.hazard import TCTracks
import shapely.geometry as geom
import shapely.ops as ops
import geopandas as gpd


# ---------------------------------------------------------
# Load India coastline (mainland only)
# ---------------------------------------------------------
coast = gpd.read_file(
    r"C:\CMIP data\cmip6\Climada\Projects\ccart-india\data\coastl_ind.shp"
).to_crs("EPSG:4326")

bounds = coast.bounds

is_andaman = (
    (bounds.minx > 90) & (bounds.maxx > 90) &
    (bounds.miny < 16) & (bounds.maxy > 6)
)

is_lakshadweep = (
    (bounds.minx > 70) & (bounds.maxx < 76) &
    (bounds.miny > 6) & (bounds.maxy < 18)
)

coast_mainland = coast.loc[~(is_andaman | is_lakshadweep)].copy()
coastline = ops.unary_union(coast_mainland.geometry)
COAST_BUFFER_20KM = coastline.buffer(20 / 111.0)


# ---------------------------------------------------------
# Helper: resample track to fixed length
# ---------------------------------------------------------
def resample_track(lat, lon, n_points=50):
    idx = np.linspace(0, len(lat) - 1, n_points)
    lat_rs = np.interp(idx, np.arange(len(lat)), lat)
    lon_rs = np.interp(idx, np.arange(len(lon)), lon)
    return lat_rs, lon_rs


# ---------------------------------------------------------
# Load cleaned historical tracks
# ---------------------------------------------------------
def load_clean_tracks(file_path, min_wind=35):
    tc = TCTracks.from_hdf5(file_path)
    tracks = []

    for tr in tc.data:
        if "max_sustained_wind" in tr:
            if tr["max_sustained_wind"].max() >= min_wind:
                tracks.append(tr)

    return tracks


# ---------------------------------------------------------
# Landfall filter
# ---------------------------------------------------------
def track_makes_landfall(trk):
    pts = [geom.Point(lon, lat) for lon, lat in zip(trk["lon"].values, trk["lat"].values)]
    line = geom.LineString(pts)

    if not line.intersects(COAST_BUFFER_20KM):
        return False

    if trk["max_sustained_wind"].max() < 40:
        return False

    lat_vals = trk["lat"].values
    if (lat_vals.max() - lat_vals.min()) < 0.5:
        return False

    return True


# ---------------------------------------------------------
# DBSCAN clustering
# ---------------------------------------------------------
def cluster_tracks(tracks, eps=12.0, min_samples=2):
    feats = []

    for t in tracks:
        lat_rs, lon_rs = resample_track(t["lat"].values, t["lon"].values)
        lat_rs = (lat_rs - lat_rs.mean()) / lat_rs.std()
        lon_rs = (lon_rs - lon_rs.mean()) / lon_rs.std()
        feats.append(np.concatenate([lat_rs, lon_rs]))

    X = np.array(feats)
    db = DBSCAN(eps=eps, min_samples=min_samples).fit(X)
    return db.labels_


# ---------------------------------------------------------
# PCA refinement
# ---------------------------------------------------------
def refine_analogs(tracks, labels, target_cluster, top_n=5):
    cluster_tracks = [t for i, t in enumerate(tracks) if labels[i] == target_cluster]

    feats = []
    for t in cluster_tracks:
        lat_rs, lon_rs = resample_track(t["lat"].values, t["lon"].values)
        feats.append(np.concatenate([lat_rs, lon_rs]))

    X = np.array(feats)
    pca = PCA(n_components=min(5, len(X) - 1))
    reduced = pca.fit_transform(X)

    sim = cosine_similarity(reduced)
    centrality = sim.mean(axis=1)

    # Instead of picking the top-N most central, pick N weighted by centrality
    # Convert centrality to non-negative probabilities
    probs = centrality - centrality.min()  # shift so min = 0
    if probs.sum() == 0:
        probs = np.ones_like(probs)
    probs = probs / probs.sum()

    # Weighted random selection
    idx = np.random.choice(len(cluster_tracks), size=top_n, replace=False, p=probs)

    return [cluster_tracks[i] for i in idx]

# ---------------------------------------------------------
# Genesis jitter (safe, ocean-only)
# ---------------------------------------------------------
def jitter_genesis(lat0, lon0, max_jitter_deg=0.3, ocean_mask=None):
    """
    Apply a small random jitter to the genesis point.
    Ensures the new point remains over ocean.
    Returns (new_lat, new_lon, jitter_deg).
    """
    for _ in range(20):
        dist = np.random.uniform(0, max_jitter_deg)
        angle = np.random.uniform(0, 2*np.pi)

        dlat = dist * np.cos(angle)
        dlon = dist * np.sin(angle)

        new_lat = lat0 + dlat
        new_lon = lon0 + dlon

        if ocean_mask is not None:
            pt = geom.Point(new_lon, new_lat)
            if ocean_mask.contains(pt):
                return new_lat, new_lon, dist

        if ocean_mask is None:
            return new_lat, new_lon, dist

    return lat0, lon0, 0.0

# ---------------------------------------------------------
# Track perturbation (Gaussian + spline smoothing)
# ---------------------------------------------------------

def perturb_track(lat, lon, sigma_deg=0.15, smooth_factor=3.0):
    """
    Apply Gaussian perturbation to mid-track points and smooth with spline.
    Genesis and landfall points remain fixed.
    Returns new_lat, new_lon, curvature_index.
    """

    n = len(lat)
    if n < 6:
        return lat, lon, 0.0  # too short to perturb safely

    # Copy arrays
    lat_new = lat.copy()
    lon_new = lon.copy()

    # Indices to perturb (avoid endpoints)
    idx = np.arange(1, n - 1)

    # Gaussian noise
    lat_new[idx] += np.random.normal(0, sigma_deg, size=len(idx))
    lon_new[idx] += np.random.normal(0, sigma_deg, size=len(idx))

    # Spline smoothing
    x = np.arange(n)
    spl_lat = UnivariateSpline(x, lat_new, s=smooth_factor)
    spl_lon = UnivariateSpline(x, lon_new, s=smooth_factor)

    lat_smooth = spl_lat(x)
    lon_smooth = spl_lon(x)

    # Curvature index (simple measure)
    dlat = np.gradient(lat_smooth)
    dlon = np.gradient(lon_smooth)
    curvature = np.mean(np.abs(np.gradient(dlat) + np.gradient(dlon)))

    return lat_smooth, lon_smooth, float(curvature)

def enforce_minimum_spacing(lat, lon, min_dist_km=5):
    """
    Ensures each step in the track moves at least min_dist_km.
    If not, nudge the point slightly along the previous direction.
    """
    lat_new = lat.copy()
    lon_new = lon.copy()

    for i in range(1, len(lat)):
        dlat = lat_new[i] - lat_new[i-1]
        dlon = lon_new[i] - lon_new[i-1]

        # approximate distance in km
        dist = np.sqrt((dlat * 111)**2 + (dlon * 111)**2)

        if dist < min_dist_km:
            # nudge point forward
            factor = min_dist_km / (dist + 1e-6)
            lat_new[i] = lat_new[i-1] + dlat * factor
            lon_new[i] = lon_new[i-1] + dlon * factor

    return lat_new, lon_new


# ---------------------------------------------------------
# Intensity variety (peak, decay, timing shift)
# ---------------------------------------------------------
def intensity_variety(wind, peak_scale_range=(0.9, 1.1), decay_scale_range=(0.9, 1.1), shift_max=2):
    """
    Apply controlled intensity variety:
    - peak multiplier
    - decay multiplier
    - timing shift (± shift_max indices)
    Returns new_wind, metadata_dict.
    """

    wind = wind.copy()
    n = len(wind)

    # 1) Peak multiplier
    peak_scale = np.random.uniform(*peak_scale_range)
    wind *= peak_scale

    # 2) Decay multiplier (post-peak)
    peak_idx = np.argmax(wind)
    decay_scale = np.random.uniform(*decay_scale_range)

    for i in range(peak_idx + 1, n):
        wind[i] = wind[peak_idx] - (wind[peak_idx] - wind[i]) * decay_scale

    # 3) Timing shift
    shift = np.random.randint(-shift_max, shift_max + 1)
    if shift != 0:
        wind = np.roll(wind, shift)

    metadata = {
        "peak_scale": float(peak_scale),
        "decay_scale": float(decay_scale),
        "timing_shift": int(shift),
    }

    return wind, metadata

# ---------------------------------------------------------
# Scenario logic (baseline, warm_sst, high_end)
# ---------------------------------------------------------
def apply_scenario_modifiers(scenario):
    """
    Returns a dictionary of scenario-specific multipliers.
    """

    if scenario == "baseline":
        return {
            "peak_scale": 1.0,
            "decay_scale": 1.0,
            "track_sigma": 1.0,
        }

    if scenario == "warm_sst":
        return {
            "peak_scale": 1.05,     # slightly stronger
            "decay_scale": 0.95,    # slower decay
            "track_sigma": 1.1,     # slightly more wiggle
        }

    if scenario == "high_end":
        return {
            "peak_scale": 1.10,     # stronger peak
            "decay_scale": 0.90,    # much slower decay
            "track_sigma": 1.2,     # more curvature
        }

    # fallback
    return {
        "peak_scale": 1.0,
        "decay_scale": 1.0,
        "track_sigma": 1.0,
    }

# ---------------------------------------------------------
# RMW variety (storm size)
# ---------------------------------------------------------
def rmw_variety(rmw, scale_range=(0.9, 1.1)):
    """
    Apply a multiplicative factor to RMW.
    Returns new_rmw, metadata.
    """
    scale = np.random.uniform(*scale_range)
    return rmw * scale, {"rmw_scale": float(scale)}

# ---------------------------------------------------------
# Translation speed variety
# ---------------------------------------------------------
def translation_speed_variety(lat, lon, speed_scale_range=(0.9, 1.1)):
    """
    Adjust forward speed by scaling time spacing.
    Returns new_lat, new_lon, metadata.
    """
    scale = np.random.uniform(*speed_scale_range)

    # compute dx, dy
    lat_new = lat.copy()
    lon_new = lon.copy()

    for i in range(1, len(lat)):
        lat_new[i] = lat[0] + (lat[i] - lat[0]) * scale
        lon_new[i] = lon[0] + (lon[i] - lon[0]) * scale

    return lat_new, lon_new, {"speed_scale": float(scale)}

# ---------------------------------------------------------
# Rainfall variety (simple multiplier)
# ---------------------------------------------------------
def rainfall_variety(scale_range=(0.8, 1.2)):
    scale = np.random.uniform(*scale_range)
    return {"rainfall_scale": float(scale)}

# ---------------------------------------------------------
# Main synthetic generator
# ---------------------------------------------------------
def build_synthetic_cyclone(
    file_path,
    min_wind=35,
    cluster_eps=12.0,
    cluster_min_samples=2,
    top_n=5,
    wind_boost=1.0,
    scenario="baseline",
):
    tracks = load_clean_tracks(file_path, min_wind=min_wind)

    # India bounding box
    def hits_india(t):
        lon = t["lon"].values
        lat = t["lat"].values
        return ((lon >= 68) & (lon <= 98) & (lat >= 5) & (lat <= 35)).any()

    tracks = [t for t in tracks if hits_india(t) and track_makes_landfall(t)]

    labels = cluster_tracks(tracks, eps=cluster_eps, min_samples=cluster_min_samples)

    # choose largest cluster
    unique, counts = np.unique(labels[labels != -1], return_counts=True)
    target_cluster = unique[np.argmax(counts)]

    refined = refine_analogs(tracks, labels, target_cluster, top_n=top_n)

    # pick one
    base = refined[np.random.randint(len(refined))]

    # apply intensity modifier
    t = base.copy()
    t["max_sustained_wind"] = t["max_sustained_wind"] * wind_boost
    
    # ---------------------------------------------------------
    # NEW: Genesis jitter (safe, ocean-only)
    # ---------------------------------------------------------
    lat0 = float(t["lat"].values[0])
    lon0 = float(t["lon"].values[0])

    new_lat0, new_lon0, jitter_deg = jitter_genesis(
        lat0,
        lon0,
        max_jitter_deg=0.3,
        ocean_mask=coastline  # from top of file
    )

    # apply jitter only to the first point
    lat_arr = t["lat"].values.copy()
    lon_arr = t["lon"].values.copy()

    lat_arr[0] = new_lat0
    lon_arr[0] = new_lon0

    t["lat"] = lat_arr
    t["lon"] = lon_arr

    # store metadata for CSV
    t.attrs["genesis_jitter_deg"] = float(jitter_deg)
    t.attrs["genesis_lat_original"] = lat0
    t.attrs["genesis_lon_original"] = lon0
    t.attrs["genesis_lat_jittered"] = new_lat0
    t.attrs["genesis_lon_jittered"] = new_lon0

    # ---------------------------------------------------------
    # NEW: Scenario logic
    # ---------------------------------------------------------
    scen = apply_scenario_modifiers(scenario)

    # adjust track perturbation sigma
    track_sigma = 0.15 * scen["track_sigma"]

    # adjust intensity variety multipliers
    peak_range = (0.9 * scen["peak_scale"], 1.1 * scen["peak_scale"])
    decay_range = (0.9 * scen["decay_scale"], 1.1 * scen["decay_scale"])

    # ---------------------------------------------------------
    # NEW: Track perturbation (Gaussian + spline)
    # ---------------------------------------------------------
    lat_arr = t["lat"].values.copy()
    lon_arr = t["lon"].values.copy()

    # ---------------------------------------------------------
    # NEW: Track perturbation (Gaussian + spline, scenario-aware)
    # ---------------------------------------------------------
    lat_pert, lon_pert, curvature_idx = perturb_track(
        lat_arr,
        lon_arr,
        sigma_deg=track_sigma,   # <-- scenario-adjusted
        smooth_factor=3.0
    )

    # --- NEW FIX: enforce minimum spacing to avoid CLIMADA crashes ---
    lat_pert, lon_pert = enforce_minimum_spacing(lat_pert, lon_pert, min_dist_km=5)

    t["lat"] = lat_pert
    t["lon"] = lon_pert


    # store metadata
    t.attrs["track_sigma_deg"] = track_sigma
    t.attrs["track_curvature_index"] = curvature_idx
    
    #----------------------------------
    # --- Translation speed variety ---
    #-----------------------------------
    lat_ts, lon_ts, ts_meta = translation_speed_variety(
        t["lat"].values,
        t["lon"].values,
        speed_scale_range=(0.9, 1.1)
    )

    t["lat"] = lat_ts
    t["lon"] = lon_ts
    t.attrs["translation_speed_scale"] = ts_meta["speed_scale"]

    # ---------------------------------------------------------
    # NEW: Intensity variety (peak, decay, timing shift)
    # ---------------------------------------------------------
    #-----------------------------------------------
    # --- FIX: ensure wind has a meaningful peak ---
    #-----------------------------------------------

    wind_arr = t["max_sustained_wind"].values.copy()

    if np.max(wind_arr) - np.min(wind_arr) < 5:
        peak_idx = len(wind_arr) // 2
        wind_arr[peak_idx] = wind_arr[peak_idx] + 20  # enforce peak

    # ---------------------------------------------------------
    # NEW: Intensity variety (scenario-aware)
    # ---------------------------------------------------------
   
    wind_new, inten_meta = intensity_variety(
        wind_arr,
        peak_scale_range=peak_range,   # <-- scenario-adjusted
        decay_scale_range=decay_range, # <-- scenario-adjusted
        shift_max=2
    )

    # --- FIX: drop old variable before overwriting ---
    if "max_sustained_wind" in t:
        t = t.drop_vars("max_sustained_wind")

    # --- assign with correct dimension ---
    t["max_sustained_wind"] = (("time"), wind_new)


    # store metadata
    t.attrs["intensity_peak_scale"] = inten_meta["peak_scale"]
    t.attrs["intensity_decay_scale"] = inten_meta["decay_scale"]
    t.attrs["intensity_timing_shift"] = inten_meta["timing_shift"]

    # store scenario metadata
    t.attrs["scenario"] = scenario
    t.attrs["scenario_peak_scale"] = scen["peak_scale"]
    t.attrs["scenario_decay_scale"] = scen["decay_scale"]
    t.attrs["scenario_track_sigma"] = scen["track_sigma"]

    #-------------------------
    # --- RMW variety ---
    #-------------------------
    if "radius_max_wind" in t:
        rmw_arr = t["radius_max_wind"].values.copy()
        rmw_new, rmw_meta = rmw_variety(rmw_arr, scale_range=(0.9, 1.1))
        t["radius_max_wind"] = (("time"), rmw_new)
        t.attrs["rmw_scale"] = rmw_meta["rmw_scale"]


    #---------------------------
    # --- Rainfall variety ---
    #----------------------------
    rain_meta = rainfall_variety(scale_range=(0.8, 1.2))
    t.attrs["rainfall_scale"] = rain_meta["rainfall_scale"]

    #-------------------------------------------------
    # --- FIX 1: ensure RMW exists and is non-zero ---
    #-------------------------------------------------
    if "radius_max_wind" in t:
        rmw = t["radius_max_wind"].values
    else:
        rmw = None

    if rmw is None or np.all(rmw == 0):
        rmw_default = np.full(len(t["time"]), 30.0)  # 30 km default
        t["radius_max_wind"] = (("time"), rmw_default)
        t.attrs["rmw_scale"] = 1.0

    # --- FIX: ensure radius_oci exists and is physically valid ---
    if "radius_oci" in t:
        oci = np.asarray(t["radius_oci"].values, dtype=float).reshape(-1)
        # Replace zeros or negative values with a safe default (e.g., 150 km)
        oci[oci <= 0] = 150.0
        # Smooth unrealistic jumps
        oci = np.clip(oci, 50.0, 300.0)
        t["radius_oci"] = (("time",), oci)
    else:
        # Provide a default if missing
        t["radius_oci"] = (("time",), np.full(len(t["time"]), 150.0))

    #--------------------------------------------------
    # --- FIX 2: ensure pressure delta is positive ---
    #--------------------------------------------------
    cp = t["central_pressure"].values
    ep = t["environmental_pressure"].values

    pdelta = ep - cp
    pdelta[pdelta < 1.0] = 1.0

    #-------------------------------------------------
    # Recompute central pressure to enforce ΔP >= 1
    #---------------------------------------------------
    t["central_pressure"] = (("time"), ep - pdelta)
 
#--------------------------------------------------
# just before `return t` in build_synthetic_cyclone
#--------------------------------------------------
    for var in ["radius_max_wind", "central_pressure", "environmental_pressure", "max_sustained_wind"]:
        if var in t:
            arr = np.asarray(t[var].values).reshape(-1)  # ensure 1D
            t[var] = (("time",), arr)

    print("rmax", t["radius_max_wind"].shape)
    print("cp", t["central_pressure"].shape)
    print("ep", t["environmental_pressure"].shape)

    return t

