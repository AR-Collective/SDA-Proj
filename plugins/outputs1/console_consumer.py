"""
Console Output Consumer for Phase 3

Real-time console output showing running averages, statistics,
and formatted metrics as they arrive from the processing pipeline.
"""

import logging
from .base_consumer import BaseOutputConsumer
from .utils import format_value, format_statistics, format_timestamp


class ConsoleConsumer(BaseOutputConsumer):
    """
    Outputs running averages to console in real-time.

    Displays:
    - Current running average value
    - Count of values processed
    - Min/max values seen
    - Average of all values
    - Elapsed time
    """

    def __init__(self, output_queue, window_size: int = 100):
        """
        Initialize console consumer.

        Args:
            output_queue: multiprocessing.Queue receiving float values
            window_size: Number of recent values to track
        """
        super().__init__(output_queue, window_size)
        self.logger = logging.getLogger("ConsoleConsumer")

    def on_start(self) -> None:
        """Print startup message."""
        print("\n" + "=" * 60)
        print("  CONSOLE OUTPUT CONSUMER STARTED")
        print("=" * 60)
        print("Waiting for values from output queue...\n")
        self.logger.info("Console consumer ready")

    def on_value_received(self, value: float) -> None:
        """
        Display the received value and current statistics.

        Args:
            value: Running average value from queue
        """
        # Format and display current value with context
        self._display_update(value)

    def _display_update(self, value: float) -> None:
        """
        Display a formatted update with current value and statistics.

        Args:
            value: The value to display
        """
        stats = self.get_statistics()

        # Create display output
        lines = [
            f"\n[{format_timestamp()}] Value #{stats['count']}",
            f"  Current:  {format_value(value, decimals=4)}",
            f"  Average:  {format_value(stats['average'], decimals=4)}  " +
            f"(min: {format_value(stats['min'], decimals=2)}, " +
            f"max: {format_value(stats['max'], decimals=2)})",
        ]

        # Print in one block to avoid interleaving in multiprocess scenario
        print("\n".join(lines))

    def on_shutdown(self) -> None:
        """Print shutdown summary with final statistics."""
        stats = self.get_statistics()

        print("\n" + "=" * 60)
        print("  CONSOLE CONSUMER SHUTTING DOWN")
        print("=" * 60)
        print(format_statistics(stats))
        print("\nFinal result:")
        print(f"  Total values processed: {stats['count']}")
        if stats['current'] is not None:
            print(f"  Final value: {format_value(stats['current'], decimals=4)}")
        if stats['average'] is not None:
            print(f"  Average: {format_value(stats['average'], decimals=4)}")
        if stats['min'] is not None:
            print(f"  Range: {format_value(stats['min'], decimals=2)} - " +
                  f"{format_value(stats['max'], decimals=2)}")
        print("=" * 60 + "\n")

        self.logger.info("Console consumer shutdown complete")
