"""
Core module for window control and manipulation.
"""

import win32gui
import win32con
from typing import Tuple, Optional
from .window_detector import WindowInfo


class WindowController:
    """Handles window control and manipulation."""
    
    def __init__(self):
        self.window_states = {}  # Store original window states for undo
    
    def save_window_state(self, hwnd: int) -> None:
        """Save current window state for undo functionality."""
        try:
            rect = win32gui.GetWindowRect(hwnd)
            placement = win32gui.GetWindowPlacement(hwnd)
            self.window_states[hwnd] = {
                'rect': rect,
                'placement': placement
            }
        except:
            pass
    
    def restore_window_state(self, hwnd: int) -> bool:
        """Restore window to previously saved state."""
        if hwnd not in self.window_states:
            return False
            
        try:
            state = self.window_states[hwnd]
            win32gui.SetWindowPlacement(hwnd, state['placement'])
            return True
        except:
            return False
    
    def move_window(self, hwnd: int, x: int, y: int, width: int, height: int) -> bool:
        """Move and resize window."""
        try:
            # Save current state before moving
            self.save_window_state(hwnd)
            
            # Ensure window is not minimized
            if win32gui.IsIconic(hwnd):
                win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
            
            # Move and resize window
            win32gui.SetWindowPos(
                hwnd,
                win32con.HWND_TOP,
                x, y, width, height,
                win32con.SWP_SHOWWINDOW
            )
            return True
        except:
            return False
    
    def bring_to_front(self, hwnd: int) -> bool:
        """Bring window to front."""
        try:
            win32gui.SetForegroundWindow(hwnd)
            return True
        except:
            return False
    
    def minimize_window(self, hwnd: int) -> bool:
        """Minimize window."""
        try:
            win32gui.ShowWindow(hwnd, win32con.SW_MINIMIZE)
            return True
        except:
            return False
    
    def maximize_window(self, hwnd: int) -> bool:
        """Maximize window."""
        try:
            win32gui.ShowWindow(hwnd, win32con.SW_MAXIMIZE)
            return True
        except:
            return False
    
    def restore_window(self, hwnd: int) -> bool:
        """Restore window from minimized/maximized state."""
        try:
            win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
            return True
        except:
            return False
    
    def get_window_rect(self, hwnd: int) -> Optional[Tuple[int, int, int, int]]:
        """Get window rectangle."""
        try:
            return win32gui.GetWindowRect(hwnd)
        except:
            return None
    
    def is_window_minimized(self, hwnd: int) -> bool:
        """Check if window is minimized."""
        try:
            return win32gui.IsIconic(hwnd)
        except:
            return False
    
    def is_window_maximized(self, hwnd: int) -> bool:
        """Check if window is maximized."""
        try:
            placement = win32gui.GetWindowPlacement(hwnd)
            # SW_MAXIMIZE = 3
            return placement[1] == 3
        except:
            return False