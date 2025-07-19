"""
Unit tests for WindowDetector.
"""

import pytest
import os
import sys
from unittest.mock import patch, MagicMock, Mock
from collections import namedtuple

# Add src to path for testing
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from win_manager.core.window_detector import WindowDetector, WindowInfo


class TestWindowDetector:
    """Test suite for WindowDetector class."""
    
    def test_init(self):
        """Test WindowDetector initialization."""
        detector = WindowDetector()
        assert detector.windows == []
        assert isinstance(detector.windows, list)
    
    def test_window_info_structure(self):
        """Test WindowInfo namedtuple structure."""
        window_info = WindowInfo(
            hwnd=12345,
            title="Test Window",
            process_name="test.exe",
            pid=1234,
            rect=(0, 0, 100, 100),
            is_visible=True,
            is_resizable=True
        )
        
        assert window_info.hwnd == 12345
        assert window_info.title == "Test Window"
        assert window_info.process_name == "test.exe"
        assert window_info.pid == 1234
        assert window_info.rect == (0, 0, 100, 100)
        assert window_info.is_visible == True
        assert window_info.is_resizable == True
    
    @patch('win_manager.core.window_detector.win32gui.EnumWindows')
    def test_enumerate_windows(self, mock_enum_windows):
        """Test window enumeration."""
        detector = WindowDetector()
        
        # Mock EnumWindows to call our callback
        def mock_enum_callback(callback, param):
            # Simulate calling callback with some window handles
            callback(12345, param)
            callback(67890, param)
            return True
        
        mock_enum_windows.side_effect = mock_enum_callback
        
        # Mock the callback to add windows
        with patch.object(detector, '_enum_windows_callback') as mock_callback:
            mock_callback.return_value = True
            
            result = detector.enumerate_windows()
            
            # Verify EnumWindows was called
            mock_enum_windows.assert_called_once()
            # Verify callback was called for each window
            assert mock_callback.call_count == 2
            mock_callback.assert_any_call(12345, None)
            mock_callback.assert_any_call(67890, None)
    
    @patch('win_manager.core.window_detector.psutil.Process')
    @patch('win_manager.core.window_detector.win32process.GetWindowThreadProcessId')
    @patch('win_manager.core.window_detector.win32gui.GetWindowRect')
    @patch('win_manager.core.window_detector.win32gui.GetWindowText')
    @patch('win_manager.core.window_detector.win32gui.IsWindowVisible')
    def test_enum_windows_callback_success(self, mock_is_visible, mock_get_text, 
                                          mock_get_rect, mock_get_thread_pid, mock_process):
        """Test successful window enumeration callback."""
        detector = WindowDetector()
        
        # Setup mocks
        mock_is_visible.return_value = True
        mock_get_text.return_value = "Test Window"
        mock_get_rect.return_value = (0, 0, 100, 100)
        mock_get_thread_pid.return_value = (1111, 2222)
        
        # Mock process
        mock_proc = Mock()
        mock_proc.name.return_value = "test.exe"
        mock_process.return_value = mock_proc
        
        # Mock window resizability check
        with patch.object(detector, '_is_window_resizable', return_value=True):
            result = detector._enum_windows_callback(12345, None)
        
        # Verify result
        assert result == True
        assert len(detector.windows) == 1
        
        window = detector.windows[0]
        assert window.hwnd == 12345
        assert window.title == "Test Window"
        assert window.process_name == "test.exe"
        assert window.pid == 2222
        assert window.rect == (0, 0, 100, 100)
        assert window.is_visible == True
        assert window.is_resizable == True
    
    @patch('win_manager.core.window_detector.win32gui.IsWindowVisible')
    def test_enum_windows_callback_invisible(self, mock_is_visible):
        """Test callback with invisible window."""
        detector = WindowDetector()
        
        mock_is_visible.return_value = False
        
        result = detector._enum_windows_callback(12345, None)
        
        assert result == True
        assert len(detector.windows) == 0
    
    @patch('win_manager.core.window_detector.win32gui.GetWindowText')
    @patch('win_manager.core.window_detector.win32gui.IsWindowVisible')
    def test_enum_windows_callback_no_title(self, mock_is_visible, mock_get_text):
        """Test callback with window that has no title."""
        detector = WindowDetector()
        
        mock_is_visible.return_value = True
        mock_get_text.return_value = ""
        
        result = detector._enum_windows_callback(12345, None)
        
        assert result == True
        assert len(detector.windows) == 0
    
    @patch('win_manager.core.window_detector.psutil.Process')
    @patch('win_manager.core.window_detector.win32process.GetWindowThreadProcessId')
    @patch('win_manager.core.window_detector.win32gui.GetWindowRect')
    @patch('win_manager.core.window_detector.win32gui.GetWindowText')
    @patch('win_manager.core.window_detector.win32gui.IsWindowVisible')
    def test_enum_windows_callback_process_error(self, mock_is_visible, mock_get_text, 
                                                mock_get_rect, mock_get_thread_pid, mock_process):
        """Test callback when process access fails."""
        detector = WindowDetector()
        
        mock_is_visible.return_value = True
        mock_get_text.return_value = "Test Window"
        mock_get_rect.return_value = (0, 0, 100, 100)
        mock_get_thread_pid.return_value = (1111, 2222)
        
        # Mock process to raise psutil.AccessDenied (which is caught)
        import psutil
        mock_process.side_effect = psutil.AccessDenied("Access denied")
        
        with patch.object(detector, '_is_window_resizable', return_value=True):
            result = detector._enum_windows_callback(12345, None)
        
        # Should continue enumeration despite error
        assert result == True
        assert len(detector.windows) == 0
    
    @patch('win_manager.core.window_detector.win32gui.GetWindowLong')
    @patch('win_manager.core.window_detector.win32con.GWL_STYLE', 123)
    @patch('win_manager.core.window_detector.win32con.WS_THICKFRAME', 0x40000)
    def test_is_window_resizable_true(self, mock_get_long):
        """Test checking if window is resizable (true case)."""
        detector = WindowDetector()
        
        # Mock window with thick frame style
        mock_get_long.return_value = 0x40000  # WS_THICKFRAME
        
        result = detector._is_window_resizable(12345)
        
        assert result == True
        mock_get_long.assert_called_once_with(12345, 123)
    
    @patch('win_manager.core.window_detector.win32gui.GetWindowLong')
    @patch('win_manager.core.window_detector.win32con.GWL_STYLE', 123)
    @patch('win_manager.core.window_detector.win32con.WS_THICKFRAME', 0x40000)
    def test_is_window_resizable_false(self, mock_get_long):
        """Test checking if window is resizable (false case)."""
        detector = WindowDetector()
        
        # Mock window without thick frame style
        mock_get_long.return_value = 0x00000  # No WS_THICKFRAME
        
        result = detector._is_window_resizable(12345)
        
        assert result == False
        mock_get_long.assert_called_once_with(12345, 123)
    
    @patch('win_manager.core.window_detector.win32gui.GetWindowLong')
    def test_is_window_resizable_exception(self, mock_get_long):
        """Test checking if window is resizable with exception."""
        detector = WindowDetector()
        
        # Mock exception
        mock_get_long.side_effect = Exception("Access denied")
        
        result = detector._is_window_resizable(12345)
        
        assert result == False
    
    def test_get_window_by_title_found(self):
        """Test finding window by title."""
        detector = WindowDetector()
        
        # Add test windows
        detector.windows = [
            WindowInfo(1, "Notepad", "notepad.exe", 100, (0, 0, 100, 100), True, True),
            WindowInfo(2, "Calculator", "calc.exe", 200, (0, 0, 200, 200), True, True),
            WindowInfo(3, "Command Prompt", "cmd.exe", 300, (0, 0, 300, 300), True, True)
        ]
        
        # Test exact match
        result = detector.get_window_by_title("Calculator")
        assert result is not None
        assert result.hwnd == 2
        assert result.process_name == "calc.exe"
        
        # Test partial match
        result = detector.get_window_by_title("command")
        assert result is not None
        assert result.hwnd == 3
        assert result.process_name == "cmd.exe"
    
    def test_get_window_by_title_not_found(self):
        """Test finding window by title when not found."""
        detector = WindowDetector()
        
        # Add test windows
        detector.windows = [
            WindowInfo(1, "Notepad", "notepad.exe", 100, (0, 0, 100, 100), True, True)
        ]
        
        result = detector.get_window_by_title("NonExistentWindow")
        assert result is None
    
    def test_get_resizable_windows(self):
        """Test getting only resizable windows."""
        detector = WindowDetector()
        
        # Add mixed windows
        detector.windows = [
            WindowInfo(1, "Resizable Window", "app1.exe", 100, (0, 0, 100, 100), True, True),
            WindowInfo(2, "Fixed Window", "app2.exe", 200, (0, 0, 200, 200), True, False),
            WindowInfo(3, "Another Resizable", "app3.exe", 300, (0, 0, 300, 300), True, True)
        ]
        
        resizable = detector.get_resizable_windows()
        
        assert len(resizable) == 2
        assert resizable[0].hwnd == 1
        assert resizable[1].hwnd == 3
        assert all(w.is_resizable for w in resizable)
    
    def test_get_resizable_windows_empty(self):
        """Test getting resizable windows when none exist."""
        detector = WindowDetector()
        
        # Add only fixed windows
        detector.windows = [
            WindowInfo(1, "Fixed Window 1", "app1.exe", 100, (0, 0, 100, 100), True, False),
            WindowInfo(2, "Fixed Window 2", "app2.exe", 200, (0, 0, 200, 200), True, False)
        ]
        
        resizable = detector.get_resizable_windows()
        
        assert len(resizable) == 0
        assert resizable == []


if __name__ == '__main__':
    pytest.main([__file__])