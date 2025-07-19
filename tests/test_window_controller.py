"""
Unit tests for WindowController.
"""

import pytest
import os
import sys
from unittest.mock import patch, MagicMock, Mock

# Add src to path for testing
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from win_manager.core.window_controller import WindowController


class TestWindowController:
    """Test suite for WindowController class."""
    
    def test_init(self):
        """Test WindowController initialization."""
        controller = WindowController()
        assert controller.window_states == {}
        assert isinstance(controller.window_states, dict)
    
    @patch('win_manager.core.window_controller.win32gui.GetWindowPlacement')
    @patch('win_manager.core.window_controller.win32gui.GetWindowRect')
    def test_save_window_state_success(self, mock_get_rect, mock_get_placement):
        """Test successful window state saving."""
        controller = WindowController()
        
        # Mock return values
        mock_get_rect.return_value = (100, 200, 300, 400)
        mock_get_placement.return_value = {'showCmd': 1, 'flags': 0, 'minPosition': (0, 0), 'maxPosition': (0, 0), 'normalPosition': (100, 200, 300, 400)}
        
        controller.save_window_state(12345)
        
        # Verify state was saved
        assert 12345 in controller.window_states
        assert controller.window_states[12345]['rect'] == (100, 200, 300, 400)
        assert 'placement' in controller.window_states[12345]
        
        # Verify API calls
        mock_get_rect.assert_called_once_with(12345)
        mock_get_placement.assert_called_once_with(12345)
    
    @patch('win_manager.core.window_controller.win32gui.GetWindowPlacement')
    @patch('win_manager.core.window_controller.win32gui.GetWindowRect')
    def test_save_window_state_exception(self, mock_get_rect, mock_get_placement):
        """Test window state saving with exception."""
        controller = WindowController()
        
        # Mock exception
        mock_get_rect.side_effect = Exception("API Error")
        
        # Should not raise exception
        controller.save_window_state(12345)
        
        # Verify state was not saved
        assert 12345 not in controller.window_states
    
    @patch('win_manager.core.window_controller.win32gui.SetWindowPlacement')
    def test_restore_window_state_success(self, mock_set_placement):
        """Test successful window state restoration."""
        controller = WindowController()
        
        # Pre-populate saved state
        test_state = {
            'rect': (100, 200, 300, 400),
            'placement': {'showCmd': 1, 'flags': 0, 'minPosition': (0, 0), 'maxPosition': (0, 0), 'normalPosition': (100, 200, 300, 400)}
        }
        controller.window_states[12345] = test_state
        
        result = controller.restore_window_state(12345)
        
        assert result == True
        mock_set_placement.assert_called_once_with(12345, test_state['placement'])
    
    def test_restore_window_state_not_saved(self):
        """Test restoring window state when not previously saved."""
        controller = WindowController()
        
        result = controller.restore_window_state(12345)
        
        assert result == False
    
    @patch('win_manager.core.window_controller.win32gui.SetWindowPlacement')
    def test_restore_window_state_exception(self, mock_set_placement):
        """Test window state restoration with exception."""
        controller = WindowController()
        
        # Pre-populate saved state
        test_state = {
            'rect': (100, 200, 300, 400),
            'placement': {'showCmd': 1}
        }
        controller.window_states[12345] = test_state
        
        # Mock exception
        mock_set_placement.side_effect = Exception("API Error")
        
        result = controller.restore_window_state(12345)
        
        assert result == False
    
    @patch('win_manager.core.window_controller.win32gui.SetWindowPos')
    @patch('win_manager.core.window_controller.win32gui.ShowWindow')
    @patch('win_manager.core.window_controller.win32gui.IsIconic')
    @patch('win_manager.core.window_controller.win32con.SW_RESTORE', 9)
    @patch('win_manager.core.window_controller.win32con.HWND_TOP', 0)
    @patch('win_manager.core.window_controller.win32con.SWP_SHOWWINDOW', 0x40)
    def test_move_window_success(self, mock_is_iconic, mock_show_window, mock_set_pos):
        """Test successful window move and resize."""
        controller = WindowController()
        
        # Mock window is not minimized
        mock_is_iconic.return_value = False
        
        # Mock save_window_state
        with patch.object(controller, 'save_window_state') as mock_save:
            result = controller.move_window(12345, 100, 200, 300, 400)
        
        assert result == True
        mock_save.assert_called_once_with(12345)
        mock_is_iconic.assert_called_once_with(12345)
        mock_show_window.assert_not_called()  # Should not be called if not minimized
        mock_set_pos.assert_called_once_with(12345, 0, 100, 200, 300, 400, 0x40)
    
    @patch('win_manager.core.window_controller.win32gui.SetWindowPos')
    @patch('win_manager.core.window_controller.win32gui.ShowWindow')
    @patch('win_manager.core.window_controller.win32gui.IsIconic')
    @patch('win_manager.core.window_controller.win32con.SW_RESTORE', 9)
    @patch('win_manager.core.window_controller.win32con.HWND_TOP', 0)
    @patch('win_manager.core.window_controller.win32con.SWP_SHOWWINDOW', 0x40)
    def test_move_window_minimized(self, mock_is_iconic, mock_show_window, mock_set_pos):
        """Test moving a minimized window."""
        controller = WindowController()
        
        # Mock window is minimized
        mock_is_iconic.return_value = True
        
        # Mock save_window_state
        with patch.object(controller, 'save_window_state') as mock_save:
            result = controller.move_window(12345, 100, 200, 300, 400)
        
        assert result == True
        mock_save.assert_called_once_with(12345)
        mock_is_iconic.assert_called_once_with(12345)
        mock_show_window.assert_called_once_with(12345, 9)  # SW_RESTORE
        mock_set_pos.assert_called_once_with(12345, 0, 100, 200, 300, 400, 0x40)
    
    @patch('win_manager.core.window_controller.win32gui.SetWindowPos')
    @patch('win_manager.core.window_controller.win32gui.ShowWindow')
    @patch('win_manager.core.window_controller.win32gui.IsIconic')
    def test_move_window_exception(self, mock_is_iconic, mock_show_window, mock_set_pos):
        """Test moving window with exception."""
        controller = WindowController()
        
        # Mock exception
        mock_is_iconic.side_effect = Exception("API Error")
        
        result = controller.move_window(12345, 100, 200, 300, 400)
        
        assert result == False
    
    @patch('win_manager.core.window_controller.win32gui.SetForegroundWindow')
    def test_bring_to_front_success(self, mock_set_foreground):
        """Test successful bring to front."""
        controller = WindowController()
        
        result = controller.bring_to_front(12345)
        
        assert result == True
        mock_set_foreground.assert_called_once_with(12345)
    
    @patch('win_manager.core.window_controller.win32gui.SetForegroundWindow')
    def test_bring_to_front_exception(self, mock_set_foreground):
        """Test bring to front with exception."""
        controller = WindowController()
        
        # Mock exception
        mock_set_foreground.side_effect = Exception("API Error")
        
        result = controller.bring_to_front(12345)
        
        assert result == False
    
    @patch('win_manager.core.window_controller.win32gui.ShowWindow')
    @patch('win_manager.core.window_controller.win32con.SW_MINIMIZE', 6)
    def test_minimize_window_success(self, mock_show_window):
        """Test successful window minimization."""
        controller = WindowController()
        
        result = controller.minimize_window(12345)
        
        assert result == True
        mock_show_window.assert_called_once_with(12345, 6)
    
    @patch('win_manager.core.window_controller.win32gui.ShowWindow')
    def test_minimize_window_exception(self, mock_show_window):
        """Test window minimization with exception."""
        controller = WindowController()
        
        # Mock exception
        mock_show_window.side_effect = Exception("API Error")
        
        result = controller.minimize_window(12345)
        
        assert result == False
    
    @patch('win_manager.core.window_controller.win32gui.ShowWindow')
    @patch('win_manager.core.window_controller.win32con.SW_MAXIMIZE', 3)
    def test_maximize_window_success(self, mock_show_window):
        """Test successful window maximization."""
        controller = WindowController()
        
        result = controller.maximize_window(12345)
        
        assert result == True
        mock_show_window.assert_called_once_with(12345, 3)
    
    @patch('win_manager.core.window_controller.win32gui.ShowWindow')
    def test_maximize_window_exception(self, mock_show_window):
        """Test window maximization with exception."""
        controller = WindowController()
        
        # Mock exception
        mock_show_window.side_effect = Exception("API Error")
        
        result = controller.maximize_window(12345)
        
        assert result == False
    
    @patch('win_manager.core.window_controller.win32gui.ShowWindow')
    @patch('win_manager.core.window_controller.win32con.SW_RESTORE', 9)
    def test_restore_window_success(self, mock_show_window):
        """Test successful window restoration."""
        controller = WindowController()
        
        result = controller.restore_window(12345)
        
        assert result == True
        mock_show_window.assert_called_once_with(12345, 9)
    
    @patch('win_manager.core.window_controller.win32gui.ShowWindow')
    def test_restore_window_exception(self, mock_show_window):
        """Test window restoration with exception."""
        controller = WindowController()
        
        # Mock exception
        mock_show_window.side_effect = Exception("API Error")
        
        result = controller.restore_window(12345)
        
        assert result == False
    
    @patch('win_manager.core.window_controller.win32gui.GetWindowRect')
    def test_get_window_rect_success(self, mock_get_rect):
        """Test successful window rectangle retrieval."""
        controller = WindowController()
        
        mock_get_rect.return_value = (100, 200, 300, 400)
        
        result = controller.get_window_rect(12345)
        
        assert result == (100, 200, 300, 400)
        mock_get_rect.assert_called_once_with(12345)
    
    @patch('win_manager.core.window_controller.win32gui.GetWindowRect')
    def test_get_window_rect_exception(self, mock_get_rect):
        """Test window rectangle retrieval with exception."""
        controller = WindowController()
        
        # Mock exception
        mock_get_rect.side_effect = Exception("API Error")
        
        result = controller.get_window_rect(12345)
        
        assert result is None
    
    @patch('win_manager.core.window_controller.win32gui.IsIconic')
    def test_is_window_minimized_true(self, mock_is_iconic):
        """Test checking if window is minimized (true case)."""
        controller = WindowController()
        
        mock_is_iconic.return_value = True
        
        result = controller.is_window_minimized(12345)
        
        assert result == True
        mock_is_iconic.assert_called_once_with(12345)
    
    @patch('win_manager.core.window_controller.win32gui.IsIconic')
    def test_is_window_minimized_false(self, mock_is_iconic):
        """Test checking if window is minimized (false case)."""
        controller = WindowController()
        
        mock_is_iconic.return_value = False
        
        result = controller.is_window_minimized(12345)
        
        assert result == False
        mock_is_iconic.assert_called_once_with(12345)
    
    @patch('win_manager.core.window_controller.win32gui.IsIconic')
    def test_is_window_minimized_exception(self, mock_is_iconic):
        """Test checking if window is minimized with exception."""
        controller = WindowController()
        
        # Mock exception
        mock_is_iconic.side_effect = Exception("API Error")
        
        result = controller.is_window_minimized(12345)
        
        assert result == False
    
    @patch('win_manager.core.window_controller.win32gui.GetWindowPlacement')
    def test_is_window_maximized_true(self, mock_get_placement):
        """Test checking if window is maximized (true case)."""
        controller = WindowController()
        
        # Mock placement with SW_MAXIMIZE (3)
        mock_get_placement.return_value = (0, 3, 0, (0, 0), (0, 0), (0, 0, 100, 100))
        
        result = controller.is_window_maximized(12345)
        
        assert result == True
        mock_get_placement.assert_called_once_with(12345)
    
    @patch('win_manager.core.window_controller.win32gui.GetWindowPlacement')
    def test_is_window_maximized_false(self, mock_get_placement):
        """Test checking if window is maximized (false case)."""
        controller = WindowController()
        
        # Mock placement with SW_RESTORE (9)
        mock_get_placement.return_value = (0, 9, 0, (0, 0), (0, 0), (0, 0, 100, 100))
        
        result = controller.is_window_maximized(12345)
        
        assert result == False
        mock_get_placement.assert_called_once_with(12345)
    
    @patch('win_manager.core.window_controller.win32gui.GetWindowPlacement')
    def test_is_window_maximized_exception(self, mock_get_placement):
        """Test checking if window is maximized with exception."""
        controller = WindowController()
        
        # Mock exception
        mock_get_placement.side_effect = Exception("API Error")
        
        result = controller.is_window_maximized(12345)
        
        assert result == False
    
    def test_window_state_persistence(self):
        """Test that window states are properly maintained."""
        controller = WindowController()
        
        # Simulate saving multiple window states
        test_state_1 = {
            'rect': (100, 200, 300, 400),
            'placement': {'showCmd': 1}
        }
        test_state_2 = {
            'rect': (500, 600, 700, 800),
            'placement': {'showCmd': 2}
        }
        
        controller.window_states[12345] = test_state_1
        controller.window_states[67890] = test_state_2
        
        # Verify both states are maintained
        assert len(controller.window_states) == 2
        assert controller.window_states[12345] == test_state_1
        assert controller.window_states[67890] == test_state_2
    
    def test_edge_case_negative_coordinates(self):
        """Test handling of negative coordinates."""
        controller = WindowController()
        
        with patch('win_manager.core.window_controller.win32gui.SetWindowPos') as mock_set_pos:
            with patch('win_manager.core.window_controller.win32gui.IsIconic', return_value=False):
                with patch.object(controller, 'save_window_state'):
                    result = controller.move_window(12345, -100, -200, 300, 400)
        
        assert result == True
        # Verify negative coordinates are passed through
        mock_set_pos.assert_called_once()
        args = mock_set_pos.call_args[0]
        assert args[2] == -100  # x coordinate
        assert args[3] == -200  # y coordinate


if __name__ == '__main__':
    pytest.main([__file__])