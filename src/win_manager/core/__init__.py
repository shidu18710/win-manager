"""
Core module initialization.
"""

from .window_detector import WindowDetector, WindowInfo
from .window_controller import WindowController
from .layout_manager import LayoutEngine, CascadeLayout, GridLayout, StackLayout
from .config_manager import ConfigManager
from .window_manager import WindowManager

__all__ = [
    "WindowDetector",
    "WindowInfo", 
    "WindowController",
    "LayoutEngine",
    "CascadeLayout",
    "GridLayout", 
    "StackLayout",
    "ConfigManager",
    "WindowManager"
]