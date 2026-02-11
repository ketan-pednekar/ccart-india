import sys
import os

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(PROJECT_ROOT)

import pandas as pd
from datetime import datetime

from legacy.v1_3.pipeline_v1_3 import run_cyclone_pipeline

# ------------------------------------------------------------
# Configuration
# ------------------------------------------------------------
METADATA_PATH = r"C:\CMIP data\cmip6\Climada\Projects\ccart-india\data\cyclone_metadata.csv"

OUTPUT_ROOT = r"C:\CMIP data\cmip6\Climada\Projects\ccart-india\outputs\v1.3"

DISTRICTS_PATH = r"C:\CMIP data\cmip6\Climada\Projects\ccart-india\data\india_districts.geojson"
COASTLINE_PATH = r"C:\CMIP data\cmip6\Climada\Projects\ccart-india\data\coastl_ind.shp"
IBTRACS_PATH = r"C:\CMIP data\cmip6\Climada\Projects\ccart-india\data\IBTrACS.ALL.v04r01.nc"

MASTER_PATH = r"C:\CMIP data\cmip6\Climada\Projects\ccart-india\data\district_relationships_master_v1_3.csv"
TEMPLATE_OUT = r"C:\CMIP data\cmip6\Climada\Projects\ccart-india\data\cyclone_templates_v1_3.csv"
TEMPLATE_MAP = {
    # Large, wide, high‑impact BoB giants
    "2020136N10088": "A",  # Amphan
    "2019116N02090": "A",  # Fani
    "2013281N12098": "A",  # Phailin
    "2014279N11096": "A",  # Hudhud
    "2019302N11118": "A",  # Bulbul (promoted from D → A)

    # Medium / large but not tail‑events
    "2020153N13072": "C",  # Nisarga
    "2021143N15090": "C",  # Yaas
    "2017333N06082": "C",  # Ockhi (from B → C; weak India impact)

    # Compact, intense, corridor‑type storms
    "2018281N14088": "D",  # Gaja (from B → D)
    "2018314N12093": "D",  # Titli (from B → D)
    "2013322N13090": "D",  # Helen (from C → D)
    "2009143N17089": "D",  # Aila
    "2010137N10090": "D",  # Laila
    "2016341N08092": "D",  # Vardah
}

def ensure_dir(path):
    os.makedirs(path, exist_ok=True)


def run_all_cyclones():
    meta = pd.read_csv(METADATA_PATH)

    required_cols = ["sid", "name", "dlna_total_usd", "year"]
    for col in required_cols:
        if col not in meta.columns:
            raise KeyError(f"Metadata CSV missing required column: {col}")

    skip_sids = ["2021133N10071"]   # TAUKTAE

    # Fresh master file
    # Fresh master file
    if os.path.exists(MASTER_PATH):
        os.remove(MASTER_PATH)
        print(f"\nDeleted old master file: {MASTER_PATH}")
    else:
        print("\nNo existing master file found — starting fresh.")

    # Fresh template file
    if os.path.exists(TEMPLATE_OUT):
        os.remove(TEMPLATE_OUT)
        print(f"\nDeleted old template file: {TEMPLATE_OUT}")
    else:
        print("\nNo existing template file found — starting fresh.")

    for _, row in meta.iterrows():
        sid = str(row["sid"]).strip()
        name = row["name"]
        dlna_total = row["dlna_total_usd"]
        year = int(row["year"])

        if sid in skip_sids:
            print(f"\n>>> Skipping {name} ({sid}) due to extreme computational load.")
            continue

        print(f"\n=== Running CCART v1.3 for {name} ({sid}) ===")

        outdir = os.path.join(OUTPUT_ROOT, f"{sid}_{name}")
        ensure_dir(outdir)
        ensure_dir(os.path.join(outdir, "states"))

        merged_all, by_state = run_cyclone_pipeline(
            cyclone_name=name,
            storm_id=sid,
            ibtracs_path=IBTRACS_PATH,
            districts_path=DISTRICTS_PATH,
            dlna_total=dlna_total,
            inland_clip_km=150.0,
            coastline_path=COASTLINE_PATH,
        )

        # --------------------------------------------------------
        # DEBUG: Inspect merged_all for one cyclone (e.g., Amphan)
        # --------------------------------------------------------
        if sid == "2020136N10088":  # Amphan
            print("\nDEBUG: merged_all columns:", merged_all.columns.tolist())
            print(
                merged_all[
                    [
                        "District",
                        "HWE_weight_norm",
                        "loss_usd_hwe",
                        "WindSpeed_Max_mps",
                        "hazard_mask",
                    ]
                ].head(40)
            )


        # Save per-cyclone outputs
        merged_all.to_file(os.path.join(outdir, "all_india.geojson"), driver="GeoJSON")
        merged_all.to_csv(os.path.join(outdir, "all_india.csv"), index=False)

        for st, gdf in by_state.items():
            safe_state = st.replace(" ", "_")
            gdf.to_file(
                os.path.join(outdir, "states", f"{safe_state}.geojson"),
                driver="GeoJSON",
            )

        with open(os.path.join(outdir, "run_log.txt"), "w", encoding="utf-8") as f:
            f.write(f"CCART v1.3 run for {name} ({sid})\n")
            f.write(f"Timestamp: {datetime.now()}\n")
            f.write(f"DLNA total: {dlna_total}\n")
            f.write(f"IBTRACS: {IBTRACS_PATH}\n")
            f.write(f"Districts: {DISTRICTS_PATH}\n")
            f.write(f"Coastline: {COASTLINE_PATH}\n")
            f.write(f"Metadata row: {row.to_dict()}\n")

        print(f"✓ Completed {name} ({sid}) — outputs saved to {outdir}")

        # --------------------------------------------------------
        # Build master-row slice for this cyclone
        # --------------------------------------------------------
        merged_all["sid"] = sid
        merged_all["cyclone_name"] = name
        merged_all["year"] = year
        merged_all["dlna_total"] = dlna_total

        cols = [
            "sid",
            "cyclone_name",
            "year",
            "state",
            "District",
            "loss_usd_raw",
            "HWE_weight_norm",
            "loss_usd_hwe",
            "dlna_total",
            "dist_to_coast_km",
            "is_inland",
            "WindSpeed_Max_mps",
            "WindSpeed_Mean_mps",
            "Centroid_Count",
            "hazard_mask",
        ]


        available_cols = [c for c in cols if c in merged_all.columns]
        out = merged_all[available_cols].copy()

        # Append directly to CSV without re-reading
        header_needed = not os.path.exists(MASTER_PATH)
        out.to_csv(MASTER_PATH, mode="a", index=False, header=header_needed)

        print(f"✓ Added {len(out)} rows for {sid} to master file.")

        # --------------------------------------------------------
        # Append template label for THIS cyclone
        # --------------------------------------------------------
        template_label = TEMPLATE_MAP.get(sid, "unknown")

        template_row = pd.DataFrame([{
            "sid": sid,
            "cyclone_name": name,
            "year": year,
            "template_label": template_label
        }])

        header_needed = not os.path.exists(TEMPLATE_OUT)
        template_row.to_csv(TEMPLATE_OUT, mode="a", index=False, header=header_needed)

        print(f"✓ Added template label for {sid}: {template_label}")


    # ------------------------------------------------------------
    # Final deduplication and cleanup
    # ------------------------------------------------------------
    print("\n=== Final master file cleanup ===")
    df = pd.read_csv(MASTER_PATH)

    before = len(df)
    df = df.drop_duplicates(subset=["sid", "District"])
    after = len(df)

    print(f"Removed {before - after} duplicate SID–District rows.")

    df.to_csv(MASTER_PATH, index=False)
    print(f"✓ Clean master file written to: {MASTER_PATH}")
    
if __name__ == "__main__":
    run_all_cyclones()
