from ccart.flood.config import load_paths
import inspect, os

# Find the config module file
import ccart.flood.config as cfg
print("[CONFIG MODULE]:", inspect.getfile(cfg))

# Now locate paths.yaml relative to that file
config_dir = os.path.dirname(inspect.getfile(cfg))
paths_yaml_guess = os.path.join(os.path.dirname(config_dir), "paths.yaml")
print("[GUESS paths.yaml]:", os.path.abspath(paths_yaml_guess))

# Load and print keys
paths = load_paths()
print("[flood.outputs keys]:", paths["flood"]["outputs"].keys())
