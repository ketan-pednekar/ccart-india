"""
CCART-Floods: Global Configuration
----------------------------------

Centralised configuration for all CCART-Floods modules.
Defines project paths, input datasets, output directories,
baseline windows, and hazard constants.

Author: CCART Team
"""

from pathlib import Path

# ============================================================
# PROJECT ROOT
# ============================================================

# Root of the *flood module*, not the entire CCART repo
FLOOD_ROOT = Path(__file__).resolve().parent

# Root of the CCART project (one level above flood/)
PROJECT_ROOT = FLOOD_ROOT.parent

# Data directory (shared across modules)
DATA_DIR = PROJECT_ROOT / "data"

# ============================================================
# INPUT DATA PATHS
# ============================================================

# INDOFLOODS datasets
INDOFLOODS_DIR = DATA_DIR / "INDOFLOODS"
CATCHMENT_CSV = INDOFLOODS_DIR / "catchment_characteristics_indofloods.csv"
EVENTS_CSV    = INDOFLOODS_DIR / "floodevents_indofloods.csv"
META_CSV      = INDOFLOODS_DIR / "metadata_indofloods.csv"
PRECIP_CSV    = INDOFLOODS_DIR / "precipitation_variables_indofloods.csv"

# HydroBASINS
HYBAS_DIR = DATA_DIR / "HYBAS"
HYBAS_SHP = HYBAS_DIR / "hybas_as_lev06_v1c.shp"

# India boundary
INDIA_SHP = DATA_DIR / "boundaries" / "INDIA_DISTRICTS_FIXED.gpkg"

# CHIRPS daily rainfall directory
CHIRPS_DAILY_DIR = Path(r"D:\Climate Risk Data\CHIRPS_daily")

# CMIP6 rainfall (India subset)
CMIP6_DIR = PROJECT_ROOT / "outputs" / "cmip6_ssp370_india_fixed"

# ============================================================
# OUTPUT DIRECTORIES
# ============================================================

OUTPUT_DIR = FLOOD_ROOT / "outputs"
FSI_OUTPUT_DIR = OUTPUT_DIR / "fsi"
DYNAMIC_HAZARD_DIR = OUTPUT_DIR / "dynamic_hazard"

# Ensure directories exist
for d in [OUTPUT_DIR, FSI_OUTPUT_DIR, DYNAMIC_HAZARD_DIR]:
    d.mkdir(parents=True, exist_ok=True)

# ============================================================
# BASELINE & FUTURE WINDOWS
# ============================================================

BASELINE_START = 1995
BASELINE_END   = 2024

FUTURE_START   = 2027
FUTURE_END     = 2100

# CHIRPS grid metadata window
CHIRPS_START_YEAR = BASELINE_START
CHIRPS_END_YEAR   = BASELINE_END

# ============================================================
# FSI RASTER (generated during pipeline)
# ============================================================

FSI_RASTER_PATH = FSI_OUTPUT_DIR / "fsi_v1_2_rescaled.tif"

# ============================================================
# GRID SETTINGS
# ============================================================

CHIRPS_RESOLUTION = 0.05   # degrees
IDW_RESOLUTION    = 0.10   # degrees

# ============================================================
# HAZARD CONSTANTS
# ============================================================

EPS = 1e-6  # avoid divide-by-zero

# ============================================================
# LOGGING
# ============================================================

VERBOSE = True
