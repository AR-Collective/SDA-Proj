"""
Output Plugins Module

Provides output drivers for writing analysis results in various formats.
Each driver implements the DataSink protocol from core/contracts.py
"""

from .console_writer import ConsoleWriter
from .graphics_writer import GraphicsChartWriter

__all__ = ['ConsoleWriter', 'GraphicsChartWriter']
