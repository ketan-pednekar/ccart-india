import os
import json
import pandas as pd

# ------------------------------------------------------------
# CONFIG
# ------------------------------------------------------------
BASE_DIR = r"C:\CMIP data\cmip6\Climada\Projects\ccart-india\outputs\synthetic_runs_multi"
SCENARIOS = ["baseline", "warm_sst", "high_end"]


# ------------------------------------------------------------
# Inspect a single run folder
# ------------------------------------------------------------
def inspect_run(run_dir):
    return {
        "track.csv": os.path.exists(os.path.join(run_dir, "track.csv")),
        "hazard.gpkg": os.path.exists(os.path.join(run_dir, "hazard.gpkg")),
        "impact.gpkg": os.path.exists(os.path.join(run_dir, "impact.gpkg")),
        "metadata.json": os.path.exists(os.path.join(run_dir, "metadata.json")),
    }


# ------------------------------------------------------------
# Collect summaries for one scenario
# ------------------------------------------------------------
def collect_scenario(scenario):
    scen_dir = os.path.join(BASE_DIR, scenario)
    rows = []
    missing = []

    for run_name in sorted(os.listdir(scen_dir)):
        run_dir = os.path.join(scen_dir, run_name)
        if not os.path.isdir(run_dir):
            continue

        status = inspect_run(run_dir)

        # Only accept runs with BOTH impact.gpkg + metadata.json
        if not (status["impact.gpkg"] and status["metadata.json"]):
            missing.append((scenario, run_name, status))
            continue

        # Load metadata.json
        meta_path = os.path.join(run_dir, "metadata.json")
        with open(meta_path, "r") as f:
            meta = json.load(f)

        rows.append({
            "scenario": scenario,
            "run": run_name,
            "output_dir": run_dir,
            "sid": meta.get("sid"),
            "storm_name": meta.get("storm_name"),
            "raw_loss_total": meta.get("raw_loss_total"),
            "dlna_total": meta.get("dlna_total"),
            "calibrated_total": meta.get("calibrated_total"),
            "hwe_total": meta.get("hwe_total"),
            "n_districts_loss": meta.get("n_districts_loss"),
            "n_states_loss": meta.get("n_states_loss"),
            "max_intensity": meta.get("max_intensity"),
        })

    df = pd.DataFrame(rows)
    return df, missing


# ------------------------------------------------------------
# MAIN
# ------------------------------------------------------------
def main():
    all_summaries = []
    all_missing = []

    for scen in SCENARIOS:
        df_scen, missing = collect_scenario(scen)

        # Save scenario summary
        scen_out = os.path.join(BASE_DIR, f"{scen}_summary.csv")
        df_scen.to_csv(scen_out, index=False)

        print(f"{scen}: {len(df_scen)} complete runs")
        all_summaries.append(df_scen)
        all_missing.extend(missing)

    # Build master summary
    master = pd.concat(all_summaries, ignore_index=True)
    master_out = os.path.join(BASE_DIR, "master_summary.csv")
    master.to_csv(master_out, index=False)

    print("\nMaster summary:", len(master), "runs")

    # Log missing runs
    print("\n=== Missing Runs (impact or metadata missing) ===")
    for scen, run, status in all_missing:
        print(f"{scen}/{run}: {status}")


if __name__ == "__main__":
    main()
