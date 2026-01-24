import os
import pandas as pd
from datetime import datetime

# ------------------------------------------------------------
# Import the v1.3 engine
# ------------------------------------------------------------
from ccart.pipeline_v1_3 import run_cyclone_pipeline

# ------------------------------------------------------------
# 1. Load cyclone metadata (Amphan)
# ------------------------------------------------------------
meta_path = r"C:\CMIP data\cmip6\Climada\Projects\ccart-india\data\cyclone_metadata.csv"
meta = pd.read_csv(meta_path)

sid = "2020136N10088"   # Amphan SID
row = meta[meta["sid"] == sid].iloc[0]

cyclone_name = row["name"].title()     # "Amphan"
dlna_total = row["dlna_total_usd"]
year = int(row["year"])

print(f"\n=== Running CCART v1.3 for {cyclone_name} ({sid}) ===")
print(f"DLNA total (USD): {dlna_total:,.0f}")

# ------------------------------------------------------------
# 2. Global paths (engine inputs)
# ------------------------------------------------------------
base_path = r"C:\CMIP data\cmip6\Climada\Projects\ccart-india"

ibtracs_path = os.path.join(base_path, "data", "IBTRACS.ALL.v04r01.nc")
districts_path = os.path.join(base_path, "data", "india_districts.geojson")
coastline_path = os.path.join(base_path, "data", "coastl_ind.shp")

# ------------------------------------------------------------
# 3. Output folder (v1.3 structure)
# ------------------------------------------------------------
outdir = os.path.join(base_path, "outputs", "v1.3", f"{sid}_{cyclone_name}")
os.makedirs(outdir, exist_ok=True)
os.makedirs(os.path.join(outdir, "states"), exist_ok=True)

# ------------------------------------------------------------
# 4. Run CCART v1.3 engine (all-India, multi-state)
# ------------------------------------------------------------
merged_all, by_state = run_cyclone_pipeline(
    cyclone_name=cyclone_name,
    storm_id=sid,
    ibtracs_path=ibtracs_path,
    districts_path=districts_path,
    dlna_total=dlna_total,
    inland_clip_km=150.0,
    coastline_path=coastline_path,
)

print("\n=== Sample output (first 5 rows) ===")
print(merged_all.head())

# ------------------------------------------------------------
# 5. Save all-India outputs
# ------------------------------------------------------------
merged_all.to_file(os.path.join(outdir, "all_india.geojson"), driver="GeoJSON")
merged_all.to_csv(os.path.join(outdir, "all_india.csv"), index=False)

# ------------------------------------------------------------
# 6. Save per-state outputs
# ------------------------------------------------------------
for st, gdf in by_state.items():
    safe_state = st.replace(" ", "_")
    gdf.to_file(
        os.path.join(outdir, "states", f"{safe_state}.geojson"),
        driver="GeoJSON",
    )

# ------------------------------------------------------------
# 7. Save metadata + log
# ------------------------------------------------------------
with open(os.path.join(outdir, "run_log.txt"), "w", encoding="utf-8") as f:
    f.write(f"CCART v1.3 run for {cyclone_name} ({sid})\n")
    f.write(f"Timestamp: {datetime.now()}\n")
    f.write(f"DLNA total: {dlna_total}\n")
    f.write(f"IBTRACS: {ibtracs_path}\n")
    f.write(f"Districts: {districts_path}\n")
    f.write(f"Coastline: {coastline_path}\n")
    f.write(f"Metadata row: {row.to_dict()}\n")

print(f"\n✓ Completed CCART v1.3 run for {cyclone_name} ({sid})")
print(f"Outputs saved to: {outdir}")

# ------------------------------------------------------------
# 8. Generate and save choropleths (PNG) for each state
# ------------------------------------------------------------
from ccart.viz_v1_3 import ccart_choropleth

print("\n=== Generating choropleths (PNG) ===")

for st, gdf_st in by_state.items():
    total_loss_st = gdf_st["loss_usd_hwe"].sum()

    if total_loss_st <= 0:
        print(f"Skipping {st} — no positive losses.")
        continue

    df_losses_st = (
        gdf_st[["District", "loss_usd_hwe"]]
        .rename(columns={"loss_usd_hwe": "loss"})
    )

    title = f"Cyclone {cyclone_name} – CCART Loss Map ({st})"
    print(f"Saving choropleth for {st} (total loss: {total_loss_st:,.0f} USD)")

    png_path = os.path.join(outdir, f"{st.replace(' ', '_')}_loss_map.png")

    ccart_choropleth(
        gdf_st,
        df_losses_st,
        district_col="District",
        loss_col="loss",
        state_filter=st,
        title=title,
        save_path=png_path,
        dpi=200
    )

# ------------------------------------------------------------
# 9. Update district_relationships_master_v1_3.csv
# ------------------------------------------------------------
master_path = os.path.join(base_path, "data", "district_relationships_master_v1_3.csv")

merged_all["sid"] = sid
merged_all["cyclone_name"] = cyclone_name
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
    "is_inland"
]

# Only keep columns that actually exist
available_cols = [c for c in cols if c in merged_all.columns]

out = merged_all[available_cols].copy()

if os.path.exists(master_path):
    master = pd.read_csv(master_path)
    master = master[master["sid"] != sid]
    master = pd.concat([master, out], ignore_index=True)
    master.to_csv(master_path, index=False)
else:
    out.to_csv(master_path, index=False)

print(f"\n✓ Updated district_relationships_master_v1_3.csv with {len(out)} rows for {sid}")
