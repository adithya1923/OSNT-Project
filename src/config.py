import json
from copy import deepcopy
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent.parent


def load_config(config_path):
    config_path = Path(config_path)

    if not config_path.is_absolute():
        config_path = PROJECT_ROOT / config_path

    with open(config_path, "r") as file:
        return json.load(file)


def set_config_value(config, parameter_path, value):
    """
    Set a nested configuration value using a dotted path.

    Example:
        parameter_path = "topology.bottleneck_bandwidth"

    modifies:
        config["topology"]["bottleneck_bandwidth"]
    """

    updated_config = deepcopy(config)

    parts = parameter_path.split(".")
    current = updated_config

    for part in parts[:-1]:
        if part not in current:
            raise KeyError(
                f"Configuration section '{part}' "
                f"not found while setting '{parameter_path}'."
            )

        current = current[part]

    final_key = parts[-1]

    if final_key not in current:
        raise KeyError(
            f"Configuration parameter '{final_key}' "
            f"not found while setting '{parameter_path}'."
        )

    current[final_key] = value

    return updated_config