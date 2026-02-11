"""
Build IBTrACS statistical backbone for CCART-India synthetic cyclone engine.

This script:
1. Loads IBTrACS (NetCDF)
2. Filters to North Indian Ocean (NI)
3. Splits storms into Bay of Bengal (BoB) and Arabian Sea (AS) using geography
4. Extracts track points into a clean dataframe
5. Computes:
   - Annual frequency (BoB, AS)
   - Genesis density (BoB, AS)
   - Landfall density (BoB, AS)
   - Translation speed distribution
   - Track archetype clusters
6. Saves processed outputs to data/processed/

Author: Ketan (CCART-India)
"""

import os
import numpy as np
import pandas as pd
import xarray as xr
from pathlib import Path
from sklearn.cluster import KMeans
from scipy.stats import gaussian_kde
from shapely.geometry import Point, LineString
import geopandas as gpd


# ---------------------------------------------------------------------
# PATHS
# ---------------------------------------------------------------------

IBTRACS_FILE = Path(r"C:\CMIP data\cmip6\Climada\Projects\ccart-india\data\IBTrACS.ALL.v04r01.nc")
INDIA_COAST = Path(r"C:\CMIP data\cmip6\Climada\Projects\ccart-india\data\coastl_ind.shp")

OUTPUT_DIR = Path(r"C:\CMIP data\cmip6\Climada\Projects\ccart-india\data\processed")
OUTPUT_DIR.mkdir(exist_ok=True)


# ---------------------------------------------------------------------
# 1. LOAD IBTrACS
# ---------------------------------------------------------------------

def load_ibtracs():
    print("Loading IBTrACS...")
    ds = xr.open_dataset(IBTRACS_FILE, decode_times=False)
    return ds


# ---------------------------------------------------------------------
# 2. FILTER TO NORTH INDIAN OCEAN (NI)
# ---------------------------------------------------------------------

def filter_ni(ds):
    print("Filtering to North Indian Ocean (NI)...")

    # basin is (storm, date_time) with byte strings
    basin = ds["basin"].astype(str)

    # Keep storms where ANY time step has basin == "NI"
    mask = (basin == "NI").any(dim="date_time")

    return ds.where(mask, drop=True)


# ---------------------------------------------------------------------
# 3. SPLIT INTO BoB AND AS USING GEOGRAPHY
# ---------------------------------------------------------------------

def classify_basin(lat, lon):
    """
    Classify a storm into Bay of Bengal (BoB) or Arabian Sea (AS)
    based on its genesis location.
    """
    if 5 <= lat <= 25 and 80 <= lon <= 100:
        return "BoB"
    if 5 <= lat <= 25 and 55 <= lon <= 75:
        return "AS"
    return "Other"


def assign_basin(df):
    print("Assigning storms to BoB or AS...")

    genesis = df.groupby("sid").first()[["lat", "lon"]]

    basin_map = {
        sid: classify_basin(row.lat, row.lon)
        for sid, row in genesis.iterrows()
    }

    df["basin_geo"] = df["sid"].map(basin_map)
    return df


# ---------------------------------------------------------------------
# 4. EXTRACT TRACK POINTS
# ---------------------------------------------------------------------

def extract_track_points(ds):
    print("Extracting track points...")

    df = pd.DataFrame({
        "sid": np.repeat(ds.sid.values, ds.date_time.size),
        "lat": ds.lat.values.flatten(),
        "lon": ds.lon.values.flatten(),
        "vmax": ds.wmo_wind.values.flatten(),
        "pmin": ds.wmo_pres.values.flatten(),
        "time": ds.time.values.flatten()
    })

    df = df.dropna(subset=["lat", "lon"])
    return df


# ---------------------------------------------------------------------
# 5. ANNUAL FREQUENCY
# ---------------------------------------------------------------------

def compute_annual_frequency(df):
    print("Computing annual frequency...")

    if "year" not in df.columns:
        df = df.copy()
        df["year"] = df["sid"].str[:4].astype(int)

    storm_year = df.groupby("sid")["year"].first()
    freq = storm_year.value_counts().sort_index()

    freq_df = freq.reset_index()
    freq_df.columns = ["year", "storm_count"]
    return freq_df



# ---------------------------------------------------------------------
# 5A. YEAR FILTER (REMOVE STORMS BEFORE 1850)
# ---------------------------------------------------------------------

def apply_year_filter(df, min_year=1850, max_year=2023):
    """
    Remove storms whose first valid timestamp corresponds to a year < min_year.
    This filters out malformed storms (e.g., 1840s with invalid timestamps).
    """

    print(f"Applying year filter: keeping storms between {min_year} and {max_year}...")

    df["year"] = df["sid"].str[:4].astype(int)

    # Determine each storm's genesis year
    storm_year = df.groupby("sid")["year"].first()

    # Identify storms to keep
    valid_sids = storm_year[(storm_year >= min_year) & (storm_year <= max_year)].index

    # QC logging
    removed_sids = storm_year[(storm_year < min_year) | (storm_year > max_year)].index
    print(f"Storms removed due to year filter: {len(removed_sids)}")
    if len(removed_sids) > 0:
        print("Removed SIDs:", list(removed_sids))

    # Filter dataframe
    df_filtered = df[df["sid"].isin(valid_sids)].copy()

    print(f"Remaining storms after filter: {df_filtered['sid'].nunique()}")
    return df_filtered

# ---------------------------------------------------------------------
# 6. GENESIS DENSITY
# ---------------------------------------------------------------------

def compute_genesis_density(df, basin_name):
    print(f"Computing genesis density for {basin_name}...")

    subset = df[df["basin_geo"] == basin_name]
    genesis = subset.groupby("sid").first()[["lat", "lon"]].dropna()

    kde = gaussian_kde([genesis["lon"], genesis["lat"]])

    return genesis, kde


# ---------------------------------------------------------------------
# 7. LANDFALL DENSITY
# ---------------------------------------------------------------------

def compute_landfall_density(df, basin_name):
    print(f"Computing landfall density for {basin_name}...")

    coast = gpd.read_file(INDIA_COAST)
    coast_union = coast.union_all()

    landfall_points = []

    for sid, track in df[df["basin_geo"] == basin_name].groupby("sid"):
        pts = [Point(xy) for xy in zip(track.lon, track.lat)]

        # Skip storms with fewer than 2 valid points
        if len(pts) < 2:
            continue

        line = LineString(pts)

        if line.intersects(coast_union):
            pt = line.intersection(coast_union)

            if pt.is_empty:
                continue

            # Case 1: Single point
            if pt.geom_type == "Point":
                landfall_points.append([sid, pt.y, pt.x])

            # Case 2: Multiple points → take the first one
            elif pt.geom_type == "MultiPoint":
                p0 = pt.geoms[0]
                landfall_points.append([sid, p0.y, p0.x])

            # Case 3: LineString or MultiLineString → take the first coordinate
            elif pt.geom_type in ["LineString", "MultiLineString"]:
                coords = list(pt.coords)
                p0 = coords[0]
                landfall_points.append([sid, p0[1], p0[0]])

            # Case 4: GeometryCollection → extract first point-like geometry
            elif pt.geom_type == "GeometryCollection":
                for geom in pt.geoms:
                    if geom.geom_type == "Point":
                        landfall_points.append([sid, geom.y, geom.x])
                        break


    lf_df = pd.DataFrame(landfall_points, columns=["sid", "lat", "lon"])

    if len(lf_df) > 0:
        kde = gaussian_kde([lf_df["lon"], lf_df["lat"]])
    else:
        kde = None

    return lf_df, kde


# ---------------------------------------------------------------------
# 8. TRANSLATION SPEED
# ---------------------------------------------------------------------

def compute_translation_speed(df):
    print("Computing translation speed...")

    speeds = []

    for sid, track in df.groupby("sid"):
        track = track.sort_values("time")
        lat = np.radians(track.lat.values)
        lon = np.radians(track.lon.values)

        dlat = np.diff(lat)
        dlon = np.diff(lon)

        a = np.sin(dlat/2)**2 + np.cos(lat[:-1]) * np.cos(lat[1:]) * np.sin(dlon/2)**2
        c = 2 * np.arcsin(np.sqrt(a))
        dist_km = 6371 * c

        dt_hours = np.diff(track.time.values) / 100  # approx
        speed = dist_km / dt_hours

        speeds.extend(speed)

    return np.array(speeds)


# ---------------------------------------------------------------------
# 9. TRACK CLUSTERS
# ---------------------------------------------------------------------

def compute_track_clusters(df, n_clusters=4):
    print("Clustering tracks...")

    features = []

    for sid, track in df.groupby("sid"):
        track = track.sort_values("time")
        length = np.sum(np.sqrt(np.diff(track.lat)**2 + np.diff(track.lon)**2))
        mean_lat = track.lat.mean()
        mean_lon = track.lon.mean()
        features.append([sid, length, mean_lat, mean_lon])

    feat_df = pd.DataFrame(features, columns=["sid", "length", "mean_lat", "mean_lon"])

    kmeans = KMeans(n_clusters=n_clusters, random_state=42)
    feat_df["cluster"] = kmeans.fit_predict(feat_df[["length", "mean_lat", "mean_lon"]])

    return feat_df


# ---------------------------------------------------------------------
# MAIN
# ---------------------------------------------------------------------

def main():
    ds = load_ibtracs()
    ds = filter_ni(ds)

    df = extract_track_points(ds)
    df["sid"] = df["sid"].str.decode("utf-8")   # decode once, globally
    df = assign_basin(df)

    # ---------------------------------------------------------
    # 1. RAW FREQUENCY BEFORE FILTERING
    # ---------------------------------------------------------
    raw_freq = compute_annual_frequency(df)
    raw_freq.to_csv(OUTPUT_DIR / "ibtracs_frequency_raw.csv", index=False)

    # ---------------------------------------------------------
    # 2. APPLY YEAR FILTER
    # ---------------------------------------------------------
    df = apply_year_filter(df, min_year=1850, max_year=2023)

    # ---------------------------------------------------------
    # 3. FILTERED FREQUENCY
    # ---------------------------------------------------------
    filtered_freq = compute_annual_frequency(df)
    filtered_freq.to_csv(OUTPUT_DIR / "ibtracs_frequency.csv", index=False)

    # ---------------------------------------------------------
    # 4. GENESIS DENSITY (BoB + AS)
    # ---------------------------------------------------------
    for basin in ["BoB", "AS"]:
        genesis_df, _ = compute_genesis_density(df, basin)
        genesis_df.to_csv(OUTPUT_DIR / f"genesis_{basin}.csv", index=False)

    # ---------------------------------------------------------
    # 5. LANDFALL DENSITY (BoB + AS)
    # ---------------------------------------------------------
    for basin in ["BoB", "AS"]:
        lf_df, _ = compute_landfall_density(df, basin)
        lf_df.to_csv(OUTPUT_DIR / f"landfall_{basin}.csv", index=False)

    # ---------------------------------------------------------
    # 6. TRANSLATION SPEEDS
    # ---------------------------------------------------------
    speeds = compute_translation_speed(df)
    pd.DataFrame({"speed_kmh": speeds}).to_csv(
        OUTPUT_DIR / "ibtracs_translation_speeds.csv", index=False
    )

    # ---------------------------------------------------------
    # 7. TRACK CLUSTERS
    # ---------------------------------------------------------
    clusters = compute_track_clusters(df)
    clusters.to_csv(OUTPUT_DIR / "ibtracs_clusters.csv", index=False)

    print("All processing complete.")



if __name__ == "__main__":
    main()
