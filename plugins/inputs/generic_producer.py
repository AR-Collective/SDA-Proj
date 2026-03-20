"""
Generic Input Producer for Phase 3 - Reads Data and Queues Packets

This module provides a GenericInputProducer process that:
1. Reads CSV file row by row (streaming)
2. Maps columns to internal generic names via schema_mapper
3. Casts data types according to schema
4. Applies throttling with input_delay_seconds
5. Puts processed packets into Queue1 (bounded queue)
6. Handles graceful shutdown

The producer is completely domain-agnostic - it works with ANY CSV
as long as the schema_mapping in config.json is correct.

Example:
    from multiprocessing import Queue
    config = load_config("config.json")
    queue1 = Queue(maxsize=50)

    producer = GenericInputProducer(config, queue1)
    producer_process = Process(target=producer.run)
    producer_process.start()
"""

from .input_validator import InputValidator
from .schema_mapper import SchemaMapper, SchemaMapperError
import csv as csv_module
import time
import sys
import signal
from pathlib import Path
from typing import Dict, Any, Optional, Generator
from multiprocessing import Queue
import logging
import traceback


# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='[Producer] %(levelname)s: %(message)s'
)
logger = logging.getLogger(__name__)


class ProducerError(Exception):
    """Base exception for producer errors."""
    pass


class GenericInputProducer:
    """
    Produces data packets from CSV and queues them for processing.

    This process runs independently and:
    - Reads CSV row by row
    - Maps columns to internal names
    - Casts data types
    - Applies input delay throttling
    - Queues packets to be processed by core workers
    - Gracefully shuts down on signal

    Attributes:
        config: schema_config only
        queue1: multiprocessing.Queue to put packets into
        schema_mapper: SchemaMapper instance for column mapping
        shutdown_requested: Flag to check for graceful shutdown
    """

    def __init__(self, queue1: Queue, schema_mapping: Dict[str, Any], input_delay: int):
        """
        Initialize the input producer.

        Args:
            config: Full config.json as dict
            queue1: multiprocessing.Queue(maxsize=50) to put packets into

        Raises:
            ProducerError: If config is invalid
        """
        self.config = schema_mapping
        self.input_queue = queue1
        self.shutdown_requested = False
        self.next_id = 0
        self.input_delay = input_delay

        # Initialize schema mapper
        try:
            self.schema_mapper = SchemaMapper(schema_mapping)
            logger.info(f"✓ Schema mapper initialized with {len(self.schema_mapper.columns)} columns")
        except Exception as e:
            logger.error(f"Failed to initialize schema mapper: {e}")
            raise ProducerError(f"Schema mapper error: {e}")


        logger.info(f"Input delay: {self.input_delay}s")

    def _setup_signal_handlers(self) -> None:
        """Setup handlers for graceful shutdown on Ctrl+C."""
        def signal_handler(signum, frame):
            logger.info("Shutdown signal received, stopping producer...")
            self.shutdown_requested = True

        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)

    def _read_csv_rows(self, dataset_path:str) -> Generator[Dict[str, Any], None, None]:
        """
        Read CSV file row by row (streaming).

        Yields:
            Dict with CSV column names as keys (raw strings)

        Raises:
            ProducerError: If CSV cannot be read
        """
        path = Path(dataset_path)

        try:
            with open(path, 'r', encoding='utf-8') as f:
                reader = csv_module.DictReader(f)

                if reader.fieldnames is None:
                    raise ProducerError(f"Cannot read CSV headers from {path}")

                # Log CSV structure
                logger.info(f"✓ CSV opened, columns: {reader.fieldnames}")

                for row in reader:
                    if self.shutdown_requested:
                        logger.info(f"Shutdown requested")
                        return

                    yield row

                logger.info(f"✓ Finished reading from CSV")

        except FileNotFoundError:
            raise ProducerError(f"Dataset file not found: {path}")
        except Exception as e:
            raise ProducerError(f"Error reading CSV: {e}")

    def _process_row(self, raw_row: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Process a single row: map columns and cast types.

        Args:
            raw_row: Row from CSV (all values are strings)

        Returns:
            Processed packet (or None if error)
        """
        try:
            # Map columns to internal names and cast types
            packet = self.schema_mapper.process_row(raw_row)

            # Add metadata
            packet["_id"] = self.next_id
            self.next_id +=1

            return packet

        except SchemaMapperError as e:
            logger.warning(f"Failed to process - {e}")
            return None
        except Exception as e:
            logger.warning(f"Unexpected error - {e}")
            return None

    def _apply_throttle(self) -> None:
        """Apply input delay throttling."""
        if self.input_delay > 0:
            time.sleep(self.input_delay)

    def _queue_packet(self, packet: Dict[str, Any]) -> None:
        """
        Put packet into Queue1 with error handling.

        Args:
            packet: Processed row data

        Raises:
            ProducerError: If queue operation fails
        """

        try:
            # Put packet into queue (will block if queue is full - natural backpressure)
            if self.input_queue is None:
                raise ProducerError("Queue1 is None - not initialized")

            self.input_queue.put(packet, timeout=30)
            logger.debug(f"Row Successfully queued packet")

        except Exception as e:
            error_trace = traceback.format_exc()
            logger.error(f"Exception type: {type(e).__name__}")
            logger.error(f"Exception message: {str(e)}")
            logger.error(f"Traceback:\n{error_trace}")
            raise ProducerError(f"Queue error: {str(e)}")

    def run(self, dataset_path) -> None:
        """
        Main producer loop.

        Reads CSV row by row, processes each row, applies throttling,
        and queues packets for core workers to process.

        This method runs in its own process and will block if queue fills
        (natural backpressure).
        """
        logger.info("=" * 70)
        logger.info("GENERIC INPUT PRODUCER STARTED")
        logger.info("=" * 70)

        self._setup_signal_handlers()

        packets_queued = 0
        packets_skipped = 0

        try:
            # Read CSV and process each row
            for raw_row in self._read_csv_rows(dataset_path):
                if self.shutdown_requested:
                    logger.info("Shutdown requested, exiting main loop")
                    break


                # Process the row
                packet = self._process_row(raw_row)

                if packet is None:
                    packets_skipped += 1
                    continue

                # Throttle according to config
                self._apply_throttle()

                # Queue the packet (may block if queue is full)
                try:
                    self._queue_packet(packet)
                    packets_queued += 1
                except ProducerError:
                    logger.error(f"Failed to queue row stopping producer")
                    break

            try:
                # Dropped timeout to 2 seconds so Ctrl+C shuts down faster
                self.input_queue.put(None, timeout=2)  
                logger.info(f"✓ End-of-stream sentinel sent")
            except Queue.full:
                # Catch the error if workers are dead and queue is maxed out
                logger.warning("Queue full during shutdown, dropping EOF sentinel.")

        except KeyboardInterrupt:
            logger.info("Producer interrupted by user")
        except Exception as e:
            logger.error(f"Producer error: {e}")
            # Send EOF marker even on error
            try:
                self.input_queue.put(None, timeout=5)
            except:
                pass
            raise

        finally:
            logger.info("=" * 70)
            logger.info(f"PRODUCER SHUTDOWN SUMMARY")
            logger.info(f"  Packets queued: {packets_queued}")
            logger.info(f"  Packets skipped (errors): {packets_skipped}")
            logger.info(f"  Total rows processed: {packets_queued + packets_skipped}")
            logger.info("=" * 70)

