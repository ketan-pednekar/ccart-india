import os
import pandas as pd
from datetime import datetime

from ccart.engine_v1_2 import run_cyclone_pipeline


# ------------------------------------------------------------
# Configuration
# ------------------------------------------------------------
METADATA_PATH = r"C:\CMIP data\cmip6\Climada\Projects\ccart-india\data\cyclone_metadata.csv"
OUTPUT_ROOT = r"C:\CMIP data\cmip6\Climada\Projects\ccart-india\outputs\v1.2"

# India-wide districts file (same for all cyclones)
DISTRICTS_PATH = r"C:\CMIP data\cmip6\Climada\Projects\ccart-india\data\india_districts.geojson"

# Coastline file for inland clipping
COASTLINE_PATH = r"C:\CMIP data\cmip6\Climada\Projects\ccart-india\data\coastl_ind.shp"

# IBTrACS file (same for all cyclones)
IBTRACS_PATH = r"C:\CMIP data\cmip6\Climada\Projects\ccart-india\data\IBTrACS.ALL.v04r01.nc"


# ------------------------------------------------------------
# Helper: ensure folder exists
# ------------------------------------------------------------
def ensure_dir(path):
    os.makedirs(path, exist_ok=True)


# ------------------------------------------------------------
# Batch runner
# ------------------------------------------------------------
def run_all_cyclones():
    meta = pd.read_csv(METADATA_PATH)

    required_cols = ["sid", "name", "dlna_total_usd"]
    for col in required_cols:
        if col not in meta.columns:
            raise KeyError(f"Metadata CSV missing required column: {col}")

    for _, row in meta.iterrows():
        sid = row["sid"]
        name = row["name"]
        dlna_total = row["dlna_total_usd"]

        print(f"\n=== Running CCART v1.2 for {name} ({sid}) ===")

        # Output folder for this cyclone
        outdir = os.path.join(OUTPUT_ROOT, f"{sid}_{name}")
        ensure_dir(outdir)
        ensure_dir(os.path.join(outdir, "states"))

        # Run the v1.2 engine
        merged_all, by_state = run_cyclone_pipeline(
            cyclone_name=name,
            storm_id=sid,
            ibtracs_path=IBTRACS_PATH,
            districts_path=DISTRICTS_PATH,
            dlna_total=dlna_total,
            inland_clip_km=150.0,
            coastline_path=COASTLINE_PATH,
        )

        # ------------------------------------------------------------
        # Save all-India outputs
        # ------------------------------------------------------------
        merged_all.to_file(os.path.join(outdir, "all_india.geojson"), driver="GeoJSON")
        merged_all.to_csv(os.path.join(outdir, "all_india.csv"), index=False)

        # ------------------------------------------------------------
        # Save per-state outputs
        # ------------------------------------------------------------
        for st, gdf in by_state.items():
            safe_state = st.replace(" ", "_")
            gdf.to_file(
                os.path.join(outdir, "states", f"{safe_state}.geojson"),
                driver="GeoJSON",
            )

        # ------------------------------------------------------------
        # Save metadata + log
        # ------------------------------------------------------------
        with open(os.path.join(outdir, "run_log.txt"), "w", encoding="utf-8") as f:
            f.write(f"CCART v1.2 run for {name} ({sid})\n")
            f.write(f"Timestamp: {datetime.now()}\n")
            f.write(f"DLNA total: {dlna_total}\n")
            f.write(f"IBTrACS: {IBTRACS_PATH}\n")
            f.write(f"Districts: {DISTRICTS_PATH}\n")
            f.write(f"Coastline: {COASTLINE_PATH}\n")
            f.write(f"Metadata row: {row.to_dict()}\n")

        print(f"✓ Completed {name} ({sid}) — outputs saved to {outdir}")


if __name__ == "__main__":
    run_all_cyclones()
