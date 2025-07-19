"""
Unit tests for WindowManager.
"""

import pytest
import os
import sys
from unittest.mock import patch, MagicMock, Mock
import logging

# Add src to path for testing
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from win_manager.core.window_manager import WindowManager
from win_manager.core.window_detector import WindowInfo


class TestWindowManager:
    """Test suite for WindowManager class."""
    
    def test_init(self):
        """Test WindowManager initialization."""
        with patch('win_manager.core.window_manager.WindowDetector') as mock_detector, \
             patch('win_manager.core.window_manager.WindowController') as mock_controller, \
             patch('win_manager.core.window_manager.LayoutEngine') as mock_layout_engine, \
             patch('win_manager.core.window_manager.ConfigManager') as mock_config:
            
            # Mock config manager
            mock_config_instance = Mock()
            mock_config_instance.get.return_value = "INFO"
            mock_config.return_value = mock_config_instance
            
            manager = WindowManager()
            
            # Verify all components are initialized
            mock_detector.assert_called_once()
            mock_controller.assert_called_once()
            mock_layout_engine.assert_called_once()
            mock_config.assert_called_once()
            
            assert manager.detector == mock_detector.return_value
            assert manager.controller == mock_controller.return_value
            assert manager.layout_engine == mock_layout_engine.return_value
            assert manager.config == mock_config_instance
    
    def test_get_manageable_windows_with_filters(self):
        """Test getting manageable windows with various filters."""
        with patch('win_manager.core.window_manager.WindowDetector') as mock_detector, \
             patch('win_manager.core.window_manager.WindowController') as mock_controller, \
             patch('win_manager.core.window_manager.LayoutEngine') as mock_layout_engine, \
             patch('win_manager.core.window_manager.ConfigManager') as mock_config:
            
            # Mock config manager
            mock_config_instance = Mock()
            mock_config_instance.get.side_effect = lambda key, default=None: {
                "advanced.log_level": "INFO",
                "filters.ignore_fixed_size": True,
                "filters.ignore_minimized": True
            }.get(key, default)
            mock_config_instance.get_excluded_processes.return_value = ["explorer.exe", "notepad.exe"]
            mock_config.return_value = mock_config_instance
            
            # Mock detector
            mock_detector_instance = Mock()
            mock_detector_instance.enumerate_windows.return_value = [
                WindowInfo(1, "Test Window 1", "test1.exe", 100, (0, 0, 200, 200), True, True),
                WindowInfo(2, "Test Window 2", "explorer.exe", 200, (0, 0, 300, 300), True, True),  # Excluded
                WindowInfo(3, "Test Window 3", "test3.exe", 300, (0, 0, 50, 50), True, True),  # Too small
                WindowInfo(4, "Test Window 4", "test4.exe", 400, (0, 0, 400, 400), True, False),  # Fixed size
                WindowInfo(5, "Test Window 5", "test5.exe", 500, (0, 0, 500, 500), True, True)  # Valid
            ]
            mock_detector.return_value = mock_detector_instance
            
            # Mock controller
            mock_controller_instance = Mock()
            mock_controller_instance.is_window_minimized.return_value = False
            mock_controller.return_value = mock_controller_instance
            
            manager = WindowManager()
            manageable_windows = manager.get_manageable_windows()
            
            # Should only return windows 1 and 5 (excluded: 2=explorer, 3=too small, 4=fixed size)
            assert len(manageable_windows) == 2
            assert manageable_windows[0].hwnd == 1
            assert manageable_windows[1].hwnd == 5
    
    def test_get_manageable_windows_with_minimized_filter(self):
        """Test filtering out minimized windows."""
        with patch('win_manager.core.window_manager.WindowDetector') as mock_detector, \
             patch('win_manager.core.window_manager.WindowController') as mock_controller, \
             patch('win_manager.core.window_manager.LayoutEngine') as mock_layout_engine, \
             patch('win_manager.core.window_manager.ConfigManager') as mock_config:
            
            # Mock config manager
            mock_config_instance = Mock()
            mock_config_instance.get.side_effect = lambda key, default=None: {
                "advanced.log_level": "INFO",
                "filters.ignore_fixed_size": True,
                "filters.ignore_minimized": True
            }.get(key, default)
            mock_config_instance.get_excluded_processes.return_value = []
            mock_config.return_value = mock_config_instance
            
            # Mock detector
            mock_detector_instance = Mock()
            mock_detector_instance.enumerate_windows.return_value = [
                WindowInfo(1, "Normal Window", "test1.exe", 100, (0, 0, 200, 200), True, True),
                WindowInfo(2, "Minimized Window", "test2.exe", 200, (0, 0, 300, 300), True, True)
            ]
            mock_detector.return_value = mock_detector_instance
            
            # Mock controller - window 2 is minimized
            mock_controller_instance = Mock()
            mock_controller_instance.is_window_minimized.side_effect = lambda hwnd: hwnd == 2
            mock_controller.return_value = mock_controller_instance
            
            manager = WindowManager()
            manageable_windows = manager.get_manageable_windows()
            
            # Should only return window 1 (window 2 is minimized)
            assert len(manageable_windows) == 1
            assert manageable_windows[0].hwnd == 1
    
    def test_organize_windows_success(self):
        """Test successful window organization."""
        with patch('win_manager.core.window_manager.WindowDetector') as mock_detector, \
             patch('win_manager.core.window_manager.WindowController') as mock_controller, \
             patch('win_manager.core.window_manager.LayoutEngine') as mock_layout_engine, \
             patch('win_manager.core.window_manager.ConfigManager') as mock_config:
            
            # Mock config manager
            mock_config_instance = Mock()
            mock_config_instance.get.side_effect = lambda key, default=None: {
                "advanced.log_level": "INFO",
                "window_management.default_layout": "cascade",
                "filters.ignore_fixed_size": True,
                "filters.ignore_minimized": True
            }.get(key, default)
            mock_config_instance.get_excluded_processes.return_value = []
            mock_config.return_value = mock_config_instance
            
            # Mock detector
            mock_detector_instance = Mock()
            mock_detector_instance.enumerate_windows.return_value = [
                WindowInfo(1, "Window 1", "test1.exe", 100, (0, 0, 200, 200), True, True),
                WindowInfo(2, "Window 2", "test2.exe", 200, (0, 0, 300, 300), True, True)
            ]
            mock_detector.return_value = mock_detector_instance
            
            # Mock controller
            mock_controller_instance = Mock()
            mock_controller_instance.is_window_minimized.return_value = False
            mock_controller_instance.move_window.return_value = True
            mock_controller.return_value = mock_controller_instance
            
            # Mock layout engine
            mock_layout_engine_instance = Mock()
            mock_layout_engine_instance.apply_layout.return_value = {
                1: (100, 100, 300, 300),
                2: (150, 150, 300, 300)
            }
            mock_layout_engine.return_value = mock_layout_engine_instance
            
            manager = WindowManager()
            result = manager.organize_windows("cascade")
            
            assert result == True
            mock_layout_engine_instance.apply_layout.assert_called_once_with("cascade", [
                WindowInfo(1, "Window 1", "test1.exe", 100, (0, 0, 200, 200), True, True),
                WindowInfo(2, "Window 2", "test2.exe", 200, (0, 0, 300, 300), True, True)
            ])
            assert mock_controller_instance.move_window.call_count == 2
    
    def test_organize_windows_no_windows(self):
        """Test organizing when no manageable windows exist."""
        with patch('win_manager.core.window_manager.WindowDetector') as mock_detector, \
             patch('win_manager.core.window_manager.WindowController') as mock_controller, \
             patch('win_manager.core.window_manager.LayoutEngine') as mock_layout_engine, \
             patch('win_manager.core.window_manager.ConfigManager') as mock_config:
            
            # Mock config manager
            mock_config_instance = Mock()
            mock_config_instance.get.side_effect = lambda key, default=None: {
                "advanced.log_level": "INFO",
                "window_management.default_layout": "cascade",
                "filters.ignore_fixed_size": True,
                "filters.ignore_minimized": True
            }.get(key, default)
            mock_config_instance.get_excluded_processes.return_value = []
            mock_config.return_value = mock_config_instance
            
            # Mock detector - no windows
            mock_detector_instance = Mock()
            mock_detector_instance.enumerate_windows.return_value = []
            mock_detector.return_value = mock_detector_instance
            
            # Mock controller
            mock_controller_instance = Mock()
            mock_controller.return_value = mock_controller_instance
            
            manager = WindowManager()
            result = manager.organize_windows("cascade")
            
            assert result == False
    
    def test_organize_windows_with_failures(self):
        """Test organizing windows with some move failures."""
        with patch('win_manager.core.window_manager.WindowDetector') as mock_detector, \
             patch('win_manager.core.window_manager.WindowController') as mock_controller, \
             patch('win_manager.core.window_manager.LayoutEngine') as mock_layout_engine, \
             patch('win_manager.core.window_manager.ConfigManager') as mock_config:
            
            # Mock config manager
            mock_config_instance = Mock()
            mock_config_instance.get.side_effect = lambda key, default=None: {
                "advanced.log_level": "INFO",
                "window_management.default_layout": "cascade",
                "filters.ignore_fixed_size": True,
                "filters.ignore_minimized": True
            }.get(key, default)
            mock_config_instance.get_excluded_processes.return_value = []
            mock_config.return_value = mock_config_instance
            
            # Mock detector
            mock_detector_instance = Mock()
            mock_detector_instance.enumerate_windows.return_value = [
                WindowInfo(1, "Window 1", "test1.exe", 100, (0, 0, 200, 200), True, True),
                WindowInfo(2, "Window 2", "test2.exe", 200, (0, 0, 300, 300), True, True)
            ]
            mock_detector.return_value = mock_detector_instance
            
            # Mock controller - first window fails, second succeeds
            mock_controller_instance = Mock()
            mock_controller_instance.is_window_minimized.return_value = False
            mock_controller_instance.move_window.side_effect = [False, True]
            mock_controller.return_value = mock_controller_instance
            
            # Mock layout engine
            mock_layout_engine_instance = Mock()
            mock_layout_engine_instance.apply_layout.return_value = {
                1: (100, 100, 300, 300),
                2: (150, 150, 300, 300)
            }
            mock_layout_engine.return_value = mock_layout_engine_instance
            
            manager = WindowManager()
            result = manager.organize_windows("cascade")
            
            assert result == True  # Should still be True since at least one succeeded
            assert mock_controller_instance.move_window.call_count == 2
    
    def test_organize_windows_exception(self):
        """Test organizing windows with exception."""
        with patch('win_manager.core.window_manager.WindowDetector') as mock_detector, \
             patch('win_manager.core.window_manager.WindowController') as mock_controller, \
             patch('win_manager.core.window_manager.LayoutEngine') as mock_layout_engine, \
             patch('win_manager.core.window_manager.ConfigManager') as mock_config:
            
            # Mock config manager
            mock_config_instance = Mock()
            mock_config_instance.get.side_effect = lambda key, default=None: {
                "advanced.log_level": "INFO",
                "window_management.default_layout": "cascade"
            }.get(key, default)
            mock_config.return_value = mock_config_instance
            
            # Mock detector - raise exception
            mock_detector_instance = Mock()
            mock_detector_instance.enumerate_windows.side_effect = Exception("Test error")
            mock_detector.return_value = mock_detector_instance
            
            manager = WindowManager()
            result = manager.organize_windows("cascade")
            
            assert result == False
    
    def test_cascade_windows(self):
        """Test cascade windows shortcut method."""
        with patch('win_manager.core.window_manager.WindowDetector'), \
             patch('win_manager.core.window_manager.WindowController'), \
             patch('win_manager.core.window_manager.LayoutEngine'), \
             patch('win_manager.core.window_manager.ConfigManager') as mock_config:
            
            # Mock config manager
            mock_config_instance = Mock()
            mock_config_instance.get.return_value = "INFO"
            mock_config.return_value = mock_config_instance
            
            manager = WindowManager()
            
            with patch.object(manager, 'organize_windows') as mock_organize:
                mock_organize.return_value = True
                
                result = manager.cascade_windows()
                
                assert result == True
                mock_organize.assert_called_once_with("cascade")
    
    def test_grid_windows(self):
        """Test grid windows shortcut method."""
        with patch('win_manager.core.window_manager.WindowDetector'), \
             patch('win_manager.core.window_manager.WindowController'), \
             patch('win_manager.core.window_manager.LayoutEngine'), \
             patch('win_manager.core.window_manager.ConfigManager') as mock_config:
            
            # Mock config manager
            mock_config_instance = Mock()
            mock_config_instance.get.return_value = "INFO"
            mock_config.return_value = mock_config_instance
            
            manager = WindowManager()
            
            with patch.object(manager, 'organize_windows') as mock_organize:
                mock_organize.return_value = True
                
                result = manager.grid_windows()
                
                assert result == True
                mock_organize.assert_called_once_with("grid")
    
    def test_stack_windows(self):
        """Test stack windows shortcut method."""
        with patch('win_manager.core.window_manager.WindowDetector'), \
             patch('win_manager.core.window_manager.WindowController'), \
             patch('win_manager.core.window_manager.LayoutEngine'), \
             patch('win_manager.core.window_manager.ConfigManager') as mock_config:
            
            # Mock config manager
            mock_config_instance = Mock()
            mock_config_instance.get.return_value = "INFO"
            mock_config.return_value = mock_config_instance
            
            manager = WindowManager()
            
            with patch.object(manager, 'organize_windows') as mock_organize:
                mock_organize.return_value = True
                
                result = manager.stack_windows()
                
                assert result == True
                mock_organize.assert_called_once_with("stack")
    
    def test_undo_layout_success(self):
        """Test successful undo layout."""
        with patch('win_manager.core.window_manager.WindowDetector') as mock_detector, \
             patch('win_manager.core.window_manager.WindowController') as mock_controller, \
             patch('win_manager.core.window_manager.LayoutEngine') as mock_layout_engine, \
             patch('win_manager.core.window_manager.ConfigManager') as mock_config:
            
            # Mock config manager
            mock_config_instance = Mock()
            mock_config_instance.get.return_value = "INFO"
            mock_config.return_value = mock_config_instance
            
            # Mock detector
            mock_detector_instance = Mock()
            mock_detector_instance.enumerate_windows.return_value = [
                WindowInfo(1, "Window 1", "test1.exe", 100, (0, 0, 200, 200), True, True),
                WindowInfo(2, "Window 2", "test2.exe", 200, (0, 0, 300, 300), True, True)
            ]
            mock_detector.return_value = mock_detector_instance
            
            # Mock controller
            mock_controller_instance = Mock()
            mock_controller_instance.restore_window_state.return_value = True
            mock_controller.return_value = mock_controller_instance
            
            manager = WindowManager()
            result = manager.undo_layout()
            
            assert result == True
            assert mock_controller_instance.restore_window_state.call_count == 2
    
    def test_undo_layout_no_success(self):
        """Test undo layout when no windows can be restored."""
        with patch('win_manager.core.window_manager.WindowDetector') as mock_detector, \
             patch('win_manager.core.window_manager.WindowController') as mock_controller, \
             patch('win_manager.core.window_manager.LayoutEngine') as mock_layout_engine, \
             patch('win_manager.core.window_manager.ConfigManager') as mock_config:
            
            # Mock config manager
            mock_config_instance = Mock()
            mock_config_instance.get.return_value = "INFO"
            mock_config.return_value = mock_config_instance
            
            # Mock detector
            mock_detector_instance = Mock()
            mock_detector_instance.enumerate_windows.return_value = [
                WindowInfo(1, "Window 1", "test1.exe", 100, (0, 0, 200, 200), True, True)
            ]
            mock_detector.return_value = mock_detector_instance
            
            # Mock controller - restore fails
            mock_controller_instance = Mock()
            mock_controller_instance.restore_window_state.return_value = False
            mock_controller.return_value = mock_controller_instance
            
            manager = WindowManager()
            result = manager.undo_layout()
            
            assert result == False
    
    def test_undo_layout_exception(self):
        """Test undo layout with exception."""
        with patch('win_manager.core.window_manager.WindowDetector') as mock_detector, \
             patch('win_manager.core.window_manager.WindowController') as mock_controller, \
             patch('win_manager.core.window_manager.LayoutEngine') as mock_layout_engine, \
             patch('win_manager.core.window_manager.ConfigManager') as mock_config:
            
            # Mock config manager
            mock_config_instance = Mock()
            mock_config_instance.get.return_value = "INFO"
            mock_config.return_value = mock_config_instance
            
            # Mock detector - raise exception
            mock_detector_instance = Mock()
            mock_detector_instance.enumerate_windows.side_effect = Exception("Test error")
            mock_detector.return_value = mock_detector_instance
            
            manager = WindowManager()
            result = manager.undo_layout()
            
            assert result == False
    
    def test_get_window_list(self):
        """Test getting window list."""
        with patch('win_manager.core.window_manager.WindowDetector') as mock_detector, \
             patch('win_manager.core.window_manager.WindowController') as mock_controller, \
             patch('win_manager.core.window_manager.LayoutEngine') as mock_layout_engine, \
             patch('win_manager.core.window_manager.ConfigManager') as mock_config:
            
            # Mock config manager
            mock_config_instance = Mock()
            mock_config_instance.get.return_value = "INFO"
            mock_config.return_value = mock_config_instance
            
            # Mock detector
            mock_detector_instance = Mock()
            mock_detector_instance.enumerate_windows.return_value = [
                WindowInfo(1, "Window 1", "test1.exe", 100, (0, 0, 200, 200), True, True),
                WindowInfo(2, "Window 2", "test2.exe", 200, (0, 0, 300, 300), True, False)
            ]
            mock_detector.return_value = mock_detector_instance
            
            # Mock controller
            mock_controller_instance = Mock()
            mock_controller_instance.is_window_minimized.side_effect = [False, True]
            mock_controller_instance.is_window_maximized.side_effect = [True, False]
            mock_controller.return_value = mock_controller_instance
            
            manager = WindowManager()
            window_list = manager.get_window_list()
            
            assert len(window_list) == 2
            
            # Check first window
            assert window_list[0]['hwnd'] == 1
            assert window_list[0]['title'] == "Window 1"
            assert window_list[0]['process_name'] == "test1.exe"
            assert window_list[0]['is_minimized'] == False
            assert window_list[0]['is_maximized'] == True
            
            # Check second window
            assert window_list[1]['hwnd'] == 2
            assert window_list[1]['title'] == "Window 2"
            assert window_list[1]['process_name'] == "test2.exe"
            assert window_list[1]['is_minimized'] == True
            assert window_list[1]['is_maximized'] == False
    
    def test_window_control_methods(self):
        """Test window control delegation methods."""
        with patch('win_manager.core.window_manager.WindowDetector'), \
             patch('win_manager.core.window_manager.WindowController') as mock_controller, \
             patch('win_manager.core.window_manager.LayoutEngine'), \
             patch('win_manager.core.window_manager.ConfigManager') as mock_config:
            
            # Mock config manager
            mock_config_instance = Mock()
            mock_config_instance.get.return_value = "INFO"
            mock_config.return_value = mock_config_instance
            
            # Mock controller
            mock_controller_instance = Mock()
            mock_controller_instance.bring_to_front.return_value = True
            mock_controller_instance.minimize_window.return_value = True
            mock_controller_instance.maximize_window.return_value = True
            mock_controller_instance.restore_window.return_value = True
            mock_controller.return_value = mock_controller_instance
            
            manager = WindowManager()
            
            # Test focus window
            assert manager.focus_window(12345) == True
            mock_controller_instance.bring_to_front.assert_called_once_with(12345)
            
            # Test minimize window
            assert manager.minimize_window(12345) == True
            mock_controller_instance.minimize_window.assert_called_once_with(12345)
            
            # Test maximize window
            assert manager.maximize_window(12345) == True
            mock_controller_instance.maximize_window.assert_called_once_with(12345)
            
            # Test restore window
            assert manager.restore_window(12345) == True
            mock_controller_instance.restore_window.assert_called_once_with(12345)
    
    def test_get_available_layouts(self):
        """Test getting available layouts."""
        with patch('win_manager.core.window_manager.WindowDetector'), \
             patch('win_manager.core.window_manager.WindowController'), \
             patch('win_manager.core.window_manager.LayoutEngine') as mock_layout_engine, \
             patch('win_manager.core.window_manager.ConfigManager') as mock_config:
            
            # Mock config manager
            mock_config_instance = Mock()
            mock_config_instance.get.return_value = "INFO"
            mock_config.return_value = mock_config_instance
            
            # Mock layout engine
            mock_layout_engine_instance = Mock()
            mock_layout_engine_instance.get_available_layouts.return_value = ["cascade", "grid", "stack"]
            mock_layout_engine.return_value = mock_layout_engine_instance
            
            manager = WindowManager()
            layouts = manager.get_available_layouts()
            
            assert layouts == ["cascade", "grid", "stack"]
            mock_layout_engine_instance.get_available_layouts.assert_called_once()
    
    def test_save_config(self):
        """Test saving configuration."""
        with patch('win_manager.core.window_manager.WindowDetector'), \
             patch('win_manager.core.window_manager.WindowController'), \
             patch('win_manager.core.window_manager.LayoutEngine'), \
             patch('win_manager.core.window_manager.ConfigManager') as mock_config:
            
            # Mock config manager
            mock_config_instance = Mock()
            mock_config_instance.get.return_value = "INFO"
            mock_config_instance.save_config.return_value = True
            mock_config.return_value = mock_config_instance
            
            manager = WindowManager()
            result = manager.save_config()
            
            assert result == True
            mock_config_instance.save_config.assert_called_once()
    
    def test_get_config(self):
        """Test getting configuration manager."""
        with patch('win_manager.core.window_manager.WindowDetector'), \
             patch('win_manager.core.window_manager.WindowController'), \
             patch('win_manager.core.window_manager.LayoutEngine'), \
             patch('win_manager.core.window_manager.ConfigManager') as mock_config:
            
            # Mock config manager
            mock_config_instance = Mock()
            mock_config_instance.get.return_value = "INFO"
            mock_config.return_value = mock_config_instance
            
            manager = WindowManager()
            config = manager.get_config()
            
            assert config == mock_config_instance
    
    def test_organize_windows_uses_default_layout(self):
        """Test that organize_windows uses default layout when none specified."""
        with patch('win_manager.core.window_manager.WindowDetector') as mock_detector, \
             patch('win_manager.core.window_manager.WindowController') as mock_controller, \
             patch('win_manager.core.window_manager.LayoutEngine') as mock_layout_engine, \
             patch('win_manager.core.window_manager.ConfigManager') as mock_config:
            
            # Mock config manager
            mock_config_instance = Mock()
            mock_config_instance.get.side_effect = lambda key, default=None: {
                "advanced.log_level": "INFO",
                "window_management.default_layout": "grid",
                "filters.ignore_fixed_size": True,
                "filters.ignore_minimized": True
            }.get(key, default)
            mock_config_instance.get_excluded_processes.return_value = []
            mock_config.return_value = mock_config_instance
            
            # Mock detector
            mock_detector_instance = Mock()
            mock_detector_instance.enumerate_windows.return_value = [
                WindowInfo(1, "Window 1", "test1.exe", 100, (0, 0, 200, 200), True, True)
            ]
            mock_detector.return_value = mock_detector_instance
            
            # Mock controller
            mock_controller_instance = Mock()
            mock_controller_instance.is_window_minimized.return_value = False
            mock_controller_instance.move_window.return_value = True
            mock_controller.return_value = mock_controller_instance
            
            # Mock layout engine
            mock_layout_engine_instance = Mock()
            mock_layout_engine_instance.apply_layout.return_value = {1: (100, 100, 300, 300)}
            mock_layout_engine.return_value = mock_layout_engine_instance
            
            manager = WindowManager()
            result = manager.organize_windows()  # No layout specified
            
            assert result == True
            mock_layout_engine_instance.apply_layout.assert_called_once_with("grid", [
                WindowInfo(1, "Window 1", "test1.exe", 100, (0, 0, 200, 200), True, True)
            ])


if __name__ == '__main__':
    pytest.main([__file__])