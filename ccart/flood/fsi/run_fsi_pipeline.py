"""
CCART-Floods — FSI Pipeline Runner (CHIRPS-aligned, static)
-----------------------------------------------------------

Canonical CCART-Floods susceptibility workflow:

FSI (gauges, FSI_masked)
    → HYBAS basin assignment
    → basin-wise rasterisation to CHIRPS India grid
    → clean + rescale (0–1)
    → export CHIRPS-aligned GeoTIFF

This script orchestrates the full static FSI pipeline:

1. Loads CHIRPS India grid metadata from paths.yaml
2. Computes unified FSI at IndoFloods gauges (compute_fsi; includes FSI_masked)
3. Performs basin-wise rasterisation using HYBAS L06 polygons
   (rasterise_clean_rescale_fsi)
4. Cleans and rescales the susceptibility field to 0–1
5. Exports the canonical CHIRPS-aligned static FSI GeoTIFF for hazard modelling

Output:
    ccart_floods_fsi_static_chirps_rescaled.tif
"""

from pathlib import Path
import rasterio

from ccart.flood.config import load_paths
from ccart.flood.fsi.compute_fsi import compute_fsi
from ccart.flood.fsi.rasterise_fsi import rasterise_clean_rescale_fsi
from ccart.flood.fsi.export_fsi_raster import export_fsi_raster


# --------------------------------------------------------------------
# Helpers
# --------------------------------------------------------------------

def load_chirps_grid(chirps_path: Path):
    """Return (transform, shape, crs) from a CHIRPS reference raster."""
    with rasterio.open(chirps_path) as src:
        transform = src.transform
        shape = (src.height, src.width)
        crs = src.crs
    return transform, shape, crs


# --------------------------------------------------------------------
# Main pipeline
# --------------------------------------------------------------------

def main():
    paths = load_paths()
    project_root = Path(paths["project_root"])

    # Inputs
    chirps_template = project_root / paths["chirps"]["template"]
    hybas_path = project_root / paths["data"]["hybas"]

    # Output (canonical static FSI)
    out_path = project_root / paths["flood"]["outputs"]["fsi_static"]
    out_path.parent.mkdir(parents=True, exist_ok=True)

    print("\n[CCART-Floods] FSI → CHIRPS pipeline started")
    print(f"CHIRPS template: {chirps_template}")
    print(f"HYBAS file     : {hybas_path}")
    print(f"Output raster  : {out_path}\n")

    # 1. Load CHIRPS grid metadata (canonical grid)
    chirps_transform, shape, crs = load_chirps_grid(chirps_template)
    print(f"CHIRPS grid → shape={shape}, crs={crs}")

    # 2. Compute unified FSI (v1.2 + FSI_masked at gauges)
    print("Step 1/3 — Computing FSI at gauges (compute_fsi)...")
    gdf_fsi = compute_fsi()
    print(f"  FSI gauges: {len(gdf_fsi)}")

    # 3. Basin-wise rasterisation, clean, rescale
    print("Step 2/3 — Basin-wise rasterising FSI to CHIRPS grid...")
    fsi_rescaled = rasterise_clean_rescale_fsi(
        gdf_fsi=gdf_fsi,
        chirps_transform=chirps_transform,
        shape=shape,
        hybas_path=hybas_path,
    )
    print("  FSI rasterised and rescaled to 0–1 on CHIRPS grid.")

    # 4. Export final susceptibility raster (canonical static FSI)
    print("Step 3/3 — Exporting FSI raster to GeoTIFF...")
    export_fsi_raster(
        fsi_rescaled=fsi_rescaled,
        chirps_transform=chirps_transform,
        out_path=out_path,
        crs=str(crs),
    )

    print("\n[CCART-Floods] FSI → CHIRPS pipeline completed.")
    print(f"Canonical static FSI raster → {out_path}\n")


if __name__ == "__main__":
    main()
