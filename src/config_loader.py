import json
import pandas as pd


def get_config_options():
    check_keys = ["region", "operation", "year", "output"]
    try:
        with open("config.json") as file:
            data = json.load(file)

            missing = [key for key in check_keys if key not in data]
            if missing:
                print(f"Configuration error: Missing keys {
                      ', '.join(missing)}")
                return None

        return data

    except FileNotFoundError:
        print("Configuration error: config.json file not found.")
        return None
    except json.JSONDecodeError as e:
        print(f"Configuration error: Invalid JSON format: {e}")
        return None


def validate_config(config_array: dict, df: pd.DataFrame) -> None:
    if config_array['region'] not in df['Continent'].values:
        raise ValueError(
            f"The Region '{config_array['region']}' does not exist in the data.")
    if config_array['year'] not in df['Year'].values:
        raise ValueError(
            f"Year {config_array['year']} not found in dataset.")
