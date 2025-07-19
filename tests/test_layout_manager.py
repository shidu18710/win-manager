"""
Unit tests for LayoutManager and related classes.
"""

import pytest
import os
import sys
from unittest.mock import patch, MagicMock
from collections import namedtuple

# Add src to path for testing
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from win_manager.core.layout_manager import (
    LayoutManager, CascadeLayout, GridLayout, StackLayout, LayoutEngine
)
from win_manager.core.window_detector import WindowInfo


class TestLayoutManager:
    """Test suite for LayoutManager abstract base class."""
    
    def test_abstract_class_cannot_be_instantiated(self):
        """Test that LayoutManager cannot be instantiated directly."""
        with pytest.raises(TypeError):
            LayoutManager()


class TestCascadeLayout:
    """Test suite for CascadeLayout class."""
    
    def test_init_default_values(self):
        """Test CascadeLayout initialization with default values."""
        layout = CascadeLayout()
        assert layout.offset_x == 30
        assert layout.offset_y == 30
    
    def test_init_custom_values(self):
        """Test CascadeLayout initialization with custom values."""
        layout = CascadeLayout(offset_x=50, offset_y=40)
        assert layout.offset_x == 50
        assert layout.offset_y == 40
    
    def test_calculate_positions_empty_windows(self):
        """Test calculating positions with empty window list."""
        layout = CascadeLayout()
        windows = []
        screen_rect = (0, 0, 1920, 1080)
        
        positions = layout.calculate_positions(windows, screen_rect)
        
        assert positions == {}
    
    def test_calculate_positions_single_window(self):
        """Test calculating positions with single window."""
        layout = CascadeLayout()
        windows = [
            WindowInfo(12345, "Test Window", "test.exe", 100, (0, 0, 100, 100), True, True)
        ]
        screen_rect = (0, 0, 1920, 1080)
        
        positions = layout.calculate_positions(windows, screen_rect)
        
        assert len(positions) == 1
        assert 12345 in positions
        
        x, y, width, height = positions[12345]
        assert x == 0  # screen_left + (0 * offset_x)
        assert y == 0  # screen_top + (0 * offset_y)
        assert width == int(1920 * 0.7)  # 70% of screen width
        assert height == int(1080 * 0.7)  # 70% of screen height
    
    def test_calculate_positions_multiple_windows(self):
        """Test calculating positions with multiple windows."""
        layout = CascadeLayout(offset_x=50, offset_y=40)
        windows = [
            WindowInfo(12345, "Window 1", "test1.exe", 100, (0, 0, 100, 100), True, True),
            WindowInfo(67890, "Window 2", "test2.exe", 200, (0, 0, 200, 200), True, True),
            WindowInfo(11111, "Window 3", "test3.exe", 300, (0, 0, 300, 300), True, True)
        ]
        screen_rect = (0, 0, 1920, 1080)
        
        positions = layout.calculate_positions(windows, screen_rect)
        
        assert len(positions) == 3
        
        # Check first window
        x, y, width, height = positions[12345]
        assert x == 0
        assert y == 0
        
        # Check second window
        x, y, width, height = positions[67890]
        assert x == 50  # offset_x
        assert y == 40  # offset_y
        
        # Check third window
        x, y, width, height = positions[11111]
        assert x == 100  # 2 * offset_x
        assert y == 80   # 2 * offset_y
    
    def test_calculate_positions_screen_overflow(self):
        """Test calculating positions when windows would overflow screen."""
        layout = CascadeLayout(offset_x=100, offset_y=100)
        windows = [
            WindowInfo(i, f"Window {i}", f"test{i}.exe", i, (0, 0, 100, 100), True, True)
            for i in range(50)  # Many windows to cause overflow
        ]
        screen_rect = (0, 0, 800, 600)
        
        positions = layout.calculate_positions(windows, screen_rect)
        
        assert len(positions) == 50
        
        # Check that some windows were reset to screen_left/screen_top
        window_width = int(800 * 0.7)
        window_height = int(600 * 0.7)
        
        for hwnd, (x, y, width, height) in positions.items():
            assert x >= 0  # Should not go negative
            assert y >= 0  # Should not go negative
            assert width == window_width
            assert height == window_height


class TestGridLayout:
    """Test suite for GridLayout class."""
    
    def test_init_default_values(self):
        """Test GridLayout initialization with default values."""
        layout = GridLayout()
        assert layout.columns is None
        assert layout.padding == 10
    
    def test_init_custom_values(self):
        """Test GridLayout initialization with custom values."""
        layout = GridLayout(columns=3, padding=20)
        assert layout.columns == 3
        assert layout.padding == 20
    
    def test_calculate_positions_empty_windows(self):
        """Test calculating positions with empty window list."""
        layout = GridLayout()
        windows = []
        screen_rect = (0, 0, 1920, 1080)
        
        positions = layout.calculate_positions(windows, screen_rect)
        
        assert positions == {}
    
    def test_calculate_positions_single_window(self):
        """Test calculating positions with single window."""
        layout = GridLayout()
        windows = [
            WindowInfo(12345, "Test Window", "test.exe", 100, (0, 0, 100, 100), True, True)
        ]
        screen_rect = (0, 0, 1920, 1080)
        
        positions = layout.calculate_positions(windows, screen_rect)
        
        assert len(positions) == 1
        assert 12345 in positions
        
        x, y, width, height = positions[12345]
        assert x == 10  # padding
        assert y == 10  # padding
        # Width and height should be calculated based on grid
        assert width > 0
        assert height > 0
    
    def test_calculate_positions_auto_columns(self):
        """Test calculating positions with automatic column calculation."""
        layout = GridLayout(padding=0)  # No padding for easier calculation
        windows = [
            WindowInfo(i, f"Window {i}", f"test{i}.exe", i, (0, 0, 100, 100), True, True)
            for i in range(4)  # 4 windows should create 2x2 grid
        ]
        screen_rect = (0, 0, 1000, 1000)
        
        positions = layout.calculate_positions(windows, screen_rect)
        
        assert len(positions) == 4
        
        # With 4 windows, should create 3 columns (int(4**0.5) + 1 = 3)
        # and 2 rows (4 + 3 - 1) // 3 = 2
        expected_window_width = 1000 // 3
        expected_window_height = 1000 // 2
        
        for hwnd, (x, y, width, height) in positions.items():
            assert width == expected_window_width
            assert height == expected_window_height
    
    def test_calculate_positions_fixed_columns(self):
        """Test calculating positions with fixed column count."""
        layout = GridLayout(columns=2, padding=0)
        windows = [
            WindowInfo(i, f"Window {i}", f"test{i}.exe", i, (0, 0, 100, 100), True, True)
            for i in range(4)
        ]
        screen_rect = (0, 0, 1000, 1000)
        
        positions = layout.calculate_positions(windows, screen_rect)
        
        assert len(positions) == 4
        
        # With 2 columns and 4 windows, should create 2x2 grid
        expected_window_width = 1000 // 2
        expected_window_height = 1000 // 2
        
        for hwnd, (x, y, width, height) in positions.items():
            assert width == expected_window_width
            assert height == expected_window_height
    
    def test_calculate_positions_with_padding(self):
        """Test calculating positions with padding."""
        layout = GridLayout(columns=2, padding=10)
        windows = [
            WindowInfo(12345, "Window 1", "test1.exe", 100, (0, 0, 100, 100), True, True),
            WindowInfo(67890, "Window 2", "test2.exe", 200, (0, 0, 200, 200), True, True)
        ]
        screen_rect = (0, 0, 1000, 1000)
        
        positions = layout.calculate_positions(windows, screen_rect)
        
        assert len(positions) == 2
        
        # Check that first window starts at padding
        x, y, width, height = positions[12345]
        assert x == 10  # padding
        assert y == 10  # padding
        
        # Check that second window is offset by width + padding
        x2, y2, width2, height2 = positions[67890]
        assert x2 == 10 + width + 10  # padding + width + padding
        assert y2 == 10  # Same row, so same y


class TestStackLayout:
    """Test suite for StackLayout class."""
    
    def test_init_default_values(self):
        """Test StackLayout initialization with default values."""
        layout = StackLayout()
        assert layout.stack_position == "center"
    
    def test_init_custom_values(self):
        """Test StackLayout initialization with custom values."""
        layout = StackLayout(stack_position="left")
        assert layout.stack_position == "left"
    
    def test_calculate_positions_center(self):
        """Test calculating positions with center stack position."""
        layout = StackLayout(stack_position="center")
        windows = [
            WindowInfo(12345, "Window 1", "test1.exe", 100, (0, 0, 100, 100), True, True),
            WindowInfo(67890, "Window 2", "test2.exe", 200, (0, 0, 200, 200), True, True)
        ]
        screen_rect = (0, 0, 1000, 1000)
        
        positions = layout.calculate_positions(windows, screen_rect)
        
        assert len(positions) == 2
        
        expected_width = int(1000 * 0.8)
        expected_height = int(1000 * 0.8)
        expected_x = (1000 - expected_width) // 2
        expected_y = (1000 - expected_height) // 2
        
        # Both windows should have same position (stacked)
        for hwnd, (x, y, width, height) in positions.items():
            assert x == expected_x
            assert y == expected_y
            assert width == expected_width
            assert height == expected_height
    
    def test_calculate_positions_left(self):
        """Test calculating positions with left stack position."""
        layout = StackLayout(stack_position="left")
        windows = [
            WindowInfo(12345, "Window 1", "test1.exe", 100, (0, 0, 100, 100), True, True)
        ]
        screen_rect = (0, 0, 1000, 1000)
        
        positions = layout.calculate_positions(windows, screen_rect)
        
        x, y, width, height = positions[12345]
        assert x == 50  # screen_left + 50
        assert y == 50  # screen_top + 50
        assert width == int(1000 * 0.8)
        assert height == int(1000 * 0.8)
    
    def test_calculate_positions_right(self):
        """Test calculating positions with right stack position."""
        layout = StackLayout(stack_position="right")
        windows = [
            WindowInfo(12345, "Window 1", "test1.exe", 100, (0, 0, 100, 100), True, True)
        ]
        screen_rect = (0, 0, 1000, 1000)
        
        positions = layout.calculate_positions(windows, screen_rect)
        
        expected_width = int(1000 * 0.8)
        expected_x = 1000 - expected_width - 50
        
        x, y, width, height = positions[12345]
        assert x == expected_x
        assert y == 50  # screen_top + 50
        assert width == expected_width
        assert height == int(1000 * 0.8)
    
    def test_calculate_positions_invalid_position(self):
        """Test calculating positions with invalid stack position."""
        layout = StackLayout(stack_position="invalid")
        windows = [
            WindowInfo(12345, "Window 1", "test1.exe", 100, (0, 0, 100, 100), True, True)
        ]
        screen_rect = (0, 0, 1000, 1000)
        
        positions = layout.calculate_positions(windows, screen_rect)
        
        # Should fallback to default position (top-left with offset)
        x, y, width, height = positions[12345]
        assert x == 50  # screen_left + 50
        assert y == 50  # screen_top + 50


class TestLayoutEngine:
    """Test suite for LayoutEngine class."""
    
    def test_init(self):
        """Test LayoutEngine initialization."""
        engine = LayoutEngine()
        assert "cascade" in engine.layouts
        assert "grid" in engine.layouts
        assert "stack" in engine.layouts
        assert len(engine.layouts) == 3
    
    @patch('win_manager.core.layout_manager.win32api.GetSystemMetrics')
    def test_get_screen_rect(self, mock_get_metrics):
        """Test getting screen rectangle."""
        engine = LayoutEngine()
        
        # Mock screen metrics
        mock_get_metrics.side_effect = [1920, 1080]  # width, height
        
        screen_rect = engine.get_screen_rect()
        
        assert screen_rect == (0, 0, 1920, 1080)
        assert mock_get_metrics.call_count == 2
        mock_get_metrics.assert_any_call(0)  # SM_CXSCREEN
        mock_get_metrics.assert_any_call(1)  # SM_CYSCREEN
    
    @patch('win_manager.core.layout_manager.win32api.GetSystemMetrics')
    def test_apply_layout_cascade(self, mock_get_metrics):
        """Test applying cascade layout."""
        engine = LayoutEngine()
        
        # Mock screen metrics
        mock_get_metrics.side_effect = [1920, 1080]
        
        windows = [
            WindowInfo(12345, "Window 1", "test1.exe", 100, (0, 0, 100, 100), True, True)
        ]
        
        positions = engine.apply_layout("cascade", windows)
        
        assert len(positions) == 1
        assert 12345 in positions
    
    @patch('win_manager.core.layout_manager.win32api.GetSystemMetrics')
    def test_apply_layout_grid(self, mock_get_metrics):
        """Test applying grid layout."""
        engine = LayoutEngine()
        
        # Mock screen metrics
        mock_get_metrics.side_effect = [1920, 1080]
        
        windows = [
            WindowInfo(12345, "Window 1", "test1.exe", 100, (0, 0, 100, 100), True, True)
        ]
        
        positions = engine.apply_layout("grid", windows)
        
        assert len(positions) == 1
        assert 12345 in positions
    
    @patch('win_manager.core.layout_manager.win32api.GetSystemMetrics')
    def test_apply_layout_stack(self, mock_get_metrics):
        """Test applying stack layout."""
        engine = LayoutEngine()
        
        # Mock screen metrics
        mock_get_metrics.side_effect = [1920, 1080]
        
        windows = [
            WindowInfo(12345, "Window 1", "test1.exe", 100, (0, 0, 100, 100), True, True)
        ]
        
        positions = engine.apply_layout("stack", windows)
        
        assert len(positions) == 1
        assert 12345 in positions
    
    def test_apply_layout_unknown(self):
        """Test applying unknown layout raises error."""
        engine = LayoutEngine()
        
        windows = [
            WindowInfo(12345, "Window 1", "test1.exe", 100, (0, 0, 100, 100), True, True)
        ]
        
        with pytest.raises(ValueError, match="Unknown layout: unknown"):
            engine.apply_layout("unknown", windows)
    
    def test_add_custom_layout(self):
        """Test adding custom layout."""
        engine = LayoutEngine()
        custom_layout = CascadeLayout(offset_x=100, offset_y=100)
        
        engine.add_custom_layout("custom", custom_layout)
        
        assert "custom" in engine.layouts
        assert engine.layouts["custom"] == custom_layout
    
    def test_get_available_layouts(self):
        """Test getting available layouts."""
        engine = LayoutEngine()
        
        layouts = engine.get_available_layouts()
        
        assert "cascade" in layouts
        assert "grid" in layouts
        assert "stack" in layouts
        assert len(layouts) == 3
    
    def test_get_available_layouts_with_custom(self):
        """Test getting available layouts including custom ones."""
        engine = LayoutEngine()
        custom_layout = CascadeLayout()
        engine.add_custom_layout("custom", custom_layout)
        
        layouts = engine.get_available_layouts()
        
        assert "cascade" in layouts
        assert "grid" in layouts
        assert "stack" in layouts
        assert "custom" in layouts
        assert len(layouts) == 4
    
    def test_layout_integration(self):
        """Test integration between different layout types."""
        engine = LayoutEngine()
        
        windows = [
            WindowInfo(i, f"Window {i}", f"test{i}.exe", i, (0, 0, 100, 100), True, True)
            for i in range(3)
        ]
        
        with patch('win_manager.core.layout_manager.win32api.GetSystemMetrics') as mock_metrics:
            # Return fixed values for screen metrics
            mock_metrics.return_value = 1920  # First call returns width
            mock_metrics.side_effect = [1920, 1080, 1920, 1080, 1920, 1080]  # 3 layouts x 2 calls each
            
            # Test each layout type
            for layout_name in ["cascade", "grid", "stack"]:
                positions = engine.apply_layout(layout_name, windows)
                assert len(positions) == 3
                
                # Verify all windows have positions
                for window in windows:
                    assert window.hwnd in positions
                    x, y, width, height = positions[window.hwnd]
                    assert isinstance(x, int)
                    assert isinstance(y, int)
                    assert isinstance(width, int)
                    assert isinstance(height, int)
                    assert width > 0
                    assert height > 0


if __name__ == '__main__':
    pytest.main([__file__])