import os
import pandas as pd
from datetime import datetime

from ccart.synthetic.run_synthetic_cyclone_v2 import run_single_synthetic

SCENARIOS = ["warm_sst", "high_end"]

def run_synthetic_batch_multi(n_runs_per_scenario=50):
    """
    Run synthetic cyclones across multiple scenarios.
    Each scenario gets its own folder.
    Each run gets its own subfolder + metadata.json.
    A scenario-level summary CSV and a master CSV are produced.
    """

    base_dir = r"C:\CMIP data\cmip6\Climada\Projects\ccart-india"
    batch_root = os.path.join(base_dir, "outputs", "synthetic_runs_multi")
    os.makedirs(batch_root, exist_ok=True)

    master_rows = []

    print("\n=== CCART Multi-Scenario Batch Runner ===")
    print(f"Scenarios: {SCENARIOS}")
    print(f"Runs per scenario: {n_runs_per_scenario}\n")

    for scenario in SCENARIOS:
        retry_count = 0
        valid_count = 0

        print(f"\n=== Scenario: {scenario} ===")

        scenario_dir = os.path.join(batch_root, scenario)
        os.makedirs(scenario_dir, exist_ok=True)

        scenario_rows = []

        for i in range(1, n_runs_per_scenario + 1):
            run_id = f"run_{i:03d}"
            run_dir = os.path.join(scenario_dir, run_id)

            # --- RESUME FIX: Skip completed runs ---
            if os.path.exists(run_dir) and os.listdir(run_dir):
                print(f"→ Scenario {scenario} | Run {i} already exists — skipping.")
                continue

            # Create folder only if missing
            os.makedirs(run_dir, exist_ok=True)

            print(f"\n→ Scenario {scenario} | Starting run {i}/{n_runs_per_scenario}")

            # Run the engine
            try:
                result = run_single_synthetic(
                    run_dir,
                    save_hazard=True,
                    save_track=True,
                    save_hazard_gpkg=True,
                    save_track_csv=True
                )
            except Exception as e:
                print(f"⚠️ ERROR in run {i}, continuing: {e}")
                continue

            if result == "RETRY":
                retry_count += 1
                print(f"⚠️ RETRY #{retry_count} for scenario '{scenario}' (attempt {i})")
                continue

            valid_count += 1
            print(f"✓ Valid storm #{valid_count} for scenario '{scenario}'")

            result["run_id"] = run_id
            result["scenario"] = scenario
            result["timestamp"] = datetime.now().isoformat()

            scenario_rows.append(result)
            master_rows.append(result)


        print(f"\n=== Scenario '{scenario}' summary ===")
        print(f"  Valid storms : {valid_count}")
        print(f"  RETRY storms : {retry_count}")
        print("=====================================\n")

        # Save scenario summary
        scenario_csv = os.path.join(scenario_dir, "scenario_summary.csv")
        pd.DataFrame(scenario_rows).to_csv(scenario_csv, index=False)
        print(f"✓ Scenario summary saved: {scenario_csv}")

    # Save master summary
    master_csv = os.path.join(batch_root, "master_summary.csv")
    pd.DataFrame(master_rows).to_csv(master_csv, index=False)

    print("\n=== Batch Complete ===")
    print(f"Master summary written to:\n  {master_csv}")


if __name__ == "__main__":
    run_synthetic_batch_multi(n_runs_per_scenario=500)

