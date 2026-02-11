import pandas as pd
import xarray as xr
import numpy as np
import os

def build_clean_ibtracs_dataset(
    csv_path,
    save_path=r"C:\CMIP data\cmip6\Climada\Projects\ccart-india\data\processed\ibtracs_ni_clean_1950_2023.nc",
    min_year=1950,
    max_year=2023,
    min_wind=35,
):
    """
    Build a clean, curated NI-basin IBTrACS dataset (1950–2023).
    Filters:
        - NI basin (BoB + AS)
        - USA provider (if available)
        - min_wind >= 35 kt
        - >= 5 track points
        - sorted by time
    Saves as a single NetCDF file.
    """

    print("📥 Loading raw IBTrACS CSV...")
    df = pd.read_csv(csv_path)

    # Convert MJD → datetime
    df["time"] = pd.to_datetime("1858-11-17") + pd.to_timedelta(df["time"], unit="D")
    df["year"] = df["time"].dt.year

    # Filter years
    df = df[(df["year"] >= min_year) & (df["year"] <= max_year)]

    # Filter NI basin
    df["basin_geo"] = df["basin_geo"].astype(str)
    df = df[df["basin_geo"].isin(["BoB", "AS"])]

    # Filter strong storms only
    df = df[df["vmax"] >= min_wind]

    # Filter provider if available
    if "source" in df.columns:
        df = df[df["source"] == "usa"]

    print(f"📊 After filtering: {df['sid'].nunique()} storms remain")

    # Group into tracks
    tracks = []
    for sid, group in df.groupby("sid"):
        group = group.sort_values("time")
        if len(group) < 5:
            continue
        ds = group.set_index("time").to_xarray()
        tracks.append(ds)

    print(f"🌀 Final curated tracks: {len(tracks)}")

    # Combine into a single dataset
    print("📦 Combining into a single dataset...")
    combined = xr.concat(tracks, dim="storm")
    combined = combined.assign_coords(storm=("storm", [t.sid.values[0] for t in tracks]))

    # Save
    print(f"💾 Saving curated dataset to:\n{save_path}")
    os.makedirs(os.path.dirname(save_path), exist_ok=True)
    combined.to_netcdf(save_path)

    print("✅ Done! Clean NI dataset ready.")
    return combined


if __name__ == "__main__":
    build_clean_ibtracs_dataset(
        csv_path=r"C:\CMIP data\cmip6\Climada\Projects\ccart-india\data\processed\ibtracs_ni_tracks_raw.csv"
    )
