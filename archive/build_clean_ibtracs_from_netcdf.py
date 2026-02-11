import xarray as xr
import numpy as np
import pandas as pd
import os

def build_clean_ibtracs_from_netcdf(
    input_path=r"C:\CMIP data\cmip6\Climada\Projects\ccart-india\data\IBTrACS.ALL.v04r01.nc",
    output_path=r"C:\CMIP data\cmip6\Climada\Projects\ccart-india\data\processed\ibtracs_ni_clean_1950_2023.nc",
    min_year=1950,
    max_year=2023,
    min_wind=35
):
    print("📥 Loading IBTrACS NetCDF...")
    ds = xr.open_dataset(input_path)

    lat = ds["lat"]
    lon = ds["lon"]
    vmax = ds["wmo_wind"]
    basin = ds["basin"]
    season = ds["season"]

    print("🔍 Filtering NI basin (basin == 'NI')...")
    basin_mask = (basin == b"NI")
    storm_in_ni = basin_mask.any(dim="date_time")

    print("🔍 Filtering years...")
    year_mask = (season >= min_year) & (season <= max_year)

    print("🔍 Filtering intensity >= 35 kt...")
    wind_mask = vmax.max(dim="date_time") >= min_wind

    print("🔍 Combining filters...")
    storm_mask = storm_in_ni & year_mask & wind_mask

    valid_storms = np.where(storm_mask.values)[0]
    print(f"🌀 Storms passing filters: {len(valid_storms)}")

    tracks = []
    for i in valid_storms:
        track = ds.isel(storm=i)

        lat_vals = track["lat"].values
        lon_vals = track["lon"].values
        vmax_vals = track["wmo_wind"].values
        time_vals = track["time"].values

        valid = ~np.isnan(lat_vals) & ~np.isnan(lon_vals)
        lat_vals = lat_vals[valid]
        lon_vals = lon_vals[valid]
        vmax_vals = vmax_vals[valid]
        time_vals = time_vals[valid]

        if len(lat_vals) < 5:
            continue

        df = pd.DataFrame({
            "lat": lat_vals,
            "lon": lon_vals,
            "vmax": vmax_vals,
            "time": pd.to_datetime(time_vals)
        }).set_index("time")

        tracks.append(df.to_xarray())

    print(f"✨ Final curated tracks: {len(tracks)}")

    print("📦 Combining into single dataset...")
    combined = xr.concat(tracks, dim="storm")
    combined = combined.assign_coords(storm=("storm", np.arange(len(tracks))))

    print(f"💾 Saving to:\n{output_path}")
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    combined.to_netcdf(output_path)

    print("✅ Done! Clean NI dataset ready.")
    return combined


if __name__ == "__main__":
    build_clean_ibtracs_from_netcdf()