"""
SDA Project Phase 3 - Complete Pipeline with Input, Core, Output
"""

from plugins.inputs.generic_producer import GenericInputProducer
from plugins.outputs import ConsoleConsumer, GUIConsumer
from new_core.core import Core, Agregator
import multiprocessing as mp
import json
from pathlib import Path
import sys
import threading
import logging

# INPUT_DRIVERS = {"json": JsonReader, "csv": CsvReader}
# OUTPUT_DRIVERS = {"console": ConsoleWriter, "graphics": GraphicsChartWriter}


def print_section(title: str) -> None:
    """Print a formatted section header."""
    print("\n" + "="*60)
    print(f"  {title}")
    print("="*60)


def initialize_multiprocessing(processes,input_queue, agregator_queue,workers, core_config):

    for _ in range(workers):
        core = Core(input_queue, agregator_queue,core_config)
        p=mp.Process(target=core.process)
        p.start()
        processes.append(p)



def shutdown_everything(input_producer, processes, input_queue, agg_process, agregator_queue, output_processes, output_queue):
    """Gracefully shutdown all pipeline processes."""
    input_producer.join()

    for i in range(len(processes)):
        input_queue.put(None)

    agregator_queue.put(None)

    for worker in processes:
        worker.join()

    agg_process.join()

    # Signal output consumers to shutdown
    output_queue.put(None)

    # Wait for output consumers
    for proc in output_processes:
        proc.join()

    return

def bootstrap():
    """Bootstrap the complete Phase 3 pipeline."""
    # Load config
    config_path = Path("config.json")
    if not config_path.exists():
        print("config.json not found")
        sys.exit(1)

    with open(config_path) as f:
        config = json.load(f)

    print("\n" + "=" * 70)
    print("  SDA PROJECT PHASE 3 - COMPLETE PIPELINE")
    print("=" * 70)
    print("  Input → Core Workers → Aggregator → Output Consumers\n")

    # Initialize queues and processes
    processes = []
    output_processes = []
    queue_size = config["pipeline_dynamics"]["stream_queue_max_size"]
    workers = 1  # Using single worker for demo (can be increased)

    input_queue = mp.Queue(maxsize=queue_size)
    agregator_queue = mp.Queue(maxsize=queue_size)
    output_queue = mp.Queue(maxsize=queue_size)

    # Start input producer
    print("Starting Input Producer...")
    producer = GenericInputProducer(config, input_queue)
    input_producer = mp.Process(target=producer.run)
    input_producer.start()

    # Start core workers
    print("Starting Core Workers...")
    initialize_multiprocessing(processes, input_queue, agregator_queue, workers, config["processing"])

    # Start aggregator
    print("Starting Aggregator...")
    agg = Agregator(agregator_queue, output_queue, queue_size)
    agg_process = mp.Process(target=agg.agregate)
    agg_process.start()

    # Start output consumers
    print("Starting Output Consumers...\n")

    # ============================================================
    # OUTPUT CONSUMER SELECTION
    # ============================================================
    # Uncomment ONE of the two sections below to choose which
    # output consumer to use:
    #
    # Option 1: CONSOLE OUTPUT
    # Uncomment the section below to see real-time console output
    # ============================================================

    # Console consumer
    try:
        console_consumer = ConsoleConsumer(output_queue)
        console_process = mp.Process(target=console_consumer.consume)
        console_process.start()
        output_processes.append(console_process)
        print("  ✓ Console consumer started\n")
    except Exception as e:
        print(f"  ✗ Failed to start console consumer: {e}\n")

    # ============================================================
    # Option 2: GUI DASHBOARD (Requires matplotlib)
    # Comment out the Console consumer above and uncomment this
    # section to see live graph and statistics panel
    # ============================================================

    # # GUI consumer
    # try:
    #     gui_consumer = GUIConsumer(output_queue)
    #     gui_process = mp.Process(target=gui_consumer.consume)
    #     gui_process.start()
    #     output_processes.append(gui_process)
    #     print("  ✓ GUI consumer started\n")
    # except ImportError:
    #     print("  ⚠ GUI consumer skipped (matplotlib not available)\n")
    # except Exception as e:
    #     print(f"  ✗ Failed to start GUI consumer: {e}\n")

    # ============================================================

    # Setup graceful shutdown handler
    def on_all_done():
        """Called when all output is complete."""
        shutdown_everything(input_producer, processes, input_queue, agg_process, agregator_queue, output_processes, output_queue)

    shutdown_manager = threading.Thread(target=on_all_done)
    shutdown_manager.daemon = True
    shutdown_manager.start()

    # Wait for shutdown manager to complete
    shutdown_manager.join()

    print("\n" + "=" * 70)
    print("  Pipeline Complete")
    print("=" * 70 + "\n")



if __name__ == "__main__":
    bootstrap()

    # OLD CODE

    # def bootstrap():
    #     """
    #     Bootstrap the application following the Dependency Inversion Principle.
    #
    #     This function acts as the main entry point for the application, orchestrating
    #     the setup of input/output drivers and the core transformation engine based
    #     on the configuration file.
    #
    #     The bootstrapping process follows these sequential steps:
    #         1. Load ``config.json``.
    #         2. Instantiate the Output Sink based on the configuration.
    #         3. Instantiate the Core Engine with the injected Sink.
    #         4. Instantiate the Input driver based on the configuration.
    #         5. Load the data and execute the pipeline.
    #
    #     Raises:
    #         SystemExit: Exits with code 1 if files are missing or JSON is invalid,
    #             code 2 if a configuration key is missing, or code 99 for any
    #             unexpected errors.
    #     """
    #     print_section("SDA PROJECT PHASE 2 - Modular Orchestration")
    #     config = load_config()
    #     dic = {}
    #     for column in config["schema_mapping"]["columns"]:
    #         internal_name = column["internal_mapping"]
    #         data_type = column["data_type"]
    #         name = column["source_name"]
    #         dic[internal_name] = {"source_name": name, "data_type": data_type} 
    #     print(dic["entity_name"]["source_name"])
    #
    #     # Early validation of config format and file accessibility
    #     # validate_and_print_config_format(config)
    #
    #     # output_format = config.get("output_format", "console").lower()
    #     # if output_format not in OUTPUT_DRIVERS:
    #     #     print(f"✗ Unknown output format: {output_format}. Using 'console'")
    #     #     output_format = "console"
    #     #
    #     # sink = OUTPUT_DRIVERS[output_format]()
    #     # print(f"✓ Output writer instantiated: {output_format}")
    #     #
    #     # engine = TransformationEngine(sink)
    #     # print("✓ Transformation engine created with injected sink")
    #     #
    #     # input_format = config.get("input_format", "csv").lower()
    #     filepath = config.get("dataset_path", "data/sample_sensor_data.csv")
    #     #
    #     # if input_format not in INPUT_DRIVERS:
    #     #     print(f"✗ Unknown input format: {input_format}. Using 'csv'")
    #     #     input_format = "csv"
    #     #
    #     # print(f"✓ Input driver selected: {input_format}")
    #     # print(f"✓ Loading data from: {filepath}")
    #     #
    #     raw_data = INPUT_DRIVERS["csv"](filepath)
    #     print(raw_data)
    #     # print(f"✓ Data loaded successfully ({len(raw_data)} rows)")
    #     #
    #     # # Validate configuration against actual data
    #     # validate_and_print_config(raw_data, config)
    #     #
    #     # engine.execute(raw_data, config)
    #     # print("✓ Pipeline execution completed successfully")
    #     #
    #
