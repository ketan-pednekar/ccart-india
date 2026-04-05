"""
CCART Synthetic Cyclone Batch Runner (v2.1)
-------------------------------------------
Runs multiple synthetic cyclone simulations across scenarios,
with clean run numbering and retry-safe orchestration.
"""

import os
from datetime import datetime
import pandas as pd

from ccart.cyclone.synthetic.run_single_synthetic import run_single_synthetic

SCENARIOS = ["baseline", "warm_sst", "high_end"]


def run_batch(
    n_runs_per_scenario=50,
    exposures=None,
    districts_gdf=None,
    coastline_gdf=None,
    wealth_df=None,
    impf_set=None,
    clean_tracks_path=None,
    coastline_path_for_generator=None,
    output_root=None,
    max_retries_per_scenario=500,
):
    """
    Run a batch of synthetic cyclone simulations across scenarios.

    Clean run numbering:
        Only valid storms get folders (run_001, run_002, ...)

    Retry logic:
        Weak/offshore storms return "RETRY" and do not create folders.
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

    print("\n=== CCART Batch Runner (v2.1) ===")
    print(f"Scenarios: {SCENARIOS}")
    print(f"Runs per scenario: {n_runs_per_scenario}")
    print(f"Output root: {batch_root}\n")

    # -------------------------------
    # Scenario loop
    # -------------------------------
    for scenario in SCENARIOS:
        retry_count = 0
        valid_count = 0

        print(f"\n=== Scenario: {scenario} ===")

        scenario_dir = os.path.join(batch_root, scenario)
        os.makedirs(scenario_dir, exist_ok=True)

        scenario_rows = []
        attempt = 1

        while valid_count < n_runs_per_scenario:

            if attempt > max_retries_per_scenario:
                raise RuntimeError(
                    f"Too many retries ({max_retries_per_scenario}) "
                    f"for scenario '{scenario}'. Check generator settings."
                )

            print(f"\n→ Scenario {scenario} | Attempt {attempt}")

            # -----------------------------------
            # Run full synthetic pipeline (no folder yet)
            # -----------------------------------
            result = run_single_synthetic(
                run_dir=None,
                exposures=exposures,
                districts_gdf=districts_gdf.copy(),
                coastline_gdf=coastline_gdf,
                wealth_df=wealth_df,
                impf_set=impf_set,
                cleaned_tracks_path=clean_tracks_path,
                coastline_path_for_generator=coastline_path_for_generator,
                scenario=scenario,
            )

            # -----------------------------------
            # Retry logic
            # -----------------------------------
            if result == "RETRY":
                print(f"⚠️ RETRY storm for scenario '{scenario}' (attempt {attempt})")
                retry_count += 1
                attempt += 1
                continue

            # -----------------------------------
            # VALID storm → assign clean run number
            # -----------------------------------
            valid_count += 1
            run_id = f"run_{valid_count:03d}"
            run_dir = os.path.join(scenario_dir, run_id)
            os.makedirs(run_dir, exist_ok=True)

            print(f"✓ Valid storm #{valid_count} → {run_id}")

            # Save metadata
            result["run_id"] = run_id
            result["scenario"] = scenario
            result["timestamp"] = datetime.now().isoformat()

            scenario_rows.append(result)
            master_rows.append(result)

            # -----------------------------------
            # Re-run pipeline to write outputs
            # -----------------------------------
            run_single_synthetic(
                run_dir=run_dir,
                exposures=exposures,
                districts_gdf=districts_gdf.copy(),
                coastline_gdf=coastline_gdf,
                wealth_df=wealth_df,
                impf_set=impf_set,
                cleaned_tracks_path=clean_tracks_path,
                coastline_path_for_generator=coastline_path_for_generator,
                scenario=scenario,
            )

            attempt += 1

        # -------------------------------
        # Scenario summary
        # -------------------------------
        scenario_csv = os.path.join(scenario_dir, "scenario_summary.csv")
        pd.DataFrame(scenario_rows).to_csv(scenario_csv, index=False)

        print(f"\n=== Scenario '{scenario}' summary ===")
        print(f"  Valid storms : {valid_count}")
        print(f"  RETRY storms : {retry_count}")
        print(f"✓ Scenario summary saved: {scenario_csv}")
        print("=====================================\n")

    # -------------------------------
    # Master summary
    # -------------------------------
    master_csv = os.path.join(batch_root, "master_summary.csv")
    pd.DataFrame(master_rows).to_csv(master_csv, index=False)

    print("\n=== Batch Complete ===")
    print(f"Master summary written to:\n  {master_csv}")
