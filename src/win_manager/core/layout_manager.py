"""
Layout management system for window arrangements.
"""

import win32api
from typing import List, Dict, Tuple, Optional
from abc import ABC, abstractmethod
from ..core.window_detector import WindowInfo


class LayoutManager(ABC):
    """Abstract base class for layout managers."""
    
    @abstractmethod
    def calculate_positions(self, windows: List[WindowInfo], screen_rect: Tuple[int, int, int, int]) -> Dict[int, Tuple[int, int, int, int]]:
        """Calculate positions for windows."""
        pass


class CascadeLayout(LayoutManager):
    """Cascade layout - windows stacked with offset."""
    
    def __init__(self, offset_x: int = 30, offset_y: int = 30):
        self.offset_x = offset_x
        self.offset_y = offset_y
    
    def calculate_positions(self, windows: List[WindowInfo], screen_rect: Tuple[int, int, int, int]) -> Dict[int, Tuple[int, int, int, int]]:
        """Calculate cascade positions."""
        positions = {}
        screen_left, screen_top, screen_right, screen_bottom = screen_rect
        
        # Calculate window size (70% of screen)
        window_width = int((screen_right - screen_left) * 0.7)
        window_height = int((screen_bottom - screen_top) * 0.7)
        
        for i, window in enumerate(windows):
            x = screen_left + (i * self.offset_x)
            y = screen_top + (i * self.offset_y)
            
            # Ensure window doesn't go off screen
            if x + window_width > screen_right:
                x = screen_left
            if y + window_height > screen_bottom:
                y = screen_top
            
            positions[window.hwnd] = (x, y, window_width, window_height)
        
        return positions


class GridLayout(LayoutManager):
    """Grid layout - windows arranged in a grid."""
    
    def __init__(self, columns: Optional[int] = None, padding: int = 10):
        self.columns = columns
        self.padding = padding
    
    def calculate_positions(self, windows: List[WindowInfo], screen_rect: Tuple[int, int, int, int]) -> Dict[int, Tuple[int, int, int, int]]:
        """Calculate grid positions."""
        positions = {}
        screen_left, screen_top, screen_right, screen_bottom = screen_rect
        
        window_count = len(windows)
        if window_count == 0:
            return positions
        
        # Calculate grid dimensions
        if self.columns is None:
            columns = int(window_count ** 0.5) + 1
        else:
            columns = self.columns
        
        rows = (window_count + columns - 1) // columns
        
        # Calculate window size
        available_width = screen_right - screen_left - (self.padding * (columns + 1))
        available_height = screen_bottom - screen_top - (self.padding * (rows + 1))
        
        window_width = available_width // columns
        window_height = available_height // rows
        
        for i, window in enumerate(windows):
            row = i // columns
            col = i % columns
            
            x = screen_left + self.padding + col * (window_width + self.padding)
            y = screen_top + self.padding + row * (window_height + self.padding)
            
            positions[window.hwnd] = (x, y, window_width, window_height)
        
        return positions


class StackLayout(LayoutManager):
    """Stack layout - windows stacked on top of each other."""
    
    def __init__(self, stack_position: str = "center", window_width: Optional[Dict] = None, window_height: Optional[Dict] = None):
        self.stack_position = stack_position  # "center", "left", "right"
        self.window_width = window_width
        self.window_height = window_height
    
    def calculate_positions(self, windows: List[WindowInfo], screen_rect: Tuple[int, int, int, int]) -> Dict[int, Tuple[int, int, int, int]]:
        """Calculate stack positions."""
        positions = {}
        screen_left, screen_top, screen_right, screen_bottom = screen_rect
        screen_width = screen_right - screen_left
        screen_height = screen_bottom - screen_top
        
        # Calculate window size - use custom size if provided, otherwise 80% of screen
        if self.window_width is not None:
            if self.window_width['type'] == 'percentage':
                window_width = int(screen_width * self.window_width['value'] / 100)
            else:  # pixels
                window_width = self.window_width['value']
        else:
            window_width = int(screen_width * 0.8)
            
        if self.window_height is not None:
            if self.window_height['type'] == 'percentage':
                window_height = int(screen_height * self.window_height['value'] / 100)
            else:  # pixels
                window_height = self.window_height['value']
        else:
            window_height = int(screen_height * 0.8)
        
        # Calculate position based on stack_position
        if self.stack_position == "center":
            x = screen_left + (screen_right - screen_left - window_width) // 2
            y = screen_top + (screen_bottom - screen_top - window_height) // 2
        elif self.stack_position == "left":
            x = screen_left + 50
            y = screen_top + 50
        elif self.stack_position == "right":
            x = screen_right - window_width - 50
            y = screen_top + 50
        else:
            x = screen_left + 50
            y = screen_top + 50
        
        # All windows get the same position (stacked)
        for window in windows:
            positions[window.hwnd] = (x, y, window_width, window_height)
        
        return positions


class LayoutEngine:
    """Main layout engine that manages different layout types."""
    
    def __init__(self):
        self.layouts = {
            "cascade": CascadeLayout(),
            "grid": GridLayout(),
            "stack": StackLayout()
        }
    
    def get_screen_rect(self) -> Tuple[int, int, int, int]:
        """Get primary screen rectangle."""
        return (0, 0, win32api.GetSystemMetrics(0), win32api.GetSystemMetrics(1))
    
    def apply_layout(self, layout_name: str, windows: List[WindowInfo], **layout_options) -> Dict[int, Tuple[int, int, int, int]]:
        """Apply layout to windows."""
        if layout_name not in self.layouts:
            raise ValueError(f"Unknown layout: {layout_name}")
        
        layout = self.layouts[layout_name]
        
        # Create a new instance with custom options for certain layouts
        if layout_name == "stack":
            stack_position = layout_options.get("stack_position", "center")
            window_width = layout_options.get("window_width")
            window_height = layout_options.get("window_height")
            layout = StackLayout(stack_position=stack_position, window_width=window_width, window_height=window_height)
        elif layout_name == "grid" and ("columns" in layout_options or "padding" in layout_options):
            columns = layout_options.get("columns", 3)
            padding = layout_options.get("padding", 10)
            layout = GridLayout(columns=columns, padding=padding)
        elif layout_name == "cascade" and ("offset_x" in layout_options or "offset_y" in layout_options):
            offset_x = layout_options.get("offset_x", 30)
            offset_y = layout_options.get("offset_y", 30)
            layout = CascadeLayout(offset_x=offset_x, offset_y=offset_y)
        
        screen_rect = self.get_screen_rect()
        
        return layout.calculate_positions(windows, screen_rect)
    
    def add_custom_layout(self, name: str, layout: LayoutManager):
        """Add custom layout."""
        self.layouts[name] = layout
    
    def get_available_layouts(self) -> List[str]:
        """Get list of available layouts."""
        return list(self.layouts.keys())