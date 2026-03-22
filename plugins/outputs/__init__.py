"""
Phase 3 Output Module

Provides real-time output consumers that display processed results:
- ConsoleConsumer: Real-time console output with statistics
- GUIConsumer: Matplotlib dashboard with live graphs

Both consumers run as independent processes, reading from output_queue
and displaying running averages as they arrive.
"""

from .base_consumer import BaseOutputConsumer, OutputConsumerError
from .console_consumer import ConsoleConsumer
from .gui_dashboard import GUIConsumer

__all__ = [
    'BaseOutputConsumer',
    'OutputConsumerError',
    'ConsoleConsumer',
    'GUIConsumer',
]
