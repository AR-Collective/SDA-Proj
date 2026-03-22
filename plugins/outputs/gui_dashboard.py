"""
GUI Dashboard Output Consumer for Phase 3

Real-time matplotlib-based dashboard displaying:
- Live graph of running averages over time
- Statistics panel (current, min, max, average)
- Auto-updating as values arrive
"""

import logging
try:
    import matplotlib
    matplotlib.use('TkAgg')  # Use Tkinter backend for better compatibility
    import matplotlib.pyplot as plt
    from matplotlib.animation import FuncAnimation
    HAS_MATPLOTLIB = True
except ImportError:
    HAS_MATPLOTLIB = False

from .base_consumer import BaseOutputConsumer
from .utils import format_value


class GUIConsumer(BaseOutputConsumer):
    """
    Displays running averages in a live Matplotlib dashboard.

    Features:
    - Real-time line graph of values over time
    - Statistics panel showing current, min, max, average
    - Auto-updates as new values arrive
    - Graceful handling when window is closed
    """

    def __init__(self, output_queue, window_size: int = 100):
        """
        Initialize GUI consumer.

        Args:
            output_queue: multiprocessing.Queue receiving float values
            window_size: Number of recent values to display
        """
        super().__init__(output_queue, window_size)
        self.logger = logging.getLogger("GUIConsumer")

        if not HAS_MATPLOTLIB:
            self.logger.warning("Matplotlib not available, GUI disabled")
            raise ImportError("Matplotlib required for GUIConsumer")

        self.fig = None
        self.ax_graph = None
        self.ax_stats = None
        self.update_count = 0

    def on_start(self) -> None:
        """Initialize the matplotlib figure and layout."""
        self.logger.info("Initializing GUI dashboard")

        # Create figure with 2 subplots
        self.fig, (self.ax_graph, self.ax_stats) = plt.subplots(
            1, 2,
            figsize=(14, 5),
            num="Real-time Output Dashboard"
        )

        # Configure graph subplot
        self.ax_graph.set_title("Running Averages Over Time", fontsize=12, fontweight='bold')
        self.ax_graph.set_xlabel("Sample #")
        self.ax_graph.set_ylabel("Value")
        self.ax_graph.grid(True, alpha=0.3)

        # Configure stats subplot (disable axes, use for text)
        self.ax_stats.axis('off')
        self.ax_stats.set_title("Statistics", fontsize=12, fontweight='bold')

        plt.tight_layout()

        # Setup close handler
        def on_close_event(event):
            self.logger.info("Window closed, requesting shutdown")
            self.request_shutdown()

        self.fig.canvas.mpl_connect('close_event', on_close_event)

        # Show window
        plt.show(block=False)
        self.logger.info("GUI dashboard ready")

    def on_value_received(self, value: float) -> None:
        """
        Update the dashboard with new value.

        Args:
            value: Running average value from queue
        """
        self.update_count += 1

        # Only update plot every few values for performance
        # (matplotlib updates are expensive)
        if self.update_count % 5 == 0:
            self._update_plot()

    def _update_plot(self) -> None:
        """Update the matplotlib plot with current data."""
        try:
            stats = self.get_statistics()
            history = self.get_history()

            # Update graph
            self.ax_graph.clear()
            if len(history) > 0:
                indices = list(range(len(history)))
                self.ax_graph.plot(
                    indices,
                    history,
                    'b-o',
                    linewidth=2,
                    markersize=4,
                    label='Running Average'
                )
                self.ax_graph.fill_between(indices, history, alpha=0.2)

            self.ax_graph.set_title("Running Averages Over Time", fontsize=12, fontweight='bold')
            self.ax_graph.set_xlabel("Sample #")
            self.ax_graph.set_ylabel("Value")
            self.ax_graph.grid(True, alpha=0.3)
            if len(history) > 0:
                self.ax_graph.legend(loc='upper left')

            # Update statistics panel
            self.ax_stats.clear()
            self.ax_stats.axis('off')
            self._draw_stats_panel(stats)

            # Redraw
            self.fig.canvas.draw_idle()

        except Exception as e:
            self.logger.error(f"Error updating plot: {e}")

    def _draw_stats_panel(self, stats) -> None:
        """
        Draw statistics panel on the right subplot.

        Args:
            stats: Statistics dictionary from get_statistics()
        """
        # Prepare text
        text_lines = [
            "STATISTICS",
            "─" * 30,
            f"Count: {stats['count']}",
            f"",
            f"Current: {format_value(stats['current'], 4)}",
            f"Average: {format_value(stats['average'], 4)}",
            f"",
            f"Min:     {format_value(stats['min'], 4)}",
            f"Max:     {format_value(stats['max'], 4)}",
            f"",
            f"Duration: {self._format_duration(stats['duration'])}",
            "─" * 30,
        ]

        text = "\n".join(text_lines)

        # Display in monospace font
        self.ax_stats.text(
            0.5, 0.5,
            text,
            transform=self.ax_stats.transAxes,
            fontsize=11,
            verticalalignment='center',
            horizontalalignment='center',
            fontfamily='monospace',
            bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5)
        )

        self.ax_stats.set_title("Statistics", fontsize=12, fontweight='bold')

    @staticmethod
    def _format_duration(seconds: float) -> str:
        """Format duration in seconds."""
        if seconds < 60:
            return f"{int(seconds)}s"
        elif seconds < 3600:
            minutes = int(seconds // 60)
            secs = int(seconds % 60)
            return f"{minutes}m {secs}s"
        else:
            hours = int(seconds // 3600)
            minutes = int((seconds % 3600) // 60)
            return f"{hours}h {minutes}m"

    def on_shutdown(self) -> None:
        """Finalize the plot on shutdown."""
        self.logger.info("GUI consumer shutting down")

        # Final update
        self._update_plot()

        # Keep window visible
        try:
            plt.title("Pipeline Complete")
            plt.pause(0.1)  # Allow final render
        except Exception as e:
            self.logger.warning(f"Error in final plot update: {e}")

        self.logger.info("GUI consumer shutdown complete")
