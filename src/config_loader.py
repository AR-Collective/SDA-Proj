import json


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

            return {k: data[k] for k in data}

    except FileNotFoundError:
        print("Configuration error: config.json file not found.")
        return None
    except json.JSONDecodeError as e:
        print(f"Configuration error: Invalid JSON format: {e}")
        return None
