"""
Core module for window detection and enumeration.
"""

import win32gui
import win32con
import win32process
import psutil
from typing import List, Dict, NamedTuple, Optional


class WindowInfo(NamedTuple):
    """Window information structure."""
    hwnd: int
    title: str
    process_name: str
    pid: int
    rect: tuple  # (left, top, right, bottom)
    is_visible: bool
    is_resizable: bool


class WindowDetector:
    """Handles window detection and enumeration."""
    
    def __init__(self):
        self.windows: List[WindowInfo] = []
    
    def enumerate_windows(self) -> List[WindowInfo]:
        """Enumerate all visible windows."""
        self.windows = []
        win32gui.EnumWindows(self._enum_windows_callback, None)
        return self.windows
    
    def _enum_windows_callback(self, hwnd: int, param) -> bool:
        """Callback for window enumeration."""
        if not win32gui.IsWindowVisible(hwnd):
            return True
            
        title = win32gui.GetWindowText(hwnd)
        if not title:
            return True
            
        try:
            _, pid = win32process.GetWindowThreadProcessId(hwnd)
            process = psutil.Process(pid)
            process_name = process.name()
            
            rect = win32gui.GetWindowRect(hwnd)
            is_resizable = self._is_window_resizable(hwnd)
            
            window_info = WindowInfo(
                hwnd=hwnd,
                title=title,
                process_name=process_name,
                pid=pid,
                rect=rect,
                is_visible=True,
                is_resizable=is_resizable
            )
            
            self.windows.append(window_info)
            
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass
            
        return True
    
    def _is_window_resizable(self, hwnd: int) -> bool:
        """Check if window is resizable."""
        try:
            style = win32gui.GetWindowLong(hwnd, win32con.GWL_STYLE)
            return bool(style & win32con.WS_THICKFRAME)
        except:
            return False
    
    def get_window_by_title(self, title: str) -> Optional[WindowInfo]:
        """Get window by title."""
        for window in self.windows:
            if title.lower() in window.title.lower():
                return window
        return None
    
    def get_resizable_windows(self) -> List[WindowInfo]:
        """Get only resizable windows."""
        return [w for w in self.windows if w.is_resizable]