"""
CCART-Floods: Full Pipeline Orchestration
-----------------------------------------

1. CHIRPS ingestion + baseline metrics (Rx2day, P95)
2. FSI v1.1 + v1.2
3. FSI rasterisation + export
4. Hazard computation (historical + future)

Author: CCART Team
"""

from pathlib import Path
import numpy as np

# CHIRPS
from ccart.flood.chirps.ingest_chirps import load_chirps
from ccart.flood.compute_metrics import compute_baseline_metrics

# FSI
from ccart.flood.fsi.build_fsi_v1_1 import build_fsi_v1_1
from ccart.flood.fsi.build_fsi_v1_2 import build_fsi_v1_2
from ccart.flood.fsi.rasterise_fsi import rasterise_clean_rescale_fsi
from ccart.flood.fsi.export_fsi_raster import export_fsi_raster

# Hazard
from ccart.flood.hazard.ingest_fsi import ingest_fsi
from ccart.flood.hazard.hazard_engine import (
    compute_historical_hazard,
    compute_future_hazard,
)

from ccart.flood.config import (
        OUTPUT_DIR,
        FSI_OUTPUT_DIR,
        DYNAMIC_HAZARD_DIR,
        CHIRPS_DAILY_DIR,
        CMIP6_DIR,
        BASELINE_START,
        BASELINE_END,
        FUTURE_START,
        FUTURE_END,
        FSI_RASTER_PATH,
        INDIA_SHP,
        CHIRPS_START_YEAR,
        CHIRPS_END_YEAR,
    )



def run_pipeline():

    print("\n======================================")
    print("1. CHIRPS BASELINE METRICS (Rx2day, P95)")
    print("======================================")

    rx2day_dir = OUTPUT_DIR / "rx2day"
    p95_path = OUTPUT_DIR / "p95.npy"

    p95_grid = compute_baseline_metrics(
        start_year=BASELINE_START,
        end_year=BASELINE_END,
        rx2day_dir=rx2day_dir,
        p95_path=p95_path,
    )
    print("✓ Rx2day + P95 computed.")


    print("\n======================================")
    print("2. FSI v1.1 + v1.2")
    print("======================================")

    gdf_v1_1 = build_fsi_v1_1()
    gdf_v1_2 = build_fsi_v1_2(gdf_v1_1)
    print("✓ FSI v1.1 and v1.2 computed.")


    print("\n======================================")
    print("3. FSI RASTERISATION + EXPORT")
    print("======================================")

    # Use CHIRPS grid from any CHIRPS file via load_chirps
    chirps_meta = load_chirps(
        start_year=BASELINE_START,
        end_year=BASELINE_END,
    )
    shape = chirps_meta["shape"]
    transform = chirps_meta["transform"]

    fsi_rescaled = rasterise_clean_rescale_fsi(
        gdf_fsi_v1_2=gdf_v1_2,
        chirps_transform=transform,
        shape=shape,
    )

    fsi_path = FSI_OUTPUT_DIR / "fsi_v1_2_rescaled.tif"
    export_fsi_raster(fsi_rescaled, transform, fsi_path)
    print(f"✓ FSI raster exported to: {fsi_path}")


    print("\n======================================")
    print("4. FLOOD HAZARD (Historical + Future)")
    print("======================================")

    # Load FSI on CHIRPS grid (array) and metadata
    fsi_on_chirps, fsi_meta = ingest_fsi(
        fsi_path=FSI_RASTER_PATH,
        india_shp=INDIA_SHP,
        chirps_start_year=CHIRPS_START_YEAR,
        chirps_end_year=CHIRPS_END_YEAR
    )

    # Historical hazard
    compute_historical_hazard(
        rx2day_dir=rx2day_dir,
        p95_grid=p95_grid,
        fsi_on_chirps=fsi_on_chirps,
        out_dir=DYNAMIC_HAZARD_DIR,
    )
    print("✓ Historical hazard computed.")

    # Future hazard
    compute_future_hazard(
        cmip_dir=CMIP6_DIR,
        p95_grid=p95_grid,
        fsi_on_chirps=fsi_on_chirps,
        chirps_shape=fsi_meta["chirps_shape"],
        chirps_transform=fsi_meta["chirps_transform"],
        out_dir=DYNAMIC_HAZARD_DIR,
        start_year=FUTURE_START,
        end_year=FUTURE_END,
    )
    print("✓ Future hazard computed.")

    print("\n======================================")
    print("CCART-Floods pipeline completed successfully.")
    print("Outputs available in flood/outputs/")
    print("======================================\n")


if __name__ == "__main__":
    run_pipeline()
