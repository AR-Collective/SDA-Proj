"""
SDA Project Phase 3 - Complete Pipeline with Input, Core, Output
"""
import logging
import threading
import sys
from pathlib import Path
import json
import multiprocessing as mp
from core import Observer,Telemetry
from core import CoreManager
from core import Agregator
# from plugins.outputs import ConsoleConsumer, GUIConsumer
from plugins.inputs.input_validator import InputValidator
from plugins.inputs.generic_producer import GenericInputProducer
from multiprocessing.managers import BaseManager
import subprocess
import time
import socket

# Create UDP sockets for sensor data and telemetry
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
UDP_IP = "127.0.0.1"
UDP_PORT = 5005
TELEMETRY_PORT = 5006

def worker(output_queue):
    while True:
        data = output_queue.get()
        if data is None:
            return
        time.sleep(0.01)
        message = json.dumps(data).encode('utf-8')
        sock.sendto(message, (UDP_IP, UDP_PORT))

class Observer_Telemetry(Observer):
    def __init__(self, telemetry_socket=None):
        self.telemetry_socket = telemetry_socket

    def update(self, data):
        print(data)

        if self.telemetry_socket:
            try:
                telemetry_packet = json.dumps({
                    "input_queue_size": data[0],
                    "agregator_queue_size": data[1],
                    "output_queue_size": data[2],
                    "timestamp": time.time()
                }).encode('utf-8')
                self.telemetry_socket.sendto(telemetry_packet, (UDP_IP, TELEMETRY_PORT))
            except Exception as e:
                print(f"[Telemetry] Error sending UDP packet: {e}")

class Pipeline:
    def __init__(self,config):
        self.config = config
        self.manager = None  # Will be initialized in bootstrap

    def validate_config(self):
        validator = InputValidator(self.config)
        is_valid, message = validator.validate_all()
        if not is_valid:
            logger.error(f"Config validation failed:\n{message}")
            raise ProducerError(f"Invalid config: {message}")

        print(f"* Config validation passed")
        return True

    def bootstrap(self):
        # Initialize Manager FIRST for queue support on macOS
        self.manager = mp.Manager()

        self.validate_config()
        self.queue_size = self.config["pipeline_dynamics"]["stream_queue_max_size"]
        self.workers = self.config["pipeline_dynamics"]["core_parallelism"]

        self.init_queues()
        self.run_input()
        self.run_core()
        # start aggregate process
        self.run_agregate()
        self.run_telemetry()

        self.run_output()

        self.shutdown_all()


        # # Start output consumers
        # print("Starting Output Consumers...\n")


        # Setup graceful shutdown handler


    def init_queues(self):
        # Use Manager queues instead of mp.Queue for macOS compatibility
        self.input_queue = self.manager.Queue(maxsize=self.queue_size)
        self.agregator_queue = self.manager.Queue(maxsize=self.queue_size)
        self.output_queue = self.manager.Queue(maxsize=self.queue_size)

    def run_input(self):

        # Start input producer
        print("Starting Input Producer...")
        input_delay = self.config["pipeline_dynamics"]["input_delay_seconds"]
        producer = GenericInputProducer(self.input_queue,self.config["schema_mapping"], input_delay)
        self.input_producer = mp.Process(target=producer.run, args=(self.config["dataset_path"],))
        self.input_producer.start()
        return
    def shutdown_input(self):
        self.input_producer.join()
        return
    def run_telemetry(self):
        # Create telemetry UDP socket
        telemetry_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        print("Starting Telemetry...")
        self.see = Observer_Telemetry(telemetry_socket=telemetry_socket)
        self.telemetry = Telemetry(self.input_queue, self.agregator_queue, self.output_queue)
        self.telemetry.subscribe(self.see)
        self.telemetry_proc = mp.Process(target=self.telemetry.poll, args=(0.01,))
        self.telemetry_proc.start()
        return
    def shutdown_telemetry(self):
        self.telemetry.quit()
        self.telemetry_proc.join()
        return
    def run_core(self):
        # Start core workers
        print("Starting Core Workers...")
        self.core = CoreManager(self.input_queue, self.agregator_queue, self.workers, self.config["processing"])
        self.core.initialize_multiprocessing()
        return
    def shutdown_core(self):
        self.core.shutdown_core()
        return
    def run_agregate(self):
        # Start aggregator
        print("Starting Aggregator...")
        agg = Agregator(self.agregator_queue, self.output_queue, self.config["processing"]["stateful_tasks"]["running_average_window_size"])
        self.agg_process = mp.Process(target=agg.agregate)
        self.agg_process.start()
        return
    def shutdown_agregate(self):
        self.agregator_queue.put(None)
        self.agg_process.join()

    def shutdown_all(self):
        def shutdown(self):
            self.shutdown_input()
            self.shutdown_core()
            self.shutdown_agregate()
            self.shutdown_telemetry()
            self.shutdown_output()
            return
        shutdown_manager = threading.Thread(target=shutdown, args=(self,))
        shutdown_manager.daemon = True
        shutdown_manager.start()

        shutdown_manager.join()

    def run_output(self):

        self.gui_process = mp.Process(target=worker, args=(self.output_queue,))
        self.gui_process.start()
        return

    def shutdown_output(self):
        # Signal output consumers to shutdown
        self.output_queue.put(None)
        self.gui_process.join()


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
    pipeline = Pipeline(config)
    try:
        pipeline.bootstrap()
    except KeyboardInterrupt:
        print("\n[MAIN] Pipeline gracefully terminated by user (Ctrl+C).")
        for p in mp.active_children():
            p.terminate()

    print("\n" + "=" * 70)
    print("  Pipeline Complete")
    print("=" * 70 + "\n")


if __name__ == "__main__":
    bootstrap()





