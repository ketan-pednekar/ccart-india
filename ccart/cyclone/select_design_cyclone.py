import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import xarray as xr
import pyarrow.parquet as pq

from shapely.geometry import box
from climada.hazard import TCTracks, TropCyclone, Centroids
from ccart.hazard_simulated_v2 import build_hazard_from_tc_tracks


# ---------------------------------------------------------
# Step 1 — Load the cyclone master catalogue
# ---------------------------------------------------------
table = pq.read_table(
    r"C:\CMIP data\cmip6\Climada\Projects\ccart-india\ccart\cyclone\ccart_cyclone_master.parquet"
)
df = table.to_pandas()

print("Master shape:", df.shape)
print(df.columns)

# ---------------------------------------------------------
# Step 2 — Filter Vizag-relevant storms
# ---------------------------------------------------------
vizag_df = df[df["vizag_relevant"] == True]
print("Number of Vizag-relevant storms:", vizag_df.shape[0])

print(vizag_df[
    ["scenario", "run", "sid", "storm_name", "max_intensity",
     "closest_distance_km", "landfall_distance_km", "landfall_angle_deg"]
])

# ---------------------------------------------------------
# Step 3 — Identify top candidates
# ---------------------------------------------------------
# Sort by closest distance (ascending)
candidates = vizag_df.sort_values("closest_distance_km")

# Pick top 4 variants of the main storm
top_variants = candidates[candidates["sid"] == "2003345N05092"].head(4)

# Pick LAILA if present
laila = candidates[candidates["storm_name"] == "LAILA"]

# Combine
plot_set = pd.concat([top_variants, laila], ignore_index=True)

print("\nSelected storms for plotting:")
print(plot_set[
    ["scenario", "run", "sid", "storm_name", "closest_distance_km"]
])

# ---------------------------------------------------------
# Step 4 — Plot tracks for comparison
# ---------------------------------------------------------
plt.figure(figsize=(8, 8))

for idx, row in plot_set.iterrows():
    track = row["track"]
    lats = [p[0] for p in track]
    lons = [p[1] for p in track]
    label = f"{row['storm_name']} ({row['scenario']}, {row['run']})"
    plt.plot(lons, lats, label=label)

# Vizag marker
plt.scatter([83.29], [17.69], color="red", s=50, label="Vizag")

plt.xlabel("Longitude")
plt.ylabel("Latitude")
plt.title("Candidate Design Cyclone Tracks — Vizag Region")
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.show()


laila_track = df[df["storm_name"] == "LAILA"].iloc[0]["track"]
print("LAILA track length:", len(laila_track))
print(laila_track[:10])

plt.figure(figsize=(8,8))
lats = [p[0] for p in laila_track]
lons = [p[1] for p in laila_track]
plt.plot(lons, lats)
plt.scatter([83.29], [17.69], color="red")
plt.title("LAILA Track")
plt.grid(True)
plt.show()

# Step A — Filter Vizag-relevant storms
candidates = df[df["vizag_relevant"] == True].copy()

# Step B — Remove storms with incomplete tracks
candidates["track_length"] = candidates["track"].apply(len)
candidates = candidates[candidates["track_length"] > 10]

# Step C — Apply physical filters
candidates = candidates[
    (candidates["max_intensity"] > 30) &
    (candidates["closest_distance_km"] < 150) &
    (candidates["landfall_angle_deg"] > 60) &
    (candidates["landfall_angle_deg"] < 90)
]

# Step D — Select the best candidate
design_storm = candidates.sort_values("closest_distance_km").iloc[0]

print("Selected design cyclone:")
print(design_storm[["scenario", "run", "sid", "storm_name",
                    "max_intensity", "closest_distance_km",
                    "landfall_angle_deg"]])


# ---------------------------------------------------------
# Step 5 — Extract track for the selected design cyclone
# ---------------------------------------------------------
design = design_storm  # from your selection logic

track = design["track"]
print("Design cyclone track length:", len(track))

lats = [p[0] for p in track]
lons = [p[1] for p in track]
ints = [p[2] for p in track]

print("First 5 points:")
for p in track[:5]:
    print(p)

# Build a synthetic datetime axis (1 hour per step)
start_time = pd.Timestamp("2000-01-01 00:00:00")
times = start_time + pd.to_timedelta(np.arange(len(lats)), unit="h")

ds = xr.Dataset(
    {
        "lat": ("time", lats),
        "lon": ("time", lons),
        "max_sustained_wind": ("time", ints),
        "radius_max_wind": ("time", np.full(len(lats), 30.0)),
        "radius_oci": ("time", np.full(len(lats), 150.0)),
        "central_pressure": ("time", np.full(len(lats), 970.0)),
        "environmental_pressure": ("time", np.full(len(lats), 1010.0)),
        "time_step": ("time", np.full(len(lats), 1.0)),
    },
    coords={"time": times},   # MUST be datetime
    attrs={
        "sid": design["sid"],
        "name": design["storm_name"],
        "orig_event_flag": False,
        "category": 0,   # REQUIRED BY CLIMADA
    },
)

# Add required CLIMADA basin variable
ds["basin"] = (("time",), np.array(["NI"] * len(lats)))

# Required CLIMADA units
ds.attrs["lat_unit"] = "degree"
ds.attrs["lon_unit"] = "degree"
ds.attrs["max_sustained_wind_unit"] = "kn"
ds.attrs["radius_max_wind_unit"] = "km"
ds.attrs["radius_oci_unit"] = "km"
ds.attrs["central_pressure_unit"] = "hPa"
ds.attrs["environmental_pressure_unit"] = "hPa"
ds.attrs["time_step_unit"] = "hour"

# Build TCTracks
tc_tracks = TCTracks()
tc_tracks.data = [ds]


import matplotlib.pyplot as plt

# 1) All tracks (faint grey)
plt.figure(figsize=(8, 8))

for idx, row in df.iterrows():
    track = row["track"]
    lats = [p[0] for p in track]
    lons = [p[1] for p in track]
    plt.plot(lons, lats, color="lightgrey", linewidth=0.5, zorder=1)

# 2) Vizag-relevant storms (blue)
vizag_df = df[df["vizag_relevant"] == True].copy()

for idx, row in vizag_df.iterrows():
    track = row["track"]
    lats = [p[0] for p in track]
    lons = [p[1] for p in track]
    plt.plot(lons, lats, color="steelblue", linewidth=1.0, alpha=0.8, zorder=2)

# 3) Design cyclone (red, bold)
design = design_storm  # from your selection logic
track = design["track"]
lats = [p[0] for p in track]
lons = [p[1] for p in track]
plt.plot(lons, lats, color="crimson", linewidth=2.0, label="Design cyclone", zorder=3)

# 4) Vizag marker
plt.scatter([83.29], [17.69], color="black", s=40, marker="x", label="Vizag Port", zorder=4)

plt.xlabel("Longitude")
plt.ylabel("Latitude")
plt.title("From 1100 Synthetic Cyclones to 1 Design Cyclone — Vizag Region")
plt.legend()
plt.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig("slide3_design_cyclone_selection.png", dpi=300)
plt.show()


plt.figure(figsize=(8, 8))

# Plot only Vizag-relevant candidates (light blue)
for idx, row in vizag_df.iterrows():
    track = row["track"]
    lats = [p[0] for p in track]
    lons = [p[1] for p in track]
    plt.plot(lons, lats, color="lightblue", linewidth=0.8, alpha=0.7)

# Highlight design cyclone
track = design["track"]
lats = [p[0] for p in track]
lons = [p[1] for p in track]
plt.plot(lons, lats, color="crimson", linewidth=2.0, label="Design cyclone")

plt.scatter([83.29], [17.69], color="black", s=40, marker="x", label="Vizag Port")

plt.xlabel("Longitude")
plt.ylabel("Latitude")
plt.title("Physically Filtered Candidates and Selected Design Cyclone")
plt.legend()
plt.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig("slide3_candidates_vs_design.png", dpi=300)
plt.show()


# ---------------------------------------------------------
# Step 5.5 — Build hazard using CCART v2 engine
# ---------------------------------------------------------

thaz = build_hazard_from_tc_tracks(tc_tracks)

print("DEBUG: thaz type:", type(thaz))
print("DEBUG: total centroids:", thaz.centroids.size)

# ---------------------------------------------------------
# Step 6 — Clip hazard to Vizag bounding box (manual centroid slicing)
# ---------------------------------------------------------

vizag_lat_min = 17.4
vizag_lat_max = 18.0
vizag_lon_min = 83.0
vizag_lon_max = 83.6

mask = (
    (thaz.centroids.lat >= vizag_lat_min) &
    (thaz.centroids.lat <= vizag_lat_max) &
    (thaz.centroids.lon >= vizag_lon_min) &
    (thaz.centroids.lon <= vizag_lon_max)
)

print("Centroids in mask:", mask.sum())

if mask.sum() == 0:
    raise ValueError("ERROR: No centroids found in Vizag bounding box.")

indices = np.where(mask)[0]

# --- Manual centroid + intensity slicing ---
cent_clip = Centroids(
    lat=thaz.centroids.lat[indices],
    lon=thaz.centroids.lon[indices],
    crs=thaz.centroids.crs,
)

intensity_clip = thaz.intensity[:, indices]
intensity_thres_clip = thaz.intensity_thres[:, indices]
fraction_clip = thaz.fraction[:, indices]

# Build new hazard object
thaz_clip = TropCyclone()
thaz_clip.event_id = thaz.event_id.copy()

# Optional attributes (copy only if present)
if hasattr(thaz, "event_name"):
    thaz_clip.event_name = thaz.event_name.copy()
if hasattr(thaz, "frequency"):
    thaz_clip.frequency = thaz.frequency.copy()

thaz_clip.centroids = cent_clip
thaz_clip.intensity = intensity_clip
thaz_clip.intensity_thres = intensity_thres_clip
thaz_clip.fraction = fraction_clip
thaz_clip.units = thaz.units

print("Clipped centroids:", thaz_clip.centroids.size)
print("Max intensity (clipped):", float(thaz_clip.intensity.max()))

thaz_clip.check()
thaz_clip.write_hdf5("vizag_design_cyclone_hazard.h5")
print("Saved clipped hazard to vizag_design_cyclone_hazard.h5")
