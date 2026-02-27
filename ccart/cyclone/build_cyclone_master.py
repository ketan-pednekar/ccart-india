import pandas as pd
import os
import numpy as np

#---------------------------------------------
# Step 1 — Load master summary
#---------------------------------------------
master = pd.read_csv(
    r"C:\CMIP data\cmip6\Climada\Projects\ccart-india\outputs\synthetic_runs_multi\master_summary.csv"
)

#---------------------------------------------
# Step 2 — Load track for each storm
#---------------------------------------------

def load_track(output_dir):
    candidates = ["track.csv", "track_points.csv", "track.geojson"]
    for fname in candidates:
        fpath = os.path.join(output_dir, fname)
        if os.path.exists(fpath):
            df = pd.read_csv(fpath)
            return df
    return None

#--------------------------------------------------
# Step 3 — Convert track dataframe → list of tuples
#--------------------------------------------------

def df_to_track_list(track_df):
    if track_df is None:
        return None
    
    # Try common intensity column names
    for col in ["vmax", "vmax_ms", "wind", "wind_ms", "vmax_10m", "max_sustained_wind"]:
        if col in track_df.columns:
            intensity_col = col
            break
    else:
        raise KeyError(f"No intensity column found in track file. Columns: {track_df.columns}")
    
    return list(zip(track_df["lat"], track_df["lon"], track_df[intensity_col]))

#------------------------------------------------------
# Step 4 — Compute cyclone metrics once and store them
#------------------------------------------------------

VIZAG_LAT = 17.6900
VIZAG_LON = 83.2900

def haversine(lat1, lon1, lat2, lon2):
    R = 6371
    dlat = np.radians(lat2 - lat1)
    dlon = np.radians(lon2 - lon1)
    a = (np.sin(dlat/2)**2 +
         np.cos(np.radians(lat1)) *
         np.cos(np.radians(lat2)) *
         np.sin(dlon/2)**2)
    return 2 * R * np.arcsin(np.sqrt(a))

# Compute closest approach
def compute_closest_distance(track):
    if track is None:
        return None
    dists = [haversine(lat, lon, VIZAG_LAT, VIZAG_LON) for lat, lon, vmax in track]
    return min(dists)

# Compute landfall distance
def compute_landfall_distance(track):
    if track is None or len(track) == 0:
        return None
    landfall_lat, landfall_lon, _ = track[-1]
    return haversine(landfall_lat, landfall_lon, VIZAG_LAT, VIZAG_LON)

# Compute landfall angle
def compute_landfall_angle(track):
    if track is None or len(track) < 2:
        return None
    (lat1, lon1, _), (lat2, lon2, _) = track[-2], track[-1]
    dy = lat2 - lat1
    dx = lon2 - lon1
    return np.degrees(np.arctan2(dy, dx))

#------------------------------------------------------
# Step 5 — Build the true master file
#------------------------------------------------------

tracks = []
track_lists = []
closest_dists = []
landfall_dists = []
angles = []

for i, row in master.iterrows():
    tdf = load_track(row["output_dir"])
    tlist = df_to_track_list(tdf)
    
    tracks.append(tdf)
    track_lists.append(tlist)
    closest_dists.append(compute_closest_distance(tlist))
    landfall_dists.append(compute_landfall_distance(tlist))   # FIXED
    angles.append(compute_landfall_angle(tlist))

master["track"] = track_lists
master["closest_distance_km"] = closest_dists
master["landfall_distance_km"] = landfall_dists
master["landfall_angle_deg"] = angles

#------------------------------------------------------
# Step 6 — Add Vizag relevance flag
#------------------------------------------------------

def is_vizag_relevant(row):
    return (
        row["closest_distance_km"] <= 200 and
        row["landfall_distance_km"] <= 150 and
        row["max_intensity"] >= 30 and
        abs(row["landfall_angle_deg"] - 90) <= 45
    )

master["vizag_relevant"] = master.apply(is_vizag_relevant, axis=1)


#------------------------------------------------------
# Step 7 — Save the true master file
#------------------------------------------------------

master.to_parquet(
    r"C:\CMIP data\cmip6\Climada\Projects\ccart-india\ccart\cyclone\ccart_cyclone_master.parquet",
    index=False
)



