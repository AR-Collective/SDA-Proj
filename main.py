"""
SDA Project Phase 3 - Complete Pipeline with Input, Core, Output
"""

from plugins.inputs.generic_producer import GenericInputProducer
from plugins.inputs.input_validator import InputValidator
from plugins.outputs import ConsoleConsumer, GUIConsumer
from core.core import Core, Agregator
import multiprocessing as mp
import json
from pathlib import Path
import sys
import threading
import logging



def initialize_multiprocessing(processes,input_queue, agregator_queue,workers, core_config):

    for _ in range(workers):
        core = Core(input_queue, agregator_queue,core_config)
        p=mp.Process(target=core.process)
        p.start()
        processes.append(p)



def shutdown_everything(input_producer, processes, input_queue, agg_process, agregator_queue, output_processes, output_queue):
    """Gracefully shutdown all pipeline processes."""
    input_producer.join()

    for worker in processes:
        worker.join()

    agregator_queue.put(None)
    agg_process.join()

    # Signal output consumers to shutdown
    output_queue.put(None)

    # Wait for output consumers
    for proc in output_processes:
        proc.join()

    return

def print_header():
    print("\n" + "=" * 70)
    print("  SDA PROJECT PHASE 3 - COMPLETE PIPELINE")
    print("=" * 70)
    print("  Input → Core Workers → Aggregator → Output Consumers\n")

def bootstrap():
    """Bootstrap the complete Phase 3 pipeline."""
    # Load config
    config_path = Path("config.json")
    if not config_path.exists():
        print("config.json not found")
        sys.exit(1)

    with open(config_path) as f:
        config = json.load(f)

    print_header()

    validator = InputValidator(config)
    is_valid, message = validator.validate_all()
    if not is_valid:
        logger.error(f"Config validation failed:\n{message}")
        raise ProducerError(f"Invalid config: {message}")

    print(f"* Config validation passed")

    # Initialize queues and processes
    processes = []
    output_processes = []
    queue_size = config["pipeline_dynamics"]["stream_queue_max_size"]
    workers = 5  

    input_queue = mp.Queue(maxsize=queue_size)
    agregator_queue = mp.Queue(maxsize=queue_size)
    output_queue = mp.Queue(maxsize=queue_size)

    # Start input producer
    print("Starting Input Producer...")
    input_delay = config["pipeline_dynamics"]["input_delay_seconds"]
    producer = GenericInputProducer(input_queue,config["schema_mapping"], input_delay)
    input_producer = mp.Process(target=producer.run, args=(config["dataset_path"],))
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

