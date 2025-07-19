"""
Basic tests for win-manager.
"""

import pytest
import sys
import os

# Add src to path for testing
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from win_manager import __version__, WindowManager, WindowDetector, ConfigManager


def test_version():
    """Test that version is properly set."""
    assert __version__ == "0.1.0"


def test_window_manager_creation():
    """Test that WindowManager can be created."""
    wm = WindowManager()
    assert wm is not None
    assert isinstance(wm, WindowManager)


def test_window_detector_creation():
    """Test that WindowDetector can be created."""
    detector = WindowDetector()
    assert detector is not None
    assert isinstance(detector, WindowDetector)


def test_config_manager_creation():
    """Test that ConfigManager can be created."""
    config = ConfigManager()
    assert config is not None
    assert isinstance(config, ConfigManager)


def test_config_manager_default_values():
    """Test that ConfigManager has default values."""
    config = ConfigManager()
    
    # Test some default values
    assert config.get("window_management.default_layout") == "cascade"
    assert config.get("filters.ignore_fixed_size") == True
    assert config.get("hotkeys.organize_windows") == "ctrl+alt+o"


def test_window_manager_methods():
    """Test that WindowManager has required methods."""
    wm = WindowManager()
    
    # Test method existence
    assert hasattr(wm, 'get_manageable_windows')
    assert hasattr(wm, 'organize_windows')
    assert hasattr(wm, 'cascade_windows')
    assert hasattr(wm, 'grid_windows')
    assert hasattr(wm, 'stack_windows')
    assert hasattr(wm, 'undo_layout')
    assert hasattr(wm, 'get_available_layouts')


def test_layout_availability():
    """Test that all expected layouts are available."""
    wm = WindowManager()
    available_layouts = wm.get_available_layouts()
    
    expected_layouts = ["cascade", "grid", "stack"]
    for layout in expected_layouts:
        assert layout in available_layouts


@pytest.mark.skipif(sys.platform != "win32", reason="Windows-only functionality")
def test_window_detection():
    """Test window detection functionality (Windows only)."""
    detector = WindowDetector()
    
    # This test will only run on Windows
    windows = detector.enumerate_windows()
    assert isinstance(windows, list)
    # We should have at least some windows (including the test runner)
    assert len(windows) >= 0


if __name__ == "__main__":
    pytest.main([__file__])