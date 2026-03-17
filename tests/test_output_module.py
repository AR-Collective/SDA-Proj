"""
Tests for output module (plugins/outputs/)

Tests the output consumers and utilities for Phase 3.
"""

import pytest
import sys
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
from multiprocessing import Queue
import time

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from plugins.outputs.base_consumer import BaseOutputConsumer, OutputConsumerError
from plugins.outputs.console_consumer import ConsoleConsumer
try:
    from plugins.outputs.gui_dashboard import GUIConsumer
    HAS_GUI = True
except ImportError:
    HAS_GUI = False
from plugins.outputs.utils import (
    format_value, format_statistics, format_duration,
    format_timestamp, clamp
)


class TestUtilities:
    """Test utility functions."""

    def test_format_value_float(self):
        """Test formatting a float value."""
        result = format_value(3.14159, decimals=2)
        assert result == "3.14"

    def test_format_value_none(self):
        """Test formatting None."""
        result = format_value(None)
        assert result == "N/A"

    def test_format_value_int(self):
        """Test formatting an integer."""
        result = format_value(42, decimals=1)
        assert result == "42.0"

    def test_format_duration_seconds(self):
        """Test duration formatting for seconds."""
        result = format_duration(45)
        assert "45s" in result

    def test_format_duration_minutes(self):
        """Test duration formatting for minutes."""
        result = format_duration(125)  # 2 min 5 sec
        assert "2m" in result and "5s" in result

    def test_format_timestamp(self):
        """Test timestamp formatting."""
        result = format_timestamp()
        # Should be in format YYYY-MM-DD HH:MM:SS
        parts = result.split()
        assert len(parts) == 2
        assert len(parts[0]) == 10  # YYYY-MM-DD
        assert len(parts[1]) == 8   # HH:MM:SS

    def test_format_statistics(self):
        """Test statistics formatting."""
        stats = {
            'count': 10,
            'min': 1.5,
            'max': 9.8,
            'current': 5.2,
            'average': 5.5,
            'duration': 30
        }
        result = format_statistics(stats)
        assert 'STATISTICS' in result.upper()
        assert '10' in result
        assert '5.50' in result or '5.5' in result

    def test_clamp(self):
        """Test value clamping."""
        assert clamp(5, 0, 10) == 5
        assert clamp(-5, 0, 10) == 0
        assert clamp(15, 0, 10) == 10


class ConcreteOutputConsumer(BaseOutputConsumer):
    """Concrete implementation for testing abstract base class."""

    def __init__(self, output_queue, window_size=100):
        super().__init__(output_queue, window_size)
        self.start_called = False
        self.shutdown_called = False
        self.values_received = []

    def on_start(self):
        self.start_called = True

    def on_value_received(self, value):
        self.values_received.append(value)

    def on_shutdown(self):
        self.shutdown_called = True


class TestBaseOutputConsumer:
    """Test BaseOutputConsumer functionality."""

    def test_initialization(self):
        """Test consumer initialization."""
        queue = Queue()
        consumer = ConcreteOutputConsumer(queue)

        assert consumer.queue is queue
        assert consumer.count == 0
        assert consumer.current_value is None
        assert consumer.min_value == float('inf')
        assert consumer.max_value == float('-inf')

    def test_statistics_empty(self):
        """Test statistics when no values received."""
        queue = Queue()
        consumer = ConcreteOutputConsumer(queue)

        stats = consumer.get_statistics()
        assert stats['count'] == 0
        assert stats['min'] is None
        assert stats['max'] is None
        assert stats['current'] is None

    def test_update_stats_single_value(self):
        """Test statistics update with single value."""
        queue = Queue()
        consumer = ConcreteOutputConsumer(queue)

        consumer._update_stats(5.5)

        assert consumer.count == 1
        assert consumer.current_value == 5.5
        assert consumer.min_value == 5.5
        assert consumer.max_value == 5.5

    def test_update_stats_multiple_values(self):
        """Test statistics tracking multiple values."""
        queue = Queue()
        consumer = ConcreteOutputConsumer(queue)

        values = [2.0, 5.0, 3.0, 8.0, 1.0]
        for v in values:
            consumer._update_stats(v)

        assert consumer.count == 5
        assert consumer.current_value == 1.0
        assert consumer.min_value == 1.0
        assert consumer.max_value == 8.0

    def test_statistics_calculation(self):
        """Test correct statistics calculation."""
        queue = Queue()
        consumer = ConcreteOutputConsumer(queue)

        values = [2.0, 4.0, 6.0]
        for v in values:
            consumer._update_stats(v)

        stats = consumer.get_statistics()
        assert stats['count'] == 3
        assert stats['min'] == 2.0
        assert stats['max'] == 6.0
        assert stats['average'] == 4.0  # (2+4+6)/3

    def test_history_window(self):
        """Test history maintains window size limit."""
        queue = Queue()
        consumer = ConcreteOutputConsumer(queue, window_size=3)

        values = [1.0, 2.0, 3.0, 4.0, 5.0]
        for v in values:
            consumer._update_stats(v)

        history = consumer.get_history()
        assert len(history) == 3  # Only last 3 values
        assert history == [3.0, 4.0, 5.0]

    def test_invalid_value_type(self):
        """Test error handling for invalid value type."""
        queue = Queue()
        consumer = ConcreteOutputConsumer(queue)

        with pytest.raises(ValueError):
            consumer._update_stats("not a number")

    def test_request_shutdown(self):
        """Test shutdown request."""
        queue = Queue()
        consumer = ConcreteOutputConsumer(queue)

        assert consumer.shutdown_requested is False
        consumer.request_shutdown()
        assert consumer.shutdown_requested is True


class TestConsoleConsumer:
    """Test ConsoleConsumer functionality."""

    def test_initialization(self):
        """Test ConsoleConsumer initialization."""
        queue = Queue()
        consumer = ConsoleConsumer(queue)

        assert consumer.queue is queue
        assert consumer.count == 0

    def test_on_start_called(self):
        """Test that on_start is called."""
        queue = Queue()
        consumer = ConsoleConsumer(queue)

        with patch('builtins.print'):
            consumer.on_start()
            # Should not raise any errors

    def test_statistics_display_ready(self):
        """Test that statistics can be formatted for display."""
        queue = Queue()
        consumer = ConsoleConsumer(queue)

        # Add some values
        for v in [1.0, 2.5, 3.8, 2.1]:
            consumer._update_stats(v)

        stats = consumer.get_statistics()
        formatted = format_statistics(stats)

        # Should contain relevant info
        assert 'STATISTICS' in formatted.upper()
        assert '4' in formatted  # count

    def test_console_output_format(self):
        """Test console output formatting."""
        queue = Queue()
        consumer = ConsoleConsumer(queue)

        for v in [2.0, 4.0, 6.0]:
            consumer._update_stats(v)

        stats = consumer.get_statistics()
        # Verify stats are reasonable
        assert stats['count'] == 3
        assert stats['average'] == 4.0


class TestGUIConsumer:
    """Test GUIConsumer functionality (mocked matplotlib)."""

    @pytest.mark.skipif(not HAS_GUI, reason="Matplotlib not installed")
    def test_gui_initialization(self):
        """Test GUIConsumer initialization."""
        queue = Queue()
        consumer = GUIConsumer(queue)
        assert consumer.queue is queue
        assert consumer.count == 0

    @pytest.mark.skipif(not HAS_GUI, reason="Matplotlib not installed")
    def test_gui_graceful_import_error(self):
        """Test that GUIConsumer handles missing matplotlib gracefully."""
        queue = Queue()

        # Patch matplotlib import to fail
        with patch('plugins.outputs.gui_dashboard.HAS_MATPLOTLIB', False):
            with pytest.raises(ImportError):
                GUIConsumer(queue)


class TestOutputConsumerIntegration:
    """Integration tests for output consumers."""

    def test_consumer_with_real_queue(self):
        """Test consumer with actual multiprocessing.Queue."""
        queue = Queue(maxsize=10)
        consumer = ConcreteOutputConsumer(queue)

        # Manually add some values to testthe consumer logic
        test_values = [1.5, 2.5, 3.5, 4.5, 5.5]

        # Simulate queue consumption (without actual multiprocessing)
        for v in test_values:
            consumer._update_stats(v)
            consumer.on_value_received(v)

        assert consumer.count == 5
        assert len(consumer.values_received) == 5
        assert consumer.get_statistics()['average'] == 3.5

    def test_statistics_with_single_value(self):
        """Test statistics edge case with single value."""
        queue = Queue()
        consumer = ConcreteOutputConsumer(queue)

        consumer._update_stats(42.0)
        stats = consumer.get_statistics()

        assert stats['count'] == 1
        assert stats['min'] == 42.0
        assert stats['max'] == 42.0
        assert stats['average'] == 42.0

    def test_large_number_of_values(self):
        """Test consumer handling many values."""
        queue = Queue()
        consumer = ConcreteOutputConsumer(queue, window_size=1000)

        # Add 500 sequential values
        for i in range(1, 501):
            consumer._update_stats(float(i))

        stats = consumer.get_statistics()
        assert stats['count'] == 500
        assert stats['min'] == 1.0
        assert stats['max'] == 500.0
        assert 250 < stats['average'] < 251  # Should be around 250.5
