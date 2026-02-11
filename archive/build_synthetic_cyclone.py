# scripts/build_synthetic_cyclone_cleaned.py

import numpy as np
from sklearn.cluster import DBSCAN
from sklearn.decomposition import PCA
from sklearn.metrics.pairwise import cosine_similarity

from climada.hazard import TCTracks

# ---------------------------------------------------------
# Helper: Resample track to fixed length
# ---------------------------------------------------------

def resample_track(lat, lon, n_points=50):
    idx = np.linspace(0, len(lat) - 1, n_points)
    lat_rs = np.interp(idx, np.arange(len(lat)), lat)
    lon_rs = np.interp(idx, np.arange(len(lon)), lon)
    return lat_rs, lon_rs


# ---------------------------------------------------------
# 1. Load historical tracks from CLEANED HDF5
# ---------------------------------------------------------

def load_historical_tracks_from_clean_file(
    file_path,
    min_wind=35,
    verbose=True,
):
    """
    Load historical cyclone tracks from a pre-cleaned TCTracks HDF5 file.
    Returns a list of per-storm xarray Datasets (no NaNs, variable-length).
    """

    tc_tracks = TCTracks.from_hdf5(file_path)

    tracks = []
    for tr in tc_tracks.data:
        if "max_sustained_wind" in tr:
            if tr["max_sustained_wind"].max() >= min_wind:
                tracks.append(tr)

    if verbose:
        print(f"✅ Loaded {len(tracks)} tracks from cleaned file:")
        print(f"   {file_path}")
        print(f"   Filter: max_sustained_wind ≥ {min_wind} kn")
        if len(tracks) > 0:
            print(f"🌀 Example track name: {tracks[0].attrs.get('name', 'N/A')}")
            print(f"🧭 Example SID: {tracks[0].attrs.get('sid', 'N/A')}")

    return tracks


# ---------------------------------------------------------
# 2. Cluster tracks using DBSCAN (same as before)
# ---------------------------------------------------------

def cluster_tracks_by_path(tracks, eps=8.0, min_samples=3):
    print(">>> USING RESAMPLED + NORMALIZED DBSCAN FUNCTION <<<")

    feature_vectors = []

    for t in tracks:
        lat = t["lat"].values
        lon = t["lon"].values

        # Resample to fixed length
        lat_rs, lon_rs = resample_track(lat, lon, n_points=50)

        # Normalize shape
        lat_rs = (lat_rs - np.mean(lat_rs)) / np.std(lat_rs)
        lon_rs = (lon_rs - np.mean(lon_rs)) / np.std(lon_rs)

        vec = np.concatenate([lat_rs, lon_rs])
        feature_vectors.append(vec)

    X = np.array(feature_vectors)

    db = DBSCAN(eps=eps, min_samples=min_samples).fit(X)

    return db.labels_


# ---------------------------------------------------------
# 3. PCA-based analog refinement (same as before)
# ---------------------------------------------------------

def refine_analogs_pca(tracks, labels, target_cluster=0, top_n=5):
    """
    Select top-N analog tracks within a cluster using PCA + cosine similarity.
    Tracks are first resampled to equal length, so no padding is needed.
    """

    cluster_tracks = [t for i, t in enumerate(tracks) if labels[i] == target_cluster]

    if len(cluster_tracks) < 2:
        raise ValueError(f"Cluster {target_cluster} has fewer than 2 storms — cannot run PCA.")

    feature_vectors = []
    for t in cluster_tracks:
        lat = t["lat"].values
        lon = t["lon"].values

        lat_rs, lon_rs = resample_track(lat, lon, n_points=50)
        vec = np.concatenate([lat_rs, lon_rs])
        feature_vectors.append(vec)

    X = np.array(feature_vectors)

    n_samples = X.shape[0]
    n_components = min(5, n_samples - 1)
    pca = PCA(n_components=n_components)
    reduced = pca.fit_transform(X)

    sim = cosine_similarity(reduced)
    centrality = sim.mean(axis=1)

    idx = np.argsort(centrality)[::-1][:top_n]

    return [cluster_tracks[i] for i in idx]


# ---------------------------------------------------------
# 4. Apply simple climate/intensity modifiers (same as before)
# ---------------------------------------------------------

def apply_climate_modifiers(track, wind_boost=1.0):
    """
    Apply simple intensity modifiers to max_sustained_wind.
    """

    t = track.copy()

    if "max_sustained_wind" in t:
        t["max_sustained_wind"] = t["max_sustained_wind"] * wind_boost

    return t


# ---------------------------------------------------------
# 5. Main synthetic cyclone generator (CLEANED-FILE-based)
# ---------------------------------------------------------

def build_synthetic_cyclone_from_clean_file(
    file_path=r"C:\CMIP data\cmip6\Climada\Projects\ccart-india\data\ni_tracks_climada_1950_2023_cleaned.h5",
    min_wind=35,
    cluster_eps=8.0,
    cluster_min_samples=3,
    target_cluster=None,
    top_n=5,
    wind_boost=1.00,
):
    """
    Generate a synthetic cyclone using:
    - CCART's pre-cleaned NI TCTracks HDF5
    - DBSCAN clustering on track geometry
    - PCA analog refinement
    - optional intensity modifiers
    """

    # 1) Load tracks from cleaned file
    tracks = load_historical_tracks_from_clean_file(
        file_path=file_path,
        min_wind=min_wind,
        verbose=True,
    )

    if len(tracks) == 0:
        raise ValueError("No tracks loaded from cleaned file. Check path or min_wind.")

    # 2) Cluster
    labels = cluster_tracks_by_path(
        tracks,
        eps=cluster_eps,
        min_samples=cluster_min_samples,
    )

    unique, counts = np.unique(labels, return_counts=True)
    print("Cluster sizes:", dict(zip(unique, counts)))

    # 3) Choose cluster
    if target_cluster is None:
        unique, counts = np.unique(labels[labels != -1], return_counts=True)
        cluster_sizes = dict(zip(unique, counts))

        valid_clusters = [c for c, s in cluster_sizes.items() if s >= 5]

        if len(valid_clusters) == 0:
            raise ValueError("No cluster has at least 5 storms. Try reducing eps or min_samples.")

        target_cluster = np.random.choice(valid_clusters)

    print(f"Selected cluster: {target_cluster}")

    # 4) PCA analog refinement
    refined_tracks = refine_analogs_pca(
        tracks,
        labels,
        target_cluster=target_cluster,
        top_n=top_n,
    )

    # 5) Pick one analog
    rand_idx = np.random.randint(len(refined_tracks))
    base_track = refined_tracks[rand_idx]

    print("Selected analog SID:", base_track.attrs.get("sid", "N/A"))
    print("Selected analog name:", base_track.attrs.get("name", "N/A"))

    # 6) Apply intensity modifiers
    synthetic_track = apply_climate_modifiers(
        base_track,
        wind_boost=wind_boost,
    )

    return synthetic_track


if __name__ == "__main__":
    syn = build_synthetic_cyclone_from_clean_file()
    print(syn)
