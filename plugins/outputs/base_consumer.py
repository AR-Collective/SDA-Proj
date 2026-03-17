"""
Base Output Consumer for Phase 3

Provides base class for output consumers that read from multiprocessing queues.
Handles poison pill shutdown, statistics tracking, and graceful error handling.

All output consumers extend this class to implement specific output formats
(console, GUI, database, etc.) while sharing queue consumption logic.
"""

import logging
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from multiprocessing import Queue
from collections import deque
import time

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='[%(name)s] %(levelname)s: %(message)s'
)


class OutputConsumerError(Exception):
    """Base exception for output consumer errors."""
    pass


class BaseOutputConsumer(ABC):
    """
    Abstract base class for output consumers.

    Handles:
    - Queue consumption with poison pill pattern
    - Statistics tracking (count, min, max, average)
    - Window-based history for graphing
    - Graceful shutdown

    Subclasses implement display logic by overriding abstract methods.
    """

    def __init__(self, output_queue: Queue, window_size: int = 100):
        """
        Initialize consumer.

        Args:
            output_queue: multiprocessing.Queue receiving float values
            window_size: Number of recent values to keep for history
        """
        self.queue = output_queue
        self.window_size = window_size
        self.logger = logging.getLogger(self.__class__.__name__)

        # Statistics
        self.count = 0
        self.min_value = float('inf')
        self.max_value = float('-inf')
        self.current_value = None
        self.history = deque(maxlen=window_size)
        self.start_time = None
        self.shutdown_requested = False

    def consume(self) -> None:
        """
        Main consumer loop - reads from queue until poison pill (None).

        Implements standard flow for all consumers:
        1. Read value from queue (with timeout)
        2. Update statistics
        3. Call display logic (implemented by subclass)
        4. On None (poison pill), finalize and exit
        """
        self.start_time = time.time()
        self.logger.info(f"✓ Consumer started, reading from queue")
        self.on_start()

        try:
            while not self.shutdown_requested:
                try:
                    # Use timeout to allow non-blocking operation
                    value = self.queue.get(timeout=1)

                    # Check for poison pill (stream end)
                    if value is None:
                        self.logger.info("Poison pill received, shutting down")
                        break

                    # Update statistics
                    self._update_stats(value)

                    # Call subclass display logic
                    self.on_value_received(value)

                except Exception as e:
                    self.logger.error(f"Error processing value: {e}")
                    continue

        except KeyboardInterrupt:
            self.logger.info("Received keyboard interrupt")
        except Exception as e:
            self.logger.error(f"Unexpected error in consumer loop: {e}")
        finally:
            self.on_shutdown()
            self.logger.info("✓ Consumer shutdown complete")

    def _update_stats(self, value: float) -> None:
        """
        Update running statistics.

        Args:
            value: New float value from queue
        """
        if not isinstance(value, (int, float)):
            raise ValueError(f"Expected numeric value, got {type(value)}")

        self.current_value = float(value)
        self.count += 1
        self.min_value = min(self.min_value, value)
        self.max_value = max(self.max_value, value)
        self.history.append(value)

    def get_statistics(self) -> Dict[str, Any]:
        """
        Get current statistics.

        Returns:
            Dict with count, min, max, current, average
        """
        if self.count == 0:
            return {
                "count": 0,
                "min": None,
                "max": None,
                "current": None,
                "average": None,
                "duration": 0
            }

        duration = time.time() - self.start_time if self.start_time else 0
        average = sum(self.history) / len(self.history) if self.history else None

        return {
            "count": self.count,
            "min": self.min_value if self.min_value != float('inf') else None,
            "max": self.max_value if self.max_value != float('-inf') else None,
            "current": self.current_value,
            "average": average,
            "duration": duration
        }

    def get_history(self) -> list:
        """
        Get history of recent values.

        Returns:
            List of float values in chronological order
        """
        return list(self.history)

    @abstractmethod
    def on_start(self) -> None:
        """
        Called when consumer starts.

        Subclasses can initialize display elements here.
        """
        pass

    @abstractmethod
    def on_value_received(self, value: float) -> None:
        """
        Called when a new value is received.

        Subclasses implement display logic here.

        Args:
            value: The float value received from queue
        """
        pass

    @abstractmethod
    def on_shutdown(self) -> None:
        """
        Called when consumer is shutting down.

        Subclasses can finalize display here.
        """
        pass

    def request_shutdown(self) -> None:
        """Request graceful shutdown."""
        self.shutdown_requested = True
