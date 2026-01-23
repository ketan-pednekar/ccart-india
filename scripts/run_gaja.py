import os
import pandas as pd
from ccart.engine import run_ccart
from ccart.viz import ccart_choropleth

# ============================================================
# 1. Load cyclone metadata (Gaja)
# ============================================================

meta_path = r"C:\CMIP data\cmip6\Climada\Projects\ccart-india\data\cyclone_metadata.csv"
meta = pd.read_csv(meta_path)

sid = "2018314N12093"  # Gaja SID
row = meta[meta["sid"] == sid].iloc[0]

cyclone_name = row["name"].title()          # "Gaja"
dlna_total = row["dlna_total_usd"]
calibration_state = str(row["landfall_state"]).upper()
year = int(row["year"])

print(f"\n=== Running CCART for {cyclone_name} ({year}) ===")
print(f"SID: {sid}")
print(f"Calibration state: {calibration_state}")
print(f"DLNA total (USD): {dlna_total:,.0f}")

# ============================================================
# 2. Global paths (engine inputs)
# ============================================================

base_path = r"C:\CMIP data\cmip6\Climada\Projects\ccart-india"

ibtracs_path = os.path.join(base_path, "data", "IBTRACS.ALL.v04r01.nc")
districts_path = os.path.join(base_path, "data", "INDIA_DISTRICTS.geojson")
coastline_path = os.path.join(base_path, "data", "coastl_ind.shp")

# ============================================================
# 3. Run CCART engine (multi-state, all-India)
# ============================================================

gdf = run_ccart(
    cyclone_name=cyclone_name,
    storm_id=sid,
    ibtracs_path=ibtracs_path,
    districts_path=districts_path,
    dlna_total=dlna_total,
    state_name=calibration_state,   # primary calibration state
    inland_clip_km=150,
    coastline_path=coastline_path
)

print("\n=== Sample output (first 5 rows) ===")
print(gdf.head())

# ============================================================
# 4. India-wide diagnostics
# ============================================================

print("\n=== India-wide: Top 10 districts by CCART loss (HWE-calibrated) ===")
print(
    gdf[["state", "District", "loss_usd_hwe"]]
    .sort_values("loss_usd_hwe", ascending=False)
    .head(10)
)

print("\n=== India-wide: Top 10 districts by HWE weight ===")
print(
    gdf[["state", "District", "HWE_weight_norm"]]
    .sort_values("HWE_weight_norm", ascending=False)
    .head(10)
)

print("\n=== India-wide: Top 10 districts by raw CLIMADA loss ===")
print(
    gdf[["state", "District", "loss_usd_raw"]]
    .sort_values("loss_usd_raw", ascending=False)
    .head(10)
)

# ============================================================
# 5. Per-state diagnostics + maps
# ============================================================

states = sorted(gdf["state"].dropna().unique())
print(f"\nStates affected (non-zero geometry): {states}")

for st in states:
    gdf_st = gdf[gdf["state"] == st].copy()
    total_loss_st = gdf_st["loss_usd_hwe"].sum()

    print(f"\n=== {cyclone_name} – {st}: Top 10 districts by CCART loss ===")
    print(
        gdf_st[["District", "loss_usd_hwe"]]
        .sort_values("loss_usd_hwe", ascending=False)
        .head(10)
    )

    if total_loss_st > 0:
        df_losses_st = (
            gdf_st[["District", "loss_usd_hwe"]]
            .rename(columns={"loss_usd_hwe": "loss"})
        )

        title = f"Cyclone {cyclone_name} – CCART Loss Map ({st})"
        print(f"Generating choropleth for {st} (total loss: {total_loss_st:,.0f} USD)")

        ccart_choropleth(
            gdf_st,
            df_losses_st,
            district_col="District",
            loss_col="loss",
            state_filter=st,
            title=title
        )
    else:
        print(f"No positive losses in {st} — skipping choropleth.")

# ============================================================
# 6. Update master CSV (district_relationships_master.csv)
# ============================================================

master_path = os.path.join(base_path, "data", "district_relationships_master.csv")

gdf["sid"] = sid
gdf["cyclone_name"] = cyclone_name
gdf["year"] = year
gdf["dlna_total"] = dlna_total
gdf["calibration_state"] = calibration_state

cols = [
    "sid", "cyclone_name", "year", "state", "District",
    "loss_usd_raw", "HWE_weight_norm", "loss_usd_hwe",
    "dlna_total", "calibration_state",
    "dist_to_coast_km", "is_inland"
]

out = gdf[cols].copy()

if os.path.exists(master_path):
    master = pd.read_csv(master_path)
    master = master[master["sid"] != sid]   # remove old rows for this cyclone
    master = pd.concat([master, out], ignore_index=True)
    master.to_csv(master_path, index=False)
else:
    out.to_csv(master_path, index=False)

print(f"\nSaved {len(out)} rows for SID {sid} to master CSV.")
print("\n=== Completed CCART multi-state run for Gaja ===")
