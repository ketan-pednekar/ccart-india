import numpy as np
import rasterio
from rasterio.warp import reproject, Resampling
from pathlib import Path

project_root = Path(r"C:\CMIP_data\cmip6\Climada\Projects\ccart-india")

# source: validated FSI (620x600)
src_fsi_path = project_root / "ccart" / "flood" / "outputs" / "fsi" / "ccart_floods_fsi_rescaled.tif"

# template: CHIRPS grid (607x586) – use P95 as template
template_path = project_root / "ccart" / "flood" / "outputs" / "p95" / "p95_chirps_2day.tif"

# output: FSI on CHIRPS grid
out_path = project_root / "ccart" / "flood" / "outputs" / "fsi" / "static_fsi_on_chirps.tif"


if __name__ == "__main__":

    print("Loading source FSI...")
    with rasterio.open(src_fsi_path) as src:
        fsi = src.read(1).astype("float32")
        src_transform = src.transform
        src_crs = src.crs
        src_nodata = src.nodata

    # if no nodata defined, create one from NaNs
    if src_nodata is None:
        src_nodata = -9999.0
        mask_nan = np.isnan(fsi)
        fsi[mask_nan] = src_nodata

    print("Loading CHIRPS template (P95)...")
    with rasterio.open(template_path) as tmpl:
        dst_profile = tmpl.profile
        dst_transform = tmpl.transform
        dst_crs = tmpl.crs
        height = tmpl.height
        width = tmpl.width

    dst_profile.update(
        dtype="float32",
        nodata=src_nodata,
        compress="lzw"
    )

    dst = np.full((height, width), src_nodata, dtype="float32")

    print("Reprojecting FSI to CHIRPS grid...")
    reproject(
        source=fsi,
        destination=dst,
        src_transform=src_transform,
        src_crs=src_crs,
        src_nodata=src_nodata,
        dst_transform=dst_transform,
        dst_crs=dst_crs,
        dst_nodata=src_nodata,
        resampling=Resampling.bilinear,
    )

    # convert nodata back to NaN
    dst = dst.astype("float32")
    dst[dst == src_nodata] = np.nan

    print(f"Saving reprojected FSI → {out_path}")
    with rasterio.open(out_path, "w", **dst_profile) as dst_src:
        dst_src.write(dst, 1)

    print("Done. static_fsi_on_chirps.tif is now on the CHIRPS grid (607x586).")
