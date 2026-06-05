import yaml
from pathlib import Path

# ---------------------------------------------------------
# Resolve project root (ccart-india/)
# ---------------------------------------------------------
PROJECT_ROOT = Path(__file__).resolve().parents[2]

# ---------------------------------------------------------
# Directories
# ---------------------------------------------------------
FLOOD_DIR = Path(__file__).resolve().parent
CONFIG_DATA_DIR = FLOOD_DIR / "config_data"


# ---------------------------------------------------------
# LOAD PATHS (paths.yaml)
# ---------------------------------------------------------
def load_paths():
    paths_file = CONFIG_DATA_DIR / "paths.yaml"

    with open(paths_file, "r") as f:
        cfg = yaml.safe_load(f)

    def resolve(item):
        # string → resolve path
        if isinstance(item, str):
            p = Path(item)
            return p if p.is_absolute() else (PROJECT_ROOT / p).resolve()

        # dict → recursively resolve
        if isinstance(item, dict):
            return {k: resolve(v) for k, v in item.items()}

        # list → recursively resolve
        if isinstance(item, list):
            return [resolve(v) for v in item]

        return item

    return resolve(cfg)


# ---------------------------------------------------------
# LOAD FLOOD PARAMS (flood_params.yaml)
# ---------------------------------------------------------
def load_flood_params():
    params_file = CONFIG_DATA_DIR / "flood_params.yaml"

    with open(params_file, "r") as f:
        params = yaml.safe_load(f)

    return params
