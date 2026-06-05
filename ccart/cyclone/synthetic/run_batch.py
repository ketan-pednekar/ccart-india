"""
CCART Synthetic Cyclone Batch Runner (v3.0)
-------------------------------------------
Uses simulate_storm() + write_outputs() for atomic runs.
No partial folders. Fully resume‑friendly.
"""

import os
from datetime import datetime
import pandas as pd

from ccart.cyclone.synthetic.synthetic_core import simulate_storm, write_outputs

SCENARIOS = ["baseline", "warm_sst", "high_end"]


def run_batch(
    n_runs_per_scenario=5,
    exposures=None,
    districts_gdf=None,
    coastline_gdf=None,
    wealth_df=None,
    impf_set=None,
    clean_tracks_path=None,
    coastline_path_for_generator=None,
    output_root="E:\\ccart_cyclone_outputs",
    max_retries_per_scenario=2000,
):
    """
    Resume‑friendly CCART batch runner.
    Uses simulate_storm() for validation and write_outputs() for atomic writes.
    """

    # -------------------------------
    # Validate required inputs
    # -------------------------------
    if exposures is None:
        raise ValueError("exposures must be provided.")
    if districts_gdf is None:
        raise ValueError("districts_gdf must be provided.")
    if coastline_gdf is None:
        raise ValueError("coastline_gdf must be provided.")
    if wealth_df is None:
        raise ValueError("wealth_df must be provided.")
    if impf_set is None:
        raise ValueError("impf_set must be provided.")
    if clean_tracks_path is None:
        raise ValueError("clean_tracks_path must be provided.")
    if coastline_path_for_generator is None:
        raise ValueError("coastline_path_for_generator must be provided.")
    if output_root is None:
        raise ValueError("output_root must be provided.")

    batch_root = os.path.join(output_root, "synthetic-runs")
    os.makedirs(batch_root, exist_ok=True)

    master_rows = []

    print("\n=== CCART Batch Runner (Atomic v3.0) ===")
    print(f"Scenarios: {SCENARIOS}")
    print(f"Runs per scenario: {n_runs_per_scenario}")
    print(f"Output root: {batch_root}\n")

    # -------------------------------
    # Scenario loop
    # -------------------------------
    for scenario in SCENARIOS:

        print(f"\n=== Scenario: {scenario} ===")

        scenario_dir = os.path.join(batch_root, scenario)
        os.makedirs(scenario_dir, exist_ok=True)

        # -----------------------------------------
        # RESUME LOGIC: detect existing run folders
        # -----------------------------------------
        existing = [
            d for d in os.listdir(scenario_dir)
            if d.startswith("run_") and d[4:].isdigit()
        ]

        if existing:
            last = max(int(d.split("_")[1]) for d in existing)
        else:
            last = 0

        valid_count = last
        retry_count = 0
        attempt = 1

        print(f"→ Existing valid runs detected: {valid_count}")
        print(f"→ Continuing from run_{valid_count+1:03d}")

        scenario_rows = []

        # -----------------------------------------
        # MAIN LOOP
        # -----------------------------------------
        while valid_count < n_runs_per_scenario:

            if attempt > max_retries_per_scenario:
                raise RuntimeError(
                    f"Too many retries ({max_retries_per_scenario}) "
                    f"for scenario '{scenario}'. Check generator settings."
                )

            print(f"\n→ Scenario {scenario} | Attempt {attempt}")

            # 1) Dry run: simulate storm in memory (NO FILE WRITING)
            result = simulate_storm(
                exposures=exposures,
                districts_gdf=districts_gdf.copy(),
                coastline_gdf=coastline_gdf,
                wealth_df=wealth_df,
                impf_set=impf_set,
                cleaned_tracks_path=clean_tracks_path,
                coastline_path_for_generator=coastline_path_for_generator,
                scenario=scenario,
            )

            # 2) Retry logic
            if result == "RETRY":
                print(f"⚠️ RETRY storm for scenario '{scenario}' (attempt {attempt})")
                retry_count += 1
                attempt += 1
                continue

            # 3) Valid storm → assign next run number
            valid_count += 1
            run_id = f"run_{valid_count:03d}"
            run_dir = os.path.join(scenario_dir, run_id)

            print(f"✓ Valid storm #{valid_count} → {run_id}")

            # 4) Write outputs atomically
            write_outputs(run_dir, result)

            # 5) Add metadata to summary
            meta = result["metadata"]
            meta["run_id"] = run_id
            meta["scenario"] = scenario
            meta["timestamp"] = datetime.now().isoformat()

            scenario_rows.append(meta)
            master_rows.append(meta)

            attempt += 1

        # Scenario summary
        scenario_csv = os.path.join(scenario_dir, "scenario_summary.csv")
        pd.DataFrame(scenario_rows).to_csv(scenario_csv, index=False)

        print(f"\n=== Scenario '{scenario}' summary ===")
        print(f"  Valid storms : {valid_count}")
        print(f"  RETRY storms : {retry_count}")
        print(f"✓ Scenario summary saved: {scenario_csv}")
        print("=====================================\n")

    # Master summary
    master_csv = os.path.join(batch_root, "master_summary.csv")
    pd.DataFrame(master_rows).to_csv(master_csv, index=False)

    print("\n=== Batch Complete ===")
    print(f"Master summary written to:\n  {master_csv}")




