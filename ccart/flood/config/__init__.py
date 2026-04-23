import yaml
from pathlib import Path

CONFIG_DIR = Path(__file__).resolve().parent

def load_paths():
    with open(CONFIG_DIR / "paths.yaml", "r") as f:
        return yaml.safe_load(f)

def load_flood_params():
    with open(CONFIG_DIR / "flood_params.yaml", "r") as f:
        return yaml.safe_load(f)
