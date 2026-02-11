import xarray as xr
import numpy as np
import os

def clean_ibtracs_nc(
    input_path=r"C:\CMIP data\cmip6\Climada\Projects\ccart-india\data\processed\ibtracs_ni_clean_1950_2023.nc",
    output_path=r"C:\CMIP data\cmip6\Climada\Projects\ccart-india\data\processed\ibtracs_ni_clean_1950_2023_noNaN.nc"
):
    print("📥 Loading dataset...")
    ds = xr.open_dataset(input_path)

    print(f"🌀 Total storms before cleaning: {ds.storm.size}")

    # Identify storms with NaNs in lat/lon
    valid_storms = []
    for i in range(ds.storm.size):
        track = ds.isel(storm=i)
        lat = track["lat"].values
        lon = track["lon"].values

        if np.isnan(lat).any() or np.isnan(lon).any():
            continue

        valid_storms.append(i)

    print(f"🧹 Storms without NaNs: {len(valid_storms)}")

    # Subset dataset
    cleaned = ds.isel(storm=valid_storms)

    # Save cleaned dataset
    print(f"💾 Saving cleaned dataset to:\n{output_path}")
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    cleaned.to_netcdf(output_path)

    print("✅ Cleaning complete.")
    return cleaned


if __name__ == "__main__":
    clean_ibtracs_nc()
