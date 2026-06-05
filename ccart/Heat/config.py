import yaml
from pathlib import Path

def load_heat_paths():
    # __file__ = ccart/Heat/config.py
    project_root = Path(__file__).resolve().parents[1]      # ccart/
    heat_dir     = Path(__file__).resolve().parents[0]      # Heat/
    paths_file   = heat_dir / "config_data" / "paths.yaml"  # Heat/config_data/paths.yaml

    with open(paths_file, "r") as f:
        cfg = yaml.safe_load(f)

    heat_cfg = cfg["heat"]

    def resolve(p):
        p = Path(p)
        if p.is_absolute():
            return p
        return (project_root / p).resolve()

    return {
        "data_root": resolve(heat_cfg["data_root"]),

        "boundaries": {
            "districts":     resolve(heat_cfg["boundaries"]["districts"]),
            "india_outline": resolve(heat_cfg["boundaries"]["india_outline"]),
        },

        "builtup": resolve(heat_cfg["builtup"]),

        "ingested": {
            "hist":   resolve(heat_cfg["ingested"]["hist"]),
            "ssp370": resolve(heat_cfg["ingested"]["ssp370"]),
            "ssp585": resolve(heat_cfg["ingested"]["ssp585"]),
        },

        "hazard": {
            "historical":  resolve(heat_cfg["hazard"]["historical"]),
            "near_term":   resolve(heat_cfg["hazard"]["near_term"]),
            "mid_century": resolve(heat_cfg["hazard"]["mid_century"]),
            "end_century": resolve(heat_cfg["hazard"]["end_century"]),
        },

        "outputs": {
            "district_timeslices": resolve(heat_cfg["outputs"]["district_timeslices"]),
            "viz":                 resolve(heat_cfg["outputs"]["viz"]),
            "timeslices":          resolve(heat_cfg["outputs"]["timeslices"]),
            "timeslice_cubes":     resolve(heat_cfg["outputs"]["timeslice_cubes"]),
            "tasmax_cubes":        resolve(heat_cfg["outputs"]["tasmax_cubes"]),
            "wbt_cubes":           resolve(heat_cfg["outputs"]["wbt_cubes"]),      # ⭐ NEW
            "hazard_cubes":        resolve(heat_cfg["outputs"]["hazard_cubes"]),   # ⭐ NEW
        },


        "exceedance": resolve(heat_cfg["exceedance"]),

        "cache": resolve(heat_cfg["cache"]),
    }
