"""
Performance tests for Win-Manager.
These tests measure performance characteristics and resource usage.
"""

import pytest
import os
import sys
import time
import psutil
import threading
from unittest.mock import patch, Mock
from typing import List

# Add src to path for testing
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from win_manager.core.window_manager import WindowManager
from win_manager.core.window_detector import WindowInfo
from win_manager.core.layout_manager import LayoutEngine
from win_manager.core.config_manager import ConfigManager
from win_manager.utils.hotkey_manager import HotkeyManager


class TestWindowManagerPerformance:
    """Performance tests for WindowManager operations."""
    
    @patch('win_manager.core.window_manager.WindowDetector')
    @patch('win_manager.core.window_manager.WindowController')
    @patch('win_manager.core.window_manager.LayoutEngine')
    @patch('win_manager.core.window_manager.ConfigManager')
    def test_large_window_set_performance(self, mock_config, mock_layout_engine, 
                                         mock_controller, mock_detector):
        """Test performance with different window set sizes."""
        # Setup mock config
        mock_config_instance = Mock()
        mock_config_instance.get.side_effect = lambda key, default=None: {
            "advanced.log_level": "INFO",
            "filters.ignore_fixed_size": True,
            "filters.ignore_minimized": True
        }.get(key, default)
        mock_config_instance.get_excluded_processes.return_value = []
        mock_config.return_value = mock_config_instance
        
        # Setup mock controller
        mock_controller_instance = Mock()
        mock_controller_instance.is_window_minimized.return_value = False
        mock_controller_instance.move_window.return_value = True
        mock_controller.return_value = mock_controller_instance
        
        # Setup mock layout engine
        mock_layout_engine_instance = Mock()
        mock_layout_engine.return_value = mock_layout_engine_instance
        
        # Test different window counts
        window_counts = [10, 50, 100, 200, 500]
        performance_results = {}
        
        for count in window_counts:
            # Generate windows with proper size
            windows = []
            positions = {}
            for i in range(count):
                window = WindowInfo(i, f"Window {i}", f"app{i}.exe", 100+i, 
                                  (i*5, i*5, i*5+800, i*5+600), True, True)
                windows.append(window)
                positions[i] = (i*10, i*10, 800, 600)
            
            # Setup mocks for this test
            mock_detector_instance = Mock()
            mock_detector_instance.enumerate_windows.return_value = windows
            mock_detector.return_value = mock_detector_instance
            
            mock_layout_engine_instance.apply_layout.return_value = positions
            
            # Create window manager and measure performance
            manager = WindowManager()
            
            # Measure window enumeration time
            start_time = time.time()
            manageable_windows = manager.get_manageable_windows()
            enum_time = time.time() - start_time
            
            # Measure organization time
            start_time = time.time()
            result = manager.organize_windows("grid")
            org_time = time.time() - start_time
            
            # Store results
            performance_results[count] = {
                'enum_time': enum_time,
                'org_time': org_time,
                'total_time': enum_time + org_time,
                'windows_processed': len(manageable_windows)
            }
            
            # Verify operation succeeded
            assert result == True
            assert len(manageable_windows) == count
        
        # Verify performance scaling
        for count in window_counts:
            result = performance_results[count]
            
            # Performance should remain reasonable
            assert result['enum_time'] < 0.5, f"Enumeration took too long for {count} windows: {result['enum_time']:.3f}s"
            assert result['org_time'] < 1.0, f"Organization took too long for {count} windows: {result['org_time']:.3f}s"
            assert result['total_time'] < 1.5, f"Total time too long for {count} windows: {result['total_time']:.3f}s"
        
        # Print performance summary
        print("\nWindow Manager Performance Results:")
        print("Windows | Enum Time | Org Time | Total Time")
        print("-" * 45)
        for count in window_counts:
            result = performance_results[count]
            print(f"{count:7d} | {result['enum_time']:8.3f}s | {result['org_time']:7.3f}s | {result['total_time']:9.3f}s")
    
    @patch('win_manager.core.window_manager.WindowDetector')
    @patch('win_manager.core.window_manager.WindowController')
    @patch('win_manager.core.window_manager.LayoutEngine')
    @patch('win_manager.core.window_manager.ConfigManager')
    def test_memory_usage_with_large_window_sets(self, mock_config, mock_layout_engine, 
                                                mock_controller, mock_detector):
        """Test memory usage with large window sets."""
        # Setup mocks
        mock_config_instance = Mock()
        mock_config_instance.get.side_effect = lambda key, default=None: {
            "advanced.log_level": "INFO",
            "filters.ignore_fixed_size": True,
            "filters.ignore_minimized": True
        }.get(key, default)
        mock_config_instance.get_excluded_processes.return_value = []
        mock_config.return_value = mock_config_instance
        
        mock_controller_instance = Mock()
        mock_controller_instance.is_window_minimized.return_value = False
        mock_controller_instance.move_window.return_value = True
        mock_controller.return_value = mock_controller_instance
        
        mock_layout_engine_instance = Mock()
        mock_layout_engine.return_value = mock_layout_engine_instance
        
        # Get initial memory usage
        process = psutil.Process()
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB
        
        # Create large window set
        window_count = 1000
        windows = []
        positions = {}
        for i in range(window_count):
            window = WindowInfo(i, f"Window {i}", f"app{i}.exe", 100+i, 
                              (i*5, i*5, i*5+800, i*5+600), True, True)
            windows.append(window)
            positions[i] = (i*10, i*10, 800, 600)
        
        mock_detector_instance = Mock()
        mock_detector_instance.enumerate_windows.return_value = windows
        mock_detector.return_value = mock_detector_instance
        
        mock_layout_engine_instance.apply_layout.return_value = positions
        
        # Create window manager and process windows
        manager = WindowManager()
        manageable_windows = manager.get_manageable_windows()
        result = manager.organize_windows("grid")
        
        # Get memory usage after processing
        final_memory = process.memory_info().rss / 1024 / 1024  # MB
        memory_increase = final_memory - initial_memory
        
        # Verify operation succeeded
        assert result == True
        assert len(manageable_windows) == window_count
        
        # Memory increase should be reasonable (less than 50MB for 1000 windows)
        assert memory_increase < 50, f"Memory increase too large: {memory_increase:.2f}MB"
        
        print(f"\nMemory Usage Test Results:")
        print(f"Initial memory: {initial_memory:.2f}MB")
        print(f"Final memory: {final_memory:.2f}MB")
        print(f"Memory increase: {memory_increase:.2f}MB")
        print(f"Memory per window: {memory_increase/window_count*1024:.2f}KB")


class TestLayoutEnginePerformance:
    """Performance tests for LayoutEngine operations."""
    
    def test_layout_calculation_performance(self):
        """Test performance of layout calculations."""
        layout_engine = LayoutEngine()
        
        # Test different layout types with various window counts
        layout_types = ["cascade", "grid", "stack"]
        window_counts = [10, 50, 100, 200]
        
        performance_results = {}
        
        for layout_type in layout_types:
            performance_results[layout_type] = {}
            
            for count in window_counts:
                # Generate test windows
                windows = []
                for i in range(count):
                    window = WindowInfo(i, f"Window {i}", f"app{i}.exe", 100+i, 
                                      (i*10, i*10, i*10+800, i*10+600), True, True)
                    windows.append(window)
                
                # Measure layout calculation time
                start_time = time.time()
                positions = layout_engine.apply_layout(layout_type, windows)
                calc_time = time.time() - start_time
                
                performance_results[layout_type][count] = {
                    'calc_time': calc_time,
                    'positions_count': len(positions)
                }
                
                # Verify layout calculation succeeded
                assert len(positions) == count
                
                # Performance should be reasonable
                assert calc_time < 0.5, f"Layout calculation too slow for {layout_type} with {count} windows: {calc_time:.3f}s"
        
        # Print performance summary
        print("\nLayout Engine Performance Results:")
        print("Layout Type | 10 Win | 50 Win | 100 Win | 200 Win")
        print("-" * 51)
        for layout_type in layout_types:
            times = [performance_results[layout_type][count]['calc_time'] for count in window_counts]
            print(f"{layout_type:11s} | {times[0]:5.3f}s | {times[1]:5.3f}s | {times[2]:6.3f}s | {times[3]:6.3f}s")


class TestConfigManagerPerformance:
    """Performance tests for ConfigManager operations."""
    
    def test_config_operations_performance(self):
        """Test performance of configuration operations."""
        import tempfile
        
        with tempfile.TemporaryDirectory() as temp_dir:
            config_manager = ConfigManager(temp_dir)
            
            # Test bulk configuration operations
            operation_counts = [100, 500, 1000, 2000]
            performance_results = {}
            
            for count in operation_counts:
                # Test bulk set operations
                start_time = time.time()
                for i in range(count):
                    config_manager.set(f"test.key_{i}", f"value_{i}")
                set_time = time.time() - start_time
                
                # Test bulk get operations
                start_time = time.time()
                for i in range(count):
                    value = config_manager.get(f"test.key_{i}")
                    assert value == f"value_{i}"
                get_time = time.time() - start_time
                
                # Test save operation
                start_time = time.time()
                result = config_manager.save_config()
                save_time = time.time() - start_time
                
                performance_results[count] = {
                    'set_time': set_time,
                    'get_time': get_time,
                    'save_time': save_time,
                    'total_time': set_time + get_time + save_time
                }
                
                # Verify operations succeeded
                assert result == True
                
                # Performance should be reasonable
                assert set_time < 1.0, f"Set operations too slow for {count} items: {set_time:.3f}s"
                assert get_time < 1.0, f"Get operations too slow for {count} items: {get_time:.3f}s"
                assert save_time < 2.0, f"Save operation too slow for {count} items: {save_time:.3f}s"
        
        # Print performance summary
        print("\nConfig Manager Performance Results:")
        print("Operations | Set Time | Get Time | Save Time | Total Time")
        print("-" * 58)
        for count in operation_counts:
            result = performance_results[count]
            print(f"{count:10d} | {result['set_time']:7.3f}s | {result['get_time']:7.3f}s | {result['save_time']:8.3f}s | {result['total_time']:9.3f}s")


class TestHotkeyManagerPerformance:
    """Performance tests for HotkeyManager operations."""
    
    def test_hotkey_registration_performance(self):
        """Test performance of hotkey registration."""
        manager = HotkeyManager()
        
        # Test bulk hotkey registration
        hotkey_counts = [10, 50, 100, 200]
        performance_results = {}
        
        for count in hotkey_counts:
            # Generate test hotkeys
            hotkeys = []
            callbacks = []
            for i in range(count):
                hotkey = f"ctrl+alt+{chr(ord('a') + i % 26)}{i // 26}"
                callback = Mock()
                hotkeys.append(hotkey)
                callbacks.append(callback)
            
            # Test registration performance
            start_time = time.time()
            for i in range(count):
                result = manager.register_hotkey(hotkeys[i], callbacks[i])
                assert result == True
            reg_time = time.time() - start_time
            
            # Test lookup performance
            start_time = time.time()
            registered_hotkeys = manager.get_registered_hotkeys()
            lookup_time = time.time() - start_time
            
            # Test unregistration performance
            start_time = time.time()
            for hotkey in hotkeys:
                result = manager.unregister_hotkey(hotkey)
                assert result == True
            unreg_time = time.time() - start_time
            
            performance_results[count] = {
                'reg_time': reg_time,
                'lookup_time': lookup_time,
                'unreg_time': unreg_time,
                'total_time': reg_time + lookup_time + unreg_time
            }
            
            # Verify operations
            assert len(registered_hotkeys) == count
            assert len(manager.get_registered_hotkeys()) == 0
            
            # Performance should be reasonable
            assert reg_time < 1.0, f"Registration too slow for {count} hotkeys: {reg_time:.3f}s"
            assert lookup_time < 0.1, f"Lookup too slow for {count} hotkeys: {lookup_time:.3f}s"
            assert unreg_time < 1.0, f"Unregistration too slow for {count} hotkeys: {unreg_time:.3f}s"
        
        # Print performance summary
        print("\nHotkey Manager Performance Results:")
        print("Hotkeys | Reg Time | Lookup Time | Unreg Time | Total Time")
        print("-" * 59)
        for count in hotkey_counts:
            result = performance_results[count]
            print(f"{count:7d} | {result['reg_time']:7.3f}s | {result['lookup_time']:10.3f}s | {result['unreg_time']:9.3f}s | {result['total_time']:9.3f}s")


class TestConcurrentOperations:
    """Performance tests for concurrent operations."""
    
    @patch('win_manager.core.window_manager.WindowDetector')
    @patch('win_manager.core.window_manager.WindowController')
    @patch('win_manager.core.window_manager.LayoutEngine')
    @patch('win_manager.core.window_manager.ConfigManager')
    def test_concurrent_window_operations(self, mock_config, mock_layout_engine, 
                                         mock_controller, mock_detector):
        """Test concurrent window operations performance."""
        # Setup mocks
        mock_config_instance = Mock()
        mock_config_instance.get.side_effect = lambda key, default=None: {
            "advanced.log_level": "INFO",
            "filters.ignore_fixed_size": True,
            "filters.ignore_minimized": True
        }.get(key, default)
        mock_config_instance.get_excluded_processes.return_value = []
        mock_config.return_value = mock_config_instance
        
        mock_controller_instance = Mock()
        mock_controller_instance.is_window_minimized.return_value = False
        mock_controller_instance.move_window.return_value = True
        mock_controller.return_value = mock_controller_instance
        
        mock_layout_engine_instance = Mock()
        mock_layout_engine.return_value = mock_layout_engine_instance
        
        # Generate test windows
        windows = []
        positions = {}
        for i in range(100):
            window = WindowInfo(i, f"Window {i}", f"app{i}.exe", 100+i, 
                              (i*5, i*5, i*5+800, i*5+600), True, True)
            windows.append(window)
            positions[i] = (i*10, i*10, 800, 600)
        
        mock_detector_instance = Mock()
        mock_detector_instance.enumerate_windows.return_value = windows
        mock_detector.return_value = mock_detector_instance
        
        mock_layout_engine_instance.apply_layout.return_value = positions
        
        # Test concurrent operations
        thread_counts = [1, 2, 4, 8]
        performance_results = {}
        
        for thread_count in thread_counts:
            managers = [WindowManager() for _ in range(thread_count)]
            results = [None] * thread_count
            threads = []
            
            def worker(index):
                manager = managers[index]
                start_time = time.time()
                manageable_windows = manager.get_manageable_windows()
                result = manager.organize_windows("grid")
                execution_time = time.time() - start_time
                results[index] = {
                    'success': result,
                    'window_count': len(manageable_windows),
                    'execution_time': execution_time
                }
            
            # Start concurrent operations
            start_time = time.time()
            for i in range(thread_count):
                thread = threading.Thread(target=worker, args=(i,))
                threads.append(thread)
                thread.start()
            
            # Wait for completion
            for thread in threads:
                thread.join()
            
            total_time = time.time() - start_time
            
            performance_results[thread_count] = {
                'total_time': total_time,
                'individual_times': [r['execution_time'] for r in results],
                'all_succeeded': all(r['success'] for r in results)
            }
            
            # Verify all operations succeeded
            assert all(r['success'] for r in results)
            assert all(r['window_count'] == 100 for r in results)
            
            # Performance should be reasonable
            assert total_time < 5.0, f"Concurrent operations too slow with {thread_count} threads: {total_time:.3f}s"
        
        # Print performance summary
        print("\nConcurrent Operations Performance Results:")
        print("Threads | Total Time | Avg Individual Time | All Succeeded")
        print("-" * 62)
        for thread_count in thread_counts:
            result = performance_results[thread_count]
            avg_time = sum(result['individual_times']) / len(result['individual_times'])
            print(f"{thread_count:7d} | {result['total_time']:9.3f}s | {avg_time:18.3f}s | {result['all_succeeded']}")


if __name__ == '__main__':
    pytest.main([__file__, '-v', '-s'])