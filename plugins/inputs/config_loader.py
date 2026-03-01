"""
Configuration Loader Module

Handles loading and parsing the application configuration from config.json.
This is part of the input phase - reading external configuration before processing.
"""

import sys
import json
import traceback


def load_config(config_path: str = "config.json") -> dict:
    """
    Load and parse the application configuration from a JSON file.

    This function attempts to read the configuration file and prints a summary
    of the loaded parameters (Region, Year, and Output Format) to the console.
    If the file is missing, malformed, or encounters an unexpected error,
    it forcefully exits the application with a specific status code.

    Args:
        config_path: Path to the configuration JSON file (default: "config.json")

    Returns:
        dict: A dictionary containing the parsed configuration settings.

    Raises:
        SystemExit:
            * **Exit code 1:** If config file is not found or contains invalid JSON.
            * **Exit code 2:** If a required configuration key is missing.
            * **Exit code 99:** For any other unexpected exceptions.
    """
    try:
        # Load config.json
        with open(config_path, "r") as config_file:
            config = json.load(config_file)

        print("✓ Configuration loaded successfully")
        print(f"  Region: {config.get('region')}")
        print(f"  Year: {config.get('year')}")
        print(f"  Output Format: {config.get('output_format', 'console')}")

        return config

    except FileNotFoundError as e:
        print(f"\n✗ File error: {e}")
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"\n✗ Configuration error (invalid JSON): {e}")
        sys.exit(1)
    except KeyError as e:
        print(f"\n✗ Missing configuration key: {e}")
        sys.exit(2)
    except Exception as e:
        print("\n✗ Unexpected error - full traceback below:")
        traceback.print_exc()
        sys.exit(99)
