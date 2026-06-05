"""
CCART-Heat — Generate Time-Slice Cubes (wbt35, 0.05° India Grid)
================================================================

This script creates *time-slice Zarr cubes* from the annual exceedance
cubes. These cubes become the authoritative source for:

- TIFF generation
- animations
- GIS exports
- district-level validation

No TIFFs are written here. No masks. No transforms.
This keeps the scientific pipeline clean and bulletproof.
"""

from pathlib import Path
import xarray as xr
import numpy as np

# -------------------------------------------------------------------
# CONFIG
# -------------------------------------------------------------------
CUBE_HIST = r"C:\CMIP_data\cmip6\Climada\Projects\ccart-india\ccart\Heat\outputs\exceedance\cube_hist_wbt35.zarr"
CUBE_SSP370 = r"C:\CMIP_data\cmip6\Climada\Projects\ccart-india\ccart\Heat\outputs\exceedance\cube_ssp370_wbt35.zarr"

OUT_DIR = r"C:\CMIP_data\cmip6\Climada\Projects\ccart-india\ccart\Heat\outputs\timeslice_cubes"

TIME_SLICES = {
    "Historical_1995-2014":  (1995, 2014, "hist"),
    "NearTerm_2027-2039":    (2027, 2039, "ssp"),
    "MidCentury_2040-2069":  (2040, 2069, "ssp"),
    "EndCentury_2081-2100":  (2081, 2100, "ssp"),
}

# -------------------------------------------------------------------
# MAIN
# -------------------------------------------------------------------
def main():

    print("Loading exceedance cubes (wbt35)...")
    ds_hist = xr.open_zarr(CUBE_HIST)
    ds_ssp  = xr.open_zarr(CUBE_SSP370)

    da_hist = ds_hist["wbt35"]   # (year, lat, lon)
    da_ssp  = ds_ssp["wbt35"]

    out_root = Path(OUT_DIR)
    out_root.mkdir(parents=True, exist_ok=True)

    # ---------------------------------------------------------------
    # LOOP THROUGH TIME SLICES
    # ---------------------------------------------------------------
    for label, (start, end, cube_type) in TIME_SLICES.items():

        print(f"\n=== Generating time-slice cube: {label} ({start}-{end}) ===")

        da = da_hist if cube_type == "hist" else da_ssp

        # Max exceedance across the slice
        da_slice = da.sel(year=slice(start, end)).max("year")

        # Add metadata
        da_slice = da_slice.assign_attrs(
            {
                "description": f"Max annual exceedance (WBT>35°C) for {label}",
                "years": f"{start}-{end}",
                "source_cube": cube_type,
                "variable": "wbt35",
                "grid": "0.05° India grid (center-aligned)",
            }
        )

        # Save as Zarr
        out_path = out_root / f"cube_timeslice_wbt35_{label}.zarr"
        if out_path.exists():
            import shutil
            shutil.rmtree(out_path)

        da_slice.to_dataset(name="wbt35").to_zarr(out_path)

        print(f"Saved time-slice cube: {out_path}")


if __name__ == "__main__":
    main()
