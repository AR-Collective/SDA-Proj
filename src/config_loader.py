import json
from typing import Dict, Any
import pandas as pd

def get_config_options(config_path: str = "config.json") -> Dict[str, Any]:
    
    """
    Load and validate configuration file.

    Returns the configuration dictionary if valid, otherwise raises a clear exception.
    """
    
    required_keys = ["region", "operation", "year", "output"]

    try:
        with open(config_path) as f:
            data = json.load(f)
    except FileNotFoundError as e:
        raise FileNotFoundError(f"Configuration error: {config_path} not found.") from e
    except json.JSONDecodeError as e:
        raise ValueError(f"Configuration error: Invalid JSON format: {e}") from e

    missing = [k for k in required_keys if k not in data]
    if missing:
        raise KeyError(f"Configuration error: Missing keys: {', '.join(missing)}")

    # Basic type/choice validation
    if not isinstance(data.get("region"), str):
        raise ValueError("Configuration error: 'region' must be a string.")

    if data.get("operation") not in ("average", "sum"):
        raise ValueError("Configuration error: 'operation' must be either 'average' or 'sum'.")

    # allow integer-like years (e.g., strings that represent integers)
    try:
        data["year"] = int(data["year"])
    except Exception:
        raise ValueError("Configuration error: 'year' must be an integer year.")

    if not isinstance(data.get("output"), str):
        raise ValueError("Configuration error: 'output' must be a string (e.g. 'dashboard').")

    return data


def validate_config(config: Dict[str, Any], df: pd.DataFrame) -> None:
   
    """
    Validate that the `region` and `year` specified in config exist in the DataFrame.

    Raises ValueError with a clear message when validation fails.
    """
   
    if "Continent" not in df.columns:
        raise ValueError("Dataset validation error: 'Continent' column not found in data.")

    if config["region"] not in df["Continent"].unique():
        raise ValueError(f"Configuration error: The region '{config['region']}' does not exist in the data.")

    if "Year" not in df.columns:
        raise ValueError("Dataset validation error: 'Year' column not found in data.")

    if config["year"] not in df["Year"].unique():
        raise ValueError(f"Configuration error: Year {config['year']} not found in dataset.")
