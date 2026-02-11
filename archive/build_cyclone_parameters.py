"""
Generate cyclone_parameters.csv for CCART-India v2.0
----------------------------------------------------

Inputs:
- IBTrACS dataset (CSV or NetCDF)
- CLIMADA TC tracks (already processed)
- master_district_loss.csv (your v1.3 master file)
- cyclone_metadata.csv (for DLNA totals)

Output:
- cyclone_parameters.csv (machine-generated event catalogue)
"""

import pandas as pd
import numpy as np
import xarray as xr

from climada.hazard.tc_tracks import TCTracks
from climada.hazard import TropCyclone
from climada.hazard import Centroids

# ---------------------------------------------------------
# 1. Load core datasets
# ---------------------------------------------------------

master = pd.read_csv("data/district_relationships_master_v1_3_rebuild.csv")
meta = pd.read_csv("data/cyclone_metadata.csv")
templates = pd.read_csv("data/cyclone_templates_v1_3.csv")

IBTRACS_PATH = "data/IBTrACS.ALL.v04r01.nc"


# ---------------------------------------------------------
# 2. Helper functions
# ---------------------------------------------------------

def get_ibtracs_track(sid):
    """
    Build a TCTracks object using the same structure as
    TCTracks.from_ibtracs_netcdf(provider='usa') in your CLIMADA version,
    with RMW/OCI derived from v1.3 template labels.
    """
    try:
        ds = xr.open_dataset(IBTRACS_PATH)

        # ---------------------------------------------------------
        # 1. Locate storm in IBTrACS
        # ---------------------------------------------------------
        sids = ds["sid"].values.astype(str)
        idx = np.where(sids == sid)[0]
        if len(idx) == 0:
            print(f"SID {sid} not found in IBTrACS.")
            return None
        idx = idx[0]

        storm = ds.isel(storm=idx)

        # Extract arrays
        time = pd.to_datetime(storm["iso_time"].values.astype(str))
        lat = storm["usa_lat"].values
        lon = storm["usa_lon"].values
        wind = storm["usa_wind"].values
        pres = storm["usa_pres"].values

        # Drop invalid rows
        mask = (~np.isnan(lat)) & (~np.isnan(lon)) & (~np.isnan(wind))
        time = time[mask]
        lat = lat[mask]
        lon = lon[mask]
        wind = wind[mask]
        pres = pres[mask]

        if len(time) == 0:
            print(f"SID {sid} has no valid USA rows.")
            return None

        # ---------------------------------------------------------
        # 2. Get template label from v1.3 and map to RMW / OCI
        # ---------------------------------------------------------
        df_sid = templates[templates.sid == sid]
        if not df_sid.empty:
            template = df_sid.template_label.iloc[0]
        else:
            template = "unknown"

        if template == "A":
            rmw = 100.0
            oci = 450.0
        elif template == "B":
            rmw = 80.0
            oci = 400.0
        elif template == "C":
            rmw = 60.0
            oci = 350.0
        elif template == "D":
            rmw = 40.0
            oci = 300.0
        else:  # E or unknown
            rmw = 30.0
            oci = 250.0

        # ---------------------------------------------------------
        # 3. Stabilise pressure so CLIMADA has a usable gradient
        # ---------------------------------------------------------
        pres = np.where(np.isnan(pres), 1000.0, pres)
        pres = np.minimum(pres, 990.0)  # enforce minimum pressure drop

        # ---------------------------------------------------------
        # 4. Build xarray Dataset (CLIMADA-compatible)
        # ---------------------------------------------------------
        ds_xr = xr.Dataset(
            data_vars={
                "lat": (["time"], lat),
                "lon": (["time"], lon),
                "max_sustained_wind": (["time"], wind),
                "central_pressure": (["time"], pres),

                # Template-based storm size
                "radius_max_wind": (["time"], np.full_like(wind, rmw)),
                "radius_oci": (["time"], np.full_like(wind, oci)),

                # Required fields
                "environmental_pressure": (["time"], np.full_like(wind, 1015.0)),
                "time_step": (["time"], np.full_like(wind, 6.0)),
                "basin": (["time"], np.array(["NI"] * len(wind))),
            },
            coords={"time": time},
            attrs={
                "sid": sid,
                "name": sid,
                "category": 3,
                "orig_event_flag": True,
                "data_provider": "ibtracs_manual",
                "id_no": float(sid.replace("N", "").replace("S", "")),

                # Required units
                "max_sustained_wind_unit": "kn",
                "central_pressure_unit": "mb",
                }

        )

        # ---------------------------------------------------------
        # 5. Wrap in TCTracks object
        # ---------------------------------------------------------
        tc = TCTracks()
        tc.data = [ds_xr]

        tc.sid = sid
        tc.name = sid
        tc.basin = "NI"
        tc.orig_event_flag = True
        tc.category = 3
        tc.date = [time[0]]
        tc.event_id = [0]
        tc.frequency = [1.0]
        tc.meta = {
            "data_provider": "ibtracs_manual",
            "template_label": template
        }

        return tc

    except Exception as e:
        print("\n\n================ REAL ERROR BELOW ================\n")
        raise


def compute_landfall_properties(track):
    """
    Compute landfall properties from a TCTracks object.
    Uses max wind point as proxy for landfall.
    """
    if track is None or track.data is None or len(track.data) == 0:
        return {
            "landfall_lat": np.nan,
            "landfall_lon": np.nan,
            "vmax_landfall": np.nan,
            "pmin_landfall": np.nan,
        }

    ds = track.data[0]  # xarray Dataset

    # Ensure required variables exist
    if not all(v in ds for v in ["lat", "lon", "max_sustained_wind", "central_pressure"]):
        return {
            "landfall_lat": np.nan,
            "landfall_lon": np.nan,
            "vmax_landfall": np.nan,
            "pmin_landfall": np.nan,
        }

    df = pd.DataFrame({
        "lat": ds["lat"].values,
        "lon": ds["lon"].values,
        "wind": ds["max_sustained_wind"].values,
        "pres": ds["central_pressure"].values,
    }).dropna(subset=["wind"])

    if df.empty:
        return {
            "landfall_lat": np.nan,
            "landfall_lon": np.nan,
            "vmax_landfall": np.nan,
            "pmin_landfall": np.nan,
        }

    idx = df["wind"].idxmax()

    return {
        "landfall_lat": df.loc[idx, "lat"],
        "landfall_lon": df.loc[idx, "lon"],
        "vmax_landfall": df.loc[idx, "wind"],
        "pmin_landfall": df.loc[idx, "pres"],
    }



def compute_track_metrics(track):
    """Compute track length, translation speed, curvature, etc. Placeholder for now."""
    return {
        "track_length_km": np.nan,
        "translation_speed": np.nan,
        "track_archetype": "unknown",
    }


def compute_climada_footprint(track):
    """
    Compute CLIMADA wind footprint metrics from a fully constructed TCTracks object.
    Uses a fixed India-wide centroid grid instead of the storm track as centroids.
    """

    # ---------------------------------------------------------
    # Validate track
    # ---------------------------------------------------------
    if track is None or track.data is None or len(track.data) == 0:
        return {
            "rmw_km": np.nan,
            "wind_footprint_area_km2": np.nan,
            "districts_affected": np.nan,
            "litpop_exposed": np.nan,
        }

    ds = track.data[0]  # xarray Dataset

    if not all(v in ds for v in ["lat", "lon"]):
        return {
            "rmw_km": np.nan,
            "wind_footprint_area_km2": np.nan,
            "districts_affected": np.nan,
            "litpop_exposed": np.nan,
        }

    # ---------------------------------------------------------
    # Build India-wide centroid grid (same as troubleshooting)
    # ---------------------------------------------------------
    lat_vec = np.linspace(5.0, 35.0, 301)   # ~0.1° resolution
    lon_vec = np.linspace(65.0, 100.0, 351) # ~0.1° resolution
    lon_grid, lat_grid = np.meshgrid(lon_vec, lat_vec)

    cent = Centroids.from_lat_lon(
        lat_grid.ravel(),
        lon_grid.ravel()
    )

    # ---------------------------------------------------------
    # Run CLIMADA hazard engine (NO try/except — show real error)
    # ---------------------------------------------------------
    print(f"\nRunning CLIMADA for SID {track.sid} ...")
    haz = TropCyclone.from_tracks(track, centroids=cent)

    # ---------------------------------------------------------
    # Validate hazard
    # ---------------------------------------------------------
    if haz.intensity is None or haz.intensity.size == 0:
        return {
            "rmw_km": np.nan,
            "wind_footprint_area_km2": np.nan,
            "districts_affected": np.nan,
            "litpop_exposed": np.nan,
        }

    # Identify affected cells (any non-zero intensity)
    affected = (haz.intensity.max(axis=0) > 0).toarray().ravel()

    if not affected.any():
        return {
            "rmw_km": np.nan,
            "wind_footprint_area_km2": 0.0,
            "districts_affected": 0,
            "litpop_exposed": np.nan,
        }


    # ---------------------------------------------------------
    # Compute footprint area
    # ---------------------------------------------------------
    if not hasattr(cent, "cell_area") or cent.cell_area is None:
        area_km2 = np.nan
    else:
        area_km2 = cent.cell_area[affected].sum()

    num_cells = int(affected.sum())

    return {
        "rmw_km": np.nan,  # placeholder for future explicit RMW extraction
        "wind_footprint_area_km2": area_km2,
        "districts_affected": num_cells,
        "litpop_exposed": np.nan,
    }



def compute_master_metrics(sid):
    """Compute sum_raw, log_sum_raw from master file."""
    df = master[master.sid == sid]

    if df.empty:
        return {
            "sum_raw": np.nan,
            "log_sum_raw": np.nan,
        }

    sum_raw = df.loss_usd_raw.sum()

    return {
        "sum_raw": sum_raw,
        "log_sum_raw": np.log(sum_raw + 1),
    }


# ---------------------------------------------------------
# 3. Build the parameters table
# ---------------------------------------------------------

rows = []

for sid in meta.sid.unique():
    print(f"Processing {sid}...")

    track = get_ibtracs_track(sid)
    landfall = compute_landfall_properties(track)
    track_metrics = compute_track_metrics(track)
    climada_metrics = compute_climada_footprint(track)
    master_metrics = compute_master_metrics(sid)
    dlna_total = meta.loc[meta.sid == sid, "dlna_total_usd"].iloc[0]
    tpl_row = templates[templates.sid == sid]
    template_label = tpl_row.template_label.iloc[0] if not tpl_row.empty else "unknown"



    row = {
        "sid": sid,
        **landfall,
        **track_metrics,
        **climada_metrics,
        **master_metrics,
        "template_label": template_label,
        "dlna_total_usd": dlna_total,
    }

    rows.append(row)


# ---------------------------------------------------------
# 4. Save output
# ---------------------------------------------------------

params = pd.DataFrame(rows)
params.to_csv("data/cyclone_parameters.csv", index=False)

print("cyclone_parameters.csv generated successfully.")
