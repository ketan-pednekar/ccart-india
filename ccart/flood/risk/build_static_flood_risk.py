"""
CCART Flood Module
Static Flood Risk Builder
-------------------------

Computes static flood risk as:

    Risk = FSI (0–1) × Exposure (0–48 integer)

Corrected version:
    - Exposure is reprojected to FSI grid
    - Exposure is masked to FSI footprint
    - Risk inherits FSI geotransform exactly
"""

from pathlib import Path
import rasterio
import numpy as np
from rasterio.warp import reproject, Resampling

def build_static_flood_risk():
    project_root = Path("C:/CMIP_data/cmip6/Climada/Projects/ccart-india")

    fsi_tif = project_root / "ccart/flood/outputs/fsi/ccart_floods_fsi_rescaled.tif"

    # Your EMC exposure file
    exp_tif = Path("E:/EMC_BUILT_INDIA_005deg_CLIPPED.tif")

    risk_out = project_root / "ccart/flood/outputs/risk/ccart_floods_static_risk_005deg_v1.tif"

    with rasterio.open(fsi_tif) as fsi_src, rasterio.open(exp_tif) as exp_src:
        fsi = fsi_src.read(1).astype(float)
        fsi[fsi == fsi_src.nodata] = np.nan

        # Prepare empty array for reprojected exposure
        exp_reproj = np.empty_like(fsi, dtype=float)

        # ⭐ Reproject exposure to FSI grid
        reproject(
            source=exp_src.read(1).astype(float),
            destination=exp_reproj,
            src_transform=exp_src.transform,
            src_crs=exp_src.crs,
            dst_transform=fsi_src.transform,
            dst_crs=fsi_src.crs,
            resampling=Resampling.bilinear
        )

        exp_reproj[exp_reproj == exp_src.nodata] = np.nan

        # ⭐ STATIC RISK
        risk = fsi * exp_reproj

        # Write output
        profile = fsi_src.profile
        profile.update(dtype="float32", nodata=np.nan)

        with rasterio.open(risk_out, "w", **profile) as dst:
            dst.write(risk.astype("float32"), 1)

    print("Static risk written to:", risk_out)


if __name__ == "__main__":
    build_static_flood_risk()
