"""
Example: Running CCART Synthetic Cyclone Batch Simulations
----------------------------------------------------------
This script demonstrates how to call run_batch() with
user-supplied paths and data sources.
"""

import geopandas as gpd
import pandas as pd
from climada.entity import Exposures

from ccart.exposure.exposure import load_litpop_for_state
from ccart.vulnerability.vulnerability import build_vulnerability_curves
from ccart.cyclone.synthetic.run_batch import run_batch

# ---------------------------------------------------------
# User paths (edit these for your environment)
# ---------------------------------------------------------

DISTRICTS = r"C:\CMIP data\cmip6\Climada\Projects\ccart-india\ccart\data\boundaries\INDIA_DISTRICTS_FIXED.gpkg"
COASTLINE = r"C:\CMIP data\cmip6\Climada\Projects\ccart-india\ccart\data\coastline\coastl_ind.shp"
WEALTH = r"C:\CMIP data\cmip6\Climada\Projects\ccart-india\ccart\data\wealth\wealth_by_district.csv"
TRACKS = r"C:\CMIP data\cmip6\Climada\Projects\ccart-india\ccart\data\historical_tracks\ni_tracks_climada_1950_2023_cleaned.h5"

OUTPUT_ROOT = r"C:\CMIP data\cmip6\Climada\Projects\ccart-india\ccart\cyclone\outputs"

# ---------------------------------------------------------
# Load spatial + exposure data
# ---------------------------------------------------------

districts_gdf = gpd.read_file(DISTRICTS)
districts_gdf["District"] = districts_gdf["district"].astype(str).str.strip()

coastline_gdf = gpd.read_file(COASTLINE)
wealth_df = pd.read_csv(WEALTH)

assets_all, exp_dist = load_litpop_for_state("IND", districts_gdf)
exposures = Exposures(assets_all)

# Vulnerability curves
impf_set = build_vulnerability_curves()

# ---------------------------------------------------------
# Run batch
# ---------------------------------------------------------

run_batch(
    n_runs_per_scenario=5,
    exposures=exposures,
    districts_gdf=districts_gdf,
    coastline_gdf=coastline_gdf,
    wealth_df=wealth_df,
    impf_set=impf_set,
    clean_tracks_path=TRACKS,
    coastline_path_for_generator=COASTLINE,
    output_root=OUTPUT_ROOT,
)
