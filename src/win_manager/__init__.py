"""
Win-Manager: A Windows system or window management tool.

This package provides intelligent window management capabilities for Windows,
including automatic layout organization, window detection, and configuration management.
"""

from .core.window_manager import WindowManager
from .core.window_detector import WindowDetector, WindowInfo
from .core.window_controller import WindowController
from .core.layout_manager import LayoutEngine
from .core.config_manager import ConfigManager

__version__ = "0.1.0"
__author__ = "Your Name"
__email__ = "your.email@example.com"

__all__ = [
    "WindowManager",
    "WindowDetector",
    "WindowInfo",
    "WindowController", 
    "LayoutEngine",
    "ConfigManager",
    "__version__"
]