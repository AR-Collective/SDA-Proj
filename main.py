"""
SDA Project Phase 2 - Modular Orchestration & Dependency Inversion
"""


import traceback
import sys
from plugins.inputs import JsonReader, CsvReader, load_config
from plugins.outputs import ConsoleWriter, GraphicsChartWriter
from core.engine import TransformationEngine
from core.validator import validate_and_print_config, validate_and_print_config_format

INPUT_DRIVERS = {"json": JsonReader, "csv": CsvReader}
OUTPUT_DRIVERS = {"console": ConsoleWriter, "graphics": GraphicsChartWriter}


def print_section(title: str) -> None:
    """Print a formatted section header."""
    print("\n" + "="*60)
    print(f"  {title}")
    print("="*60)


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
    config = load_config()
    dic = {}
    for column in config["schema_mapping"]["columns"]:
        internal_name = column["internal_mapping"]
        data_type = column["data_type"]
        name = column["source_name"]
        dic[internal_name] = {"source_name": name, "data_type": data_type} 
    print(dic["entity_name"]["source_name"])

    # Early validation of config format and file accessibility
    # validate_and_print_config_format(config)

    # output_format = config.get("output_format", "console").lower()
    # if output_format not in OUTPUT_DRIVERS:
    #     print(f"✗ Unknown output format: {output_format}. Using 'console'")
    #     output_format = "console"
    #
    # sink = OUTPUT_DRIVERS[output_format]()
    # print(f"✓ Output writer instantiated: {output_format}")
    #
    # engine = TransformationEngine(sink)
    # print("✓ Transformation engine created with injected sink")
    #
    # input_format = config.get("input_format", "csv").lower()
    filepath = config.get("dataset_path", "data/sample_sensor_data.csv")
    #
    # if input_format not in INPUT_DRIVERS:
    #     print(f"✗ Unknown input format: {input_format}. Using 'csv'")
    #     input_format = "csv"
    #
    # print(f"✓ Input driver selected: {input_format}")
    # print(f"✓ Loading data from: {filepath}")
    #
    raw_data = INPUT_DRIVERS["csv"](filepath)
    print(raw_data)
    # print(f"✓ Data loaded successfully ({len(raw_data)} rows)")
    #
    # # Validate configuration against actual data
    # validate_and_print_config(raw_data, config)
    #
    # engine.execute(raw_data, config)
    # print("✓ Pipeline execution completed successfully")
    #


if __name__ == "__main__":
    bootstrap()
