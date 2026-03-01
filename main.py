"""
SDA Project Phase 2 - Modular Orchestration & Dependency Inversion
"""


import traceback
import sys
import json
from plugins.inputs import JsonReader, CsvReader
from plugins.outputs import ConsoleWriter, GraphicsChartWriter
from core.engine import TransformationEngine


def config_loader():
    """
    Load and parse the application configuration from ``config.json``.

    This function attempts to read the local JSON configuration file and prints
    a summary of the loaded parameters (Region, Year, and Output Format) to the
    console. If the file is missing, malformed, or encounters an unexpected
    error, it forcefully exits the application with a specific status code.

    Returns:
        dict: A dictionary containing the parsed configuration settings.

    Raises:
        SystemExit:
            * **Exit code 1:** If ``config.json`` is not found or contains invalid JSON.
            * **Exit code 2:** If a required configuration key is missing.
            * **Exit code 99:** For any other unexpected exceptions.
    """
    try:
        # Step 1: Load config.json
        with open("config.json", "r") as config_file:
            config = json.load(config_file)

        print("✓ Configuration loaded successfully")
        print(f"  Region: {config.get('region')}")
        print(f"  Year: {config.get('year')}")
        print(f"  Output Format: {config.get('output_format', 'console')}")


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
    return config


def print_section(title: str) -> None:
    """Print a formatted section header."""
    print("\n" + "="*60)
    print(f"  {title}")
    print("="*60)


INPUT_DRIVERS = {"json": JsonReader, "csv": CsvReader}
OUTPUT_DRIVERS = {"console": ConsoleWriter, "graphics": GraphicsChartWriter}

def bootstrap():
    """
    Bootstrap the application following the Dependency Inversion Principle.

    This function acts as the main entry point for the application, orchestrating
    the setup of input/output drivers and the core transformation engine based
    on the configuration file.

    The bootstrapping process follows these sequential steps:
        1. Load ``config.json``.
        2. Instantiate the Output Sink based on the configuration.
        3. Instantiate the Core Engine with the injected Sink.
        4. Instantiate the Input driver based on the configuration.
        5. Load the data and execute the pipeline.

    Raises:
        SystemExit: Exits with code 1 if files are missing or JSON is invalid,
            code 2 if a configuration key is missing, or code 99 for any
            unexpected errors.
    """
    print_section("SDA PROJECT PHASE 2 - Modular Orchestration")
    config = config_loader()

    output_format = config.get("output_format", "console").lower()
    if output_format not in OUTPUT_DRIVERS:
        print(f"✗ Unknown output format: {output_format}. Using 'console'")
        output_format = "console"

    sink = OUTPUT_DRIVERS[output_format]()
    print(f"✓ Output writer instantiated: {output_format}")

    engine = TransformationEngine(sink)
    print("✓ Transformation engine created with injected sink")

    input_format = config.get("input_format", "csv").lower()
    filepath = config.get("filepath", "data/gdp_with_continent_filled.csv")

    if input_format not in INPUT_DRIVERS:
        print(f"✗ Unknown input format: {input_format}. Using 'csv'")
        input_format = "csv"

    print(f"✓ Input driver selected: {input_format}")
    print(f"✓ Loading data from: {filepath}")

    raw_data = INPUT_DRIVERS[input_format](filepath)
    print(f"✓ Data loaded successfully ({len(raw_data)} rows)")

    engine.execute(raw_data, config)
    print("✓ Pipeline execution completed successfully")


if __name__ == "__main__":
    bootstrap()
