"""
Integration tests for Win-Manager.
These tests verify that different modules work together correctly.
"""

import pytest
import os
import sys
import tempfile
import json
from unittest.mock import patch, MagicMock, Mock

# Add src to path for testing
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from win_manager.core.window_manager import WindowManager
from win_manager.core.window_detector import WindowInfo
from win_manager.core.config_manager import ConfigManager
from win_manager.utils.exception_handler import ExceptionHandler
from win_manager.utils.hotkey_manager import HotkeyManager


class TestWindowManagerIntegration:
    """Integration tests for WindowManager with all components."""
    
    @patch('win_manager.core.window_manager.WindowDetector')
    @patch('win_manager.core.window_manager.WindowController')
    @patch('win_manager.core.window_manager.LayoutEngine')
    @patch('win_manager.core.window_manager.ConfigManager')
    def test_end_to_end_window_organization(self, mock_config, mock_layout_engine, 
                                           mock_controller, mock_detector):
        """Test complete window organization workflow."""
        # Setup mock config
        mock_config_instance = Mock()
        mock_config_instance.get.side_effect = lambda key, default=None: {
            "advanced.log_level": "INFO",
            "filters.ignore_fixed_size": True,
            "filters.ignore_minimized": True,
            "window_management.default_layout": "cascade"
        }.get(key, default)
        mock_config_instance.get_excluded_processes.return_value = []
        mock_config.return_value = mock_config_instance
        
        # Setup mock detector
        mock_detector_instance = Mock()
        mock_detector_instance.enumerate_windows.return_value = [
            WindowInfo(1, "Notepad", "notepad.exe", 100, (0, 0, 800, 600), True, True),
            WindowInfo(2, "Calculator", "calc.exe", 200, (100, 100, 400, 300), True, True),
            WindowInfo(3, "Browser", "chrome.exe", 300, (200, 200, 1200, 800), True, True)
        ]
        mock_detector.return_value = mock_detector_instance
        
        # Setup mock controller
        mock_controller_instance = Mock()
        mock_controller_instance.is_window_minimized.return_value = False
        mock_controller_instance.move_window.return_value = True
        mock_controller.return_value = mock_controller_instance
        
        # Setup mock layout engine
        mock_layout_engine_instance = Mock()
        mock_layout_engine_instance.apply_layout.return_value = {
            1: (0, 0, 800, 600),
            2: (30, 30, 800, 600),
            3: (60, 60, 800, 600)
        }
        mock_layout_engine.return_value = mock_layout_engine_instance
        
        # Create window manager and test workflow
        manager = WindowManager()
        
        # Test getting manageable windows
        windows = manager.get_manageable_windows()
        assert len(windows) == 3
        
        # Test organizing windows
        result = manager.organize_windows("cascade")
        assert result == True
        
        # Verify layout engine was called
        mock_layout_engine_instance.apply_layout.assert_called_once()
        
        # Verify all windows were moved
        assert mock_controller_instance.move_window.call_count == 3
    
    @patch('win_manager.core.window_manager.WindowDetector')
    @patch('win_manager.core.window_manager.WindowController')
    @patch('win_manager.core.window_manager.LayoutEngine')
    @patch('win_manager.core.window_manager.ConfigManager')
    def test_filtering_integration(self, mock_config, mock_layout_engine, 
                                  mock_controller, mock_detector):
        """Test window filtering integration with configuration."""
        # Setup mock config with specific filters
        mock_config_instance = Mock()
        mock_config_instance.get.side_effect = lambda key, default=None: {
            "advanced.log_level": "INFO",
            "filters.ignore_fixed_size": True,
            "filters.ignore_minimized": True
        }.get(key, default)
        mock_config_instance.get_excluded_processes.return_value = ["explorer.exe", "dwm.exe"]
        mock_config.return_value = mock_config_instance
        
        # Setup mock detector with mixed windows
        mock_detector_instance = Mock()
        mock_detector_instance.enumerate_windows.return_value = [
            WindowInfo(1, "Notepad", "notepad.exe", 100, (0, 0, 800, 600), True, True),
            WindowInfo(2, "Explorer", "explorer.exe", 200, (100, 100, 400, 300), True, True),  # Excluded
            WindowInfo(3, "Fixed Window", "app.exe", 300, (200, 200, 50, 50), True, False),  # Fixed size
            WindowInfo(4, "Small Window", "tiny.exe", 400, (0, 0, 50, 50), True, True),  # Too small
            WindowInfo(5, "Valid Window", "valid.exe", 500, (0, 0, 800, 600), True, True)
        ]
        mock_detector.return_value = mock_detector_instance
        
        # Setup mock controller
        mock_controller_instance = Mock()
        mock_controller_instance.is_window_minimized.side_effect = lambda hwnd: hwnd == 3
        mock_controller.return_value = mock_controller_instance
        
        # Create window manager and test filtering
        manager = WindowManager()
        windows = manager.get_manageable_windows()
        
        # Should only have windows 1 and 5 (excluding: 2=explorer, 3=fixed, 4=too small)
        assert len(windows) == 2
        assert windows[0].hwnd == 1
        assert windows[1].hwnd == 5
    
    def test_config_manager_integration(self):
        """Test configuration management integration."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create config manager with temporary directory
            config_manager = ConfigManager(temp_dir)
            
            # Test setting and getting values
            config_manager.set("test.value", "hello")
            assert config_manager.get("test.value") == "hello"
            
            # Test saving and loading
            assert config_manager.save_config() == True
            
            # Create new config manager instance and verify persistence
            new_config = ConfigManager(temp_dir)
            assert new_config.get("test.value") == "hello"
            
            # Test hotkey management
            config_manager.set_hotkey("test_action", "ctrl+shift+t")
            assert config_manager.get_hotkey("test_action") == "ctrl+shift+t"
            
            # Test excluded processes
            config_manager.add_excluded_process("test.exe")
            assert "test.exe" in config_manager.get_excluded_processes()
    
    def test_exception_handler_integration(self):
        """Test exception handler integration."""
        handler = ExceptionHandler()
        callback_called = False
        
        def test_callback(exc):
            nonlocal callback_called
            callback_called = True
        
        handler.add_error_callback(test_callback)
        
        # Test safe execution
        def failing_function():
            raise ValueError("Test error")
        
        success, result = handler.safe_execute(failing_function)
        assert success == False
        assert result is None
        assert callback_called == True
        
        # Test decorator
        @handler.with_exception_handling("test_context")
        def decorated_function():
            raise RuntimeError("Decorator test")
        
        result = decorated_function()
        assert result is None
    
    def test_hotkey_manager_integration(self):
        """Test hotkey manager integration."""
        manager = HotkeyManager()
        
        # Test hotkey registration
        callback_called = False
        
        def test_callback():
            nonlocal callback_called
            callback_called = True
        
        # Register hotkey
        assert manager.register_hotkey("ctrl+alt+t", test_callback) == True
        
        # Verify registration
        hotkeys = manager.get_registered_hotkeys()
        assert "alt+ctrl+t" in hotkeys
        
        # Test unregistration
        assert manager.unregister_hotkey("ctrl+alt+t") == True
        
        # Verify unregistration
        hotkeys = manager.get_registered_hotkeys()
        assert "alt+ctrl+t" not in hotkeys


class TestErrorHandlingIntegration:
    """Integration tests for error handling across modules."""
    
    @patch('win_manager.core.window_manager.WindowDetector')
    @patch('win_manager.core.window_manager.WindowController')
    @patch('win_manager.core.window_manager.LayoutEngine')
    @patch('win_manager.core.window_manager.ConfigManager')
    def test_graceful_error_handling(self, mock_config, mock_layout_engine, 
                                    mock_controller, mock_detector):
        """Test that errors are handled gracefully across modules."""
        # Setup mock config
        mock_config_instance = Mock()
        mock_config_instance.get.side_effect = lambda key, default=None: {
            "advanced.log_level": "INFO"
        }.get(key, default)
        mock_config.return_value = mock_config_instance
        
        # Setup mock detector to raise exception
        mock_detector_instance = Mock()
        mock_detector_instance.enumerate_windows.side_effect = Exception("Windows API error")
        mock_detector.return_value = mock_detector_instance
        
        # Create window manager
        manager = WindowManager()
        
        # Test that organize_windows handles detector errors gracefully
        result = manager.organize_windows("cascade")
        assert result == False
        
        # Test that get_window_list handles detector errors gracefully
        # Note: get_window_list doesn't have exception handling, so it will raise
        # This is actually expected behavior - not all methods need to handle all exceptions
        try:
            window_list = manager.get_window_list()
            assert False, "Expected exception to be raised"
        except Exception as e:
            assert "Windows API error" in str(e)
    
    @patch('win_manager.core.window_manager.WindowDetector')
    @patch('win_manager.core.window_manager.WindowController')
    @patch('win_manager.core.window_manager.LayoutEngine')
    @patch('win_manager.core.window_manager.ConfigManager')
    def test_partial_failure_handling(self, mock_config, mock_layout_engine, 
                                     mock_controller, mock_detector):
        """Test handling of partial failures in window operations."""
        # Setup mock config
        mock_config_instance = Mock()
        mock_config_instance.get.side_effect = lambda key, default=None: {
            "advanced.log_level": "INFO",
            "filters.ignore_fixed_size": True,
            "filters.ignore_minimized": True
        }.get(key, default)
        mock_config_instance.get_excluded_processes.return_value = []
        mock_config.return_value = mock_config_instance
        
        # Setup mock detector
        mock_detector_instance = Mock()
        mock_detector_instance.enumerate_windows.return_value = [
            WindowInfo(1, "Window 1", "app1.exe", 100, (0, 0, 800, 600), True, True),
            WindowInfo(2, "Window 2", "app2.exe", 200, (100, 100, 800, 600), True, True),
            WindowInfo(3, "Window 3", "app3.exe", 300, (200, 200, 800, 600), True, True)
        ]
        mock_detector.return_value = mock_detector_instance
        
        # Setup mock controller with partial failures
        mock_controller_instance = Mock()
        mock_controller_instance.is_window_minimized.return_value = False
        mock_controller_instance.move_window.side_effect = [True, False, True]  # Middle one fails
        mock_controller.return_value = mock_controller_instance
        
        # Setup mock layout engine
        mock_layout_engine_instance = Mock()
        mock_layout_engine_instance.apply_layout.return_value = {
            1: (0, 0, 800, 600),
            2: (30, 30, 800, 600),
            3: (60, 60, 800, 600)
        }
        mock_layout_engine.return_value = mock_layout_engine_instance
        
        # Create window manager and test
        manager = WindowManager()
        result = manager.organize_windows("cascade")
        
        # Should still return True since some windows were moved successfully
        assert result == True
        
        # Verify all windows were attempted
        assert mock_controller_instance.move_window.call_count == 3


class TestConfigurationIntegration:
    """Integration tests for configuration across modules."""
    
    def test_config_persistence_integration(self):
        """Test configuration persistence across application restarts."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create initial config
            config1 = ConfigManager(temp_dir)
            config1.set("window_management.default_layout", "grid")
            config1.set("hotkeys.organize_windows", "ctrl+alt+w")
            config1.add_excluded_process("test.exe")
            assert config1.save_config() == True
            
            # Create new config instance (simulating app restart)
            config2 = ConfigManager(temp_dir)
            
            # Verify all settings persisted
            assert config2.get("window_management.default_layout") == "grid"
            assert config2.get("hotkeys.organize_windows") == "ctrl+alt+w"
            assert "test.exe" in config2.get_excluded_processes()
    
    def test_config_export_import_integration(self):
        """Test configuration export and import functionality."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create config with custom settings
            config1 = ConfigManager(temp_dir)
            config1.set("window_management.default_layout", "stack")
            config1.set("ui.show_notifications", False)
            config1.add_excluded_process("custom.exe")
            
            # Export config
            export_path = os.path.join(temp_dir, "exported_config.json")
            assert config1.export_config(export_path) == True
            
            # Create new config and import
            config2 = ConfigManager(temp_dir)
            config2.reset_to_default()  # Reset to ensure clean state
            
            assert config2.import_config(export_path) == True
            
            # Verify imported settings
            assert config2.get("window_management.default_layout") == "stack"
            assert config2.get("ui.show_notifications") == False
            assert "custom.exe" in config2.get_excluded_processes()


class TestPerformanceIntegration:
    """Integration tests for performance characteristics."""
    
    @patch('win_manager.core.window_manager.WindowDetector')
    @patch('win_manager.core.window_manager.WindowController')
    @patch('win_manager.core.window_manager.LayoutEngine')
    @patch('win_manager.core.window_manager.ConfigManager')
    def test_large_window_count_performance(self, mock_config, mock_layout_engine, 
                                           mock_controller, mock_detector):
        """Test performance with large number of windows."""
        # Setup mock config
        mock_config_instance = Mock()
        mock_config_instance.get.side_effect = lambda key, default=None: {
            "advanced.log_level": "INFO",
            "filters.ignore_fixed_size": True,
            "filters.ignore_minimized": True
        }.get(key, default)
        mock_config_instance.get_excluded_processes.return_value = []
        mock_config.return_value = mock_config_instance
        
        # Generate large number of windows with sufficient size
        windows = []
        positions = {}
        for i in range(100):
            # Make sure windows are large enough (>= 100px) to pass filtering
            window = WindowInfo(i, f"Window {i}", f"app{i}.exe", 100+i, 
                              (i*10, i*10, i*10+800, i*10+600), True, True)
            windows.append(window)
            positions[i] = (i*20, i*20, 800, 600)
        
        # Setup mock detector
        mock_detector_instance = Mock()
        mock_detector_instance.enumerate_windows.return_value = windows
        mock_detector.return_value = mock_detector_instance
        
        # Setup mock controller
        mock_controller_instance = Mock()
        mock_controller_instance.is_window_minimized.return_value = False
        mock_controller_instance.move_window.return_value = True
        mock_controller.return_value = mock_controller_instance
        
        # Setup mock layout engine
        mock_layout_engine_instance = Mock()
        mock_layout_engine_instance.apply_layout.return_value = positions
        mock_layout_engine.return_value = mock_layout_engine_instance
        
        # Create window manager and test
        manager = WindowManager()
        
        # Test that large window count is handled efficiently
        import time
        start_time = time.time()
        
        manageable_windows = manager.get_manageable_windows()
        assert len(manageable_windows) == 100
        
        result = manager.organize_windows("grid")
        assert result == True
        
        end_time = time.time()
        execution_time = end_time - start_time
        
        # Should complete in reasonable time (less than 1 second)
        assert execution_time < 1.0
        
        # Verify all windows were processed
        assert mock_controller_instance.move_window.call_count == 100


if __name__ == '__main__':
    pytest.main([__file__])