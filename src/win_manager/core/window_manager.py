"""
Main window manager that coordinates all components.
"""

import logging
from typing import List, Dict, Optional, Tuple
from .window_detector import WindowDetector, WindowInfo
from .window_controller import WindowController
from .layout_manager import LayoutEngine
from .config_manager import ConfigManager


class WindowManager:
    """Main window manager class."""
    
    def __init__(self):
        self.detector = WindowDetector()
        self.controller = WindowController()
        self.layout_engine = LayoutEngine()
        self.config = ConfigManager()
        
        # Setup logging
        log_level = getattr(logging, self.config.get("advanced.log_level", "INFO"))
        logging.basicConfig(level=log_level)
        self.logger = logging.getLogger(__name__)
    
    def get_manageable_windows(self) -> List[WindowInfo]:
        """Get list of windows that can be managed."""
        all_windows = self.detector.enumerate_windows()
        manageable_windows = []
        
        ignore_fixed_size = self.config.get("filters.ignore_fixed_size", True)
        ignore_minimized = self.config.get("filters.ignore_minimized", True)
        excluded_processes = self.config.get_excluded_processes()
        
        for window in all_windows:
            # Skip excluded processes
            if window.process_name.lower() in [p.lower() for p in excluded_processes]:
                continue
            
            # Skip fixed size windows if configured
            if ignore_fixed_size and not window.is_resizable:
                continue
            
            # Skip minimized windows if configured
            if ignore_minimized and self.controller.is_window_minimized(window.hwnd):
                continue
            
            # Skip windows that are too small (likely UI elements)
            left, top, right, bottom = window.rect
            if (right - left) < 100 or (bottom - top) < 100:
                continue
            
            manageable_windows.append(window)
        
        return manageable_windows
    
    def organize_windows(self, layout_name: Optional[str] = None, **layout_options) -> bool:
        """Organize windows using specified layout."""
        if layout_name is None:
            layout_name = self.config.get("window_management.default_layout", "cascade")
        
        try:
            # Get manageable windows
            windows = self.get_manageable_windows()
            
            if not windows:
                self.logger.info("No manageable windows found")
                return False
            
            # Calculate positions
            positions = self.layout_engine.apply_layout(layout_name, windows, **layout_options)
            
            # Apply positions
            success_count = 0
            for hwnd, (x, y, width, height) in positions.items():
                if self.controller.move_window(hwnd, x, y, width, height):
                    success_count += 1
                else:
                    self.logger.warning(f"Failed to move window {hwnd}")
            
            self.logger.info(f"Successfully organized {success_count}/{len(windows)} windows using {layout_name} layout")
            return success_count > 0
            
        except Exception as e:
            self.logger.error(f"Error organizing windows: {e}")
            return False
    
    def cascade_windows(self) -> bool:
        """Organize windows in cascade layout."""
        return self.organize_windows("cascade")
    
    def grid_windows(self) -> bool:
        """Organize windows in grid layout."""
        return self.organize_windows("grid")
    
    def stack_windows(self) -> bool:
        """Organize windows in stack layout."""
        return self.organize_windows("stack")
    
    def undo_layout(self) -> bool:
        """Undo last layout change."""
        try:
            windows = self.detector.enumerate_windows()
            success_count = 0
            
            for window in windows:
                if self.controller.restore_window_state(window.hwnd):
                    success_count += 1
            
            self.logger.info(f"Restored {success_count} windows to previous state")
            return success_count > 0
            
        except Exception as e:
            self.logger.error(f"Error undoing layout: {e}")
            return False
    
    def get_window_list(self) -> List[Dict[str, any]]:
        """Get list of all windows with their information."""
        windows = self.detector.enumerate_windows()
        window_list = []
        
        for window in windows:
            window_dict = {
                "hwnd": window.hwnd,
                "title": window.title,
                "process_name": window.process_name,
                "pid": window.pid,
                "rect": window.rect,
                "is_visible": window.is_visible,
                "is_resizable": window.is_resizable,
                "is_minimized": self.controller.is_window_minimized(window.hwnd),
                "is_maximized": self.controller.is_window_maximized(window.hwnd)
            }
            window_list.append(window_dict)
        
        return window_list
    
    def focus_window(self, hwnd: int) -> bool:
        """Bring window to front."""
        return self.controller.bring_to_front(hwnd)
    
    def minimize_window(self, hwnd: int) -> bool:
        """Minimize window."""
        return self.controller.minimize_window(hwnd)
    
    def maximize_window(self, hwnd: int) -> bool:
        """Maximize window."""
        return self.controller.maximize_window(hwnd)
    
    def restore_window(self, hwnd: int) -> bool:
        """Restore window."""
        return self.controller.restore_window(hwnd)
    
    def get_available_layouts(self) -> List[str]:
        """Get list of available layouts."""
        return self.layout_engine.get_available_layouts()
    
    def save_config(self) -> bool:
        """Save current configuration."""
        return self.config.save_config()
    
    def get_config(self) -> ConfigManager:
        """Get configuration manager."""
        return self.config