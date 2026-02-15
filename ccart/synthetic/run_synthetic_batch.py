import os
import pandas as pd
from datetime import datetime

from ccart.synthetic.run_synthetic_cyclone_v2 import run_single_synthetic

SCENARIOS = ["baseline", "warm_sst", "high_end"]

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
        print(f"\n=== Scenario: {scenario} ===")

        scenario_dir = os.path.join(batch_root, scenario)
        os.makedirs(scenario_dir, exist_ok=True)

        scenario_rows = []

        for i in range(1, n_runs_per_scenario + 1):
            run_id = f"run_{i:03d}"
            run_dir = os.path.join(scenario_dir, run_id)
            os.makedirs(run_dir, exist_ok=True)

            print(f"\n→ Scenario {scenario} | Run {i}/{n_runs_per_scenario}")

            # Inject scenario into the environment
            result = run_single_synthetic(run_dir)

            if result == "RETRY":
                print("⚠️  Zero-impact storm — regenerating this run.")
                continue

            result["run_id"] = run_id
            result["scenario"] = scenario
            result["timestamp"] = datetime.now().isoformat()

            scenario_rows.append(result)
            master_rows.append(result)

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
    run_synthetic_batch_multi(n_runs_per_scenario=5)

