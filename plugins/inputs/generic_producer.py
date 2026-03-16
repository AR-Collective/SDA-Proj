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

# Add project root to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))



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
        config: Full config.json dict
        queue1: multiprocessing.Queue to put packets into
        schema_mapper: SchemaMapper instance for column mapping
        shutdown_requested: Flag to check for graceful shutdown
    """

    def __init__(self, config: Dict[str, Any], queue1: Queue):
        """
        Initialize the input producer.

        Args:
            config: Full config.json as dict
            queue1: multiprocessing.Queue(maxsize=50) to put packets into

        Raises:
            ProducerError: If config is invalid
        """
        self.config = config
        self.queue1 = queue1
        self.shutdown_requested = False

        # Validate config early
        validator = InputValidator(config)
        is_valid, message = validator.validate_all()
        if not is_valid:
            logger.error(f"Config validation failed:\n{message}")
            raise ProducerError(f"Invalid config: {message}")

        logger.info(f"✓ Config validation passed")

        # Initialize schema mapper
        try:
            self.schema_mapper = SchemaMapper(config["schema_mapping"])
            logger.info(f"✓ Schema mapper initialized with {len(self.schema_mapper.columns)} columns")
        except Exception as e:
            logger.error(f"Failed to initialize schema mapper: {e}")
            raise ProducerError(f"Schema mapper error: {e}")

        # Extract pipeline config
        self.dataset_path = config["dataset_path"]
        self.input_delay_seconds = config["pipeline_dynamics"]["input_delay_seconds"]
        self.queue_max_size = config["pipeline_dynamics"]["stream_queue_max_size"]

        logger.info(f"Dataset: {self.dataset_path}")
        logger.info(f"Input delay: {self.input_delay_seconds}s")
        logger.info(f"Queue max size: {self.queue_max_size}")

    def _setup_signal_handlers(self) -> None:
        """Setup handlers for graceful shutdown on Ctrl+C."""
        def signal_handler(signum, frame):
            logger.info("Shutdown signal received, stopping producer...")
            self.shutdown_requested = True

        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)

    def _read_csv_rows(self) -> Generator[Dict[str, Any], None, None]:
        """
        Read CSV file row by row (streaming).

        Yields:
            Dict with CSV column names as keys (raw strings)

        Raises:
            ProducerError: If CSV cannot be read
        """
        path = Path(self.dataset_path)

        try:
            with open(path, 'r', encoding='utf-8') as f:
                reader = csv_module.DictReader(f)

                if reader.fieldnames is None:
                    raise ProducerError(f"Cannot read CSV headers from {path}")

                # Log CSV structure
                logger.info(f"✓ CSV opened, columns: {reader.fieldnames}")

                row_number = 0
                for row in reader:
                    if self.shutdown_requested:
                        logger.info(f"Shutdown requested after {row_number} rows")
                        return

                    row_number += 1
                    yield row

                logger.info(f"✓ Finished reading {row_number} rows from CSV")

        except FileNotFoundError:
            raise ProducerError(f"Dataset file not found: {path}")
        except Exception as e:
            raise ProducerError(f"Error reading CSV: {e}")

    def _process_row(self, raw_row: Dict[str, Any], row_number: int) -> Optional[Dict[str, Any]]:
        """
        Process a single row: map columns and cast types.

        Args:
            raw_row: Row from CSV (all values are strings)
            row_number: Row number in CSV (for logging)

        Returns:
            Processed packet (or None if error)
        """
        try:
            # Map columns to internal names and cast types
            packet = self.schema_mapper.process_row(raw_row)

            # Add metadata
            packet["_source_row"] = row_number
            packet["_producer_timestamp"] = time.time()

            return packet

        except SchemaMapperError as e:
            logger.warning(f"Row {row_number}: Failed to process - {e}")
            return None
        except Exception as e:
            logger.warning(f"Row {row_number}: Unexpected error - {e}")
            return None

    def _apply_throttle(self) -> None:
        """Apply input delay throttling."""
        if self.input_delay_seconds > 0:
            time.sleep(self.input_delay_seconds)

    def _queue_packet(self, packet: Dict[str, Any], row_number: int) -> None:
        """
        Put packet into Queue1 with error handling.

        Args:
            packet: Processed row data
            row_number: Row number (for logging)

        Raises:
            ProducerError: If queue operation fails
        """
        try:
            # Put packet into queue (will block if queue is full - natural backpressure)
            if self.queue1 is None:
                raise ProducerError("Queue1 is None - not initialized")

            self.queue1.put(packet, timeout=30)
            logger.debug(f"Row {row_number}: Successfully queued packet")

        except Exception as e:
            import traceback
            error_trace = traceback.format_exc()
            logger.error(f"Row {row_number}: Failed to queue packet")
            logger.error(f"Exception type: {type(e).__name__}")
            logger.error(f"Exception message: {str(e)}")
            logger.error(f"Traceback:\n{error_trace}")
            raise ProducerError(f"Queue error: {str(e)}")

    def run(self) -> None:
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
            for raw_row in self._read_csv_rows():
                if self.shutdown_requested:
                    logger.info("Shutdown requested, exiting main loop")
                    break

                row_number = packets_queued + packets_skipped + 1

                # Process the row
                packet = self._process_row(raw_row, row_number)

                if packet is None:
                    packets_skipped += 1
                    continue

                # Throttle according to config
                self._apply_throttle()

                # Queue the packet (may block if queue is full)
                try:
                    self._queue_packet(packet, row_number)
                    packets_queued += 1
                except ProducerError:
                    logger.error(f"Failed to queue row {row_number}, stopping producer")
                    break

            # Signal end-of-stream to core workers
            logger.info(f"Sending end-of-stream sentinel to queue...")
            self.queue1.put(None, timeout=10)  # None = EOF marker
            logger.info(f"✓ End-of-stream sentinel sent")

        except KeyboardInterrupt:
            logger.info("Producer interrupted by user")
        except Exception as e:
            logger.error(f"Producer error: {e}")
            # Send EOF marker even on error
            try:
                self.queue1.put(None, timeout=5)
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

    def run_single_batch(self, batch_size: int = 10) -> list:
        """
        Process a single batch of rows (useful for testing).

        Args:
            batch_size: Number of rows to process before returning

        Returns:
            List of processed packets
        """
        packets = []

        try:
            for raw_row in self._read_csv_rows():
                if len(packets) >= batch_size:
                    break

                row_number = len(packets) + 1
                packet = self._process_row(raw_row, row_number)

                if packet is None:
                    continue

                packets.append(packet)

            logger.info(f"✓ Processed {len(packets)} packets")
            return packets

        except Exception as e:
            logger.error(f"Error in batch processing: {e}")
            return packets


