from pathlib import Path
import json


def get_config_options():
    try:
        with open("config.json") as file:
            data = json.load(file)
            return {k: data[k] for k in data}
    except (json.JSONDecodeError, KeyError) as e:
        print(f"Configuration error: {e}")
        return None
