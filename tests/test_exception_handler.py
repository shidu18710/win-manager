"""
Unit tests for ExceptionHandler.
"""

import pytest
import os
import sys
import logging
import tempfile
from unittest.mock import patch, MagicMock, Mock
from io import StringIO

# Add src to path for testing
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from win_manager.utils.exception_handler import (
    ExceptionHandler, ErrorReporter, WinManagerException,
    WindowDetectionException, WindowControlException, LayoutException,
    ConfigurationException, HotkeyException, safe_call, retry_on_exception,
    log_exceptions
)


class TestExceptionHandler:
    """Test suite for ExceptionHandler class."""
    
    def test_init_default_logger(self):
        """Test initialization with default logger."""
        handler = ExceptionHandler()
        assert handler.logger is not None
        assert handler.error_callbacks == []
    
    def test_init_custom_logger(self):
        """Test initialization with custom logger."""
        custom_logger = logging.getLogger("test_logger")
        handler = ExceptionHandler(custom_logger)
        assert handler.logger == custom_logger
        assert handler.error_callbacks == []
    
    def test_add_error_callback(self):
        """Test adding error callbacks."""
        handler = ExceptionHandler()
        
        def callback1(exc):
            pass
        
        def callback2(exc):
            pass
        
        handler.add_error_callback(callback1)
        handler.add_error_callback(callback2)
        
        assert len(handler.error_callbacks) == 2
        assert callback1 in handler.error_callbacks
        assert callback2 in handler.error_callbacks
    
    def test_handle_exception_basic(self):
        """Test basic exception handling."""
        logger = Mock()
        handler = ExceptionHandler(logger)
        
        test_exception = ValueError("Test error")
        handler.handle_exception(test_exception, "test_context")
        
        logger.error.assert_called_once_with("Exception in test_context: Test error")
        logger.debug.assert_called_once()
    
    def test_handle_exception_with_callbacks(self):
        """Test exception handling with callbacks."""
        logger = Mock()
        handler = ExceptionHandler(logger)
        
        callback1 = Mock()
        callback2 = Mock()
        handler.add_error_callback(callback1)
        handler.add_error_callback(callback2)
        
        test_exception = ValueError("Test error")
        handler.handle_exception(test_exception, "test_context")
        
        callback1.assert_called_once_with(test_exception)
        callback2.assert_called_once_with(test_exception)
    
    def test_handle_exception_callback_error(self):
        """Test exception handling when callback raises error."""
        logger = Mock()
        handler = ExceptionHandler(logger)
        
        def bad_callback(exc):
            raise RuntimeError("Callback error")
        
        handler.add_error_callback(bad_callback)
        
        test_exception = ValueError("Test error")
        handler.handle_exception(test_exception, "test_context")
        
        # Should log both original error and callback error
        assert logger.error.call_count == 2
        logger.error.assert_any_call("Exception in test_context: Test error")
        logger.error.assert_any_call("Error in exception callback: Callback error")
    
    def test_safe_execute_success(self):
        """Test safe execution with successful function."""
        handler = ExceptionHandler()
        
        def test_func(x, y):
            return x + y
        
        success, result = handler.safe_execute(test_func, 5, 3)
        
        assert success == True
        assert result == 8
    
    def test_safe_execute_failure(self):
        """Test safe execution with failing function."""
        logger = Mock()
        handler = ExceptionHandler(logger)
        
        def test_func():
            raise ValueError("Test error")
        
        success, result = handler.safe_execute(test_func)
        
        assert success == False
        assert result is None
        logger.error.assert_called_once()
    
    def test_with_exception_handling_decorator_success(self):
        """Test exception handling decorator with successful function."""
        handler = ExceptionHandler()
        
        @handler.with_exception_handling("test_context")
        def test_func(x, y):
            return x * y
        
        result = test_func(4, 5)
        assert result == 20
    
    def test_with_exception_handling_decorator_failure(self):
        """Test exception handling decorator with failing function."""
        logger = Mock()
        handler = ExceptionHandler(logger)
        
        @handler.with_exception_handling("test_context")
        def test_func():
            raise ValueError("Test error")
        
        result = test_func()
        
        assert result is None
        logger.error.assert_called_once_with("Exception in test_context: Test error")
    
    def test_with_exception_handling_decorator_default_context(self):
        """Test exception handling decorator with default context."""
        logger = Mock()
        handler = ExceptionHandler(logger)
        
        @handler.with_exception_handling()
        def test_func():
            raise ValueError("Test error")
        
        result = test_func()
        
        assert result is None
        logger.error.assert_called_once_with("Exception in test_func: Test error")
    
    def test_setup_global_exception_handler(self):
        """Test setting up global exception handler."""
        logger = Mock()
        handler = ExceptionHandler(logger)
        
        original_hook = sys.excepthook
        
        try:
            handler.setup_global_exception_handler()
            
            # Test that sys.excepthook was changed
            assert sys.excepthook != original_hook
            
            # Test handling of non-KeyboardInterrupt exception
            test_exception = ValueError("Test error")
            sys.excepthook(type(test_exception), test_exception, None)
            
            logger.critical.assert_called_once()
            
        finally:
            # Restore original hook
            sys.excepthook = original_hook
    
    def test_setup_global_exception_handler_keyboard_interrupt(self):
        """Test global exception handler with KeyboardInterrupt."""
        logger = Mock()
        handler = ExceptionHandler(logger)
        
        original_hook = sys.excepthook
        
        try:
            handler.setup_global_exception_handler()
            
            # Mock sys.__excepthook__ to verify it's called
            with patch('sys.__excepthook__') as mock_hook:
                test_exception = KeyboardInterrupt()
                sys.excepthook(type(test_exception), test_exception, None)
                
                mock_hook.assert_called_once()
                logger.critical.assert_not_called()
                
        finally:
            # Restore original hook
            sys.excepthook = original_hook


class TestCustomExceptions:
    """Test suite for custom exception classes."""
    
    def test_win_manager_exception(self):
        """Test base WinManagerException."""
        exc = WinManagerException("Test message")
        assert str(exc) == "Test message"
        assert isinstance(exc, Exception)
    
    def test_window_detection_exception(self):
        """Test WindowDetectionException."""
        exc = WindowDetectionException("Detection error")
        assert str(exc) == "Detection error"
        assert isinstance(exc, WinManagerException)
    
    def test_window_control_exception(self):
        """Test WindowControlException."""
        exc = WindowControlException("Control error")
        assert str(exc) == "Control error"
        assert isinstance(exc, WinManagerException)
    
    def test_layout_exception(self):
        """Test LayoutException."""
        exc = LayoutException("Layout error")
        assert str(exc) == "Layout error"
        assert isinstance(exc, WinManagerException)
    
    def test_configuration_exception(self):
        """Test ConfigurationException."""
        exc = ConfigurationException("Config error")
        assert str(exc) == "Config error"
        assert isinstance(exc, WinManagerException)
    
    def test_hotkey_exception(self):
        """Test HotkeyException."""
        exc = HotkeyException("Hotkey error")
        assert str(exc) == "Hotkey error"
        assert isinstance(exc, WinManagerException)


class TestSafeCall:
    """Test suite for safe_call function."""
    
    def test_safe_call_success(self):
        """Test safe_call with successful function."""
        def test_func(x, y):
            return x + y
        
        result = safe_call(test_func, 5, 3)
        assert result == 8
    
    def test_safe_call_failure_default(self):
        """Test safe_call with failing function and default value."""
        def test_func():
            raise ValueError("Test error")
        
        result = safe_call(test_func, default="fallback")
        assert result == "fallback"
    
    def test_safe_call_failure_none(self):
        """Test safe_call with failing function and no default."""
        def test_func():
            raise ValueError("Test error")
        
        result = safe_call(test_func)
        assert result is None
    
    def test_safe_call_with_logger(self):
        """Test safe_call with logger."""
        logger = Mock()
        
        def test_func():
            raise ValueError("Test error")
        
        result = safe_call(test_func, logger=logger)
        
        assert result is None
        logger.error.assert_called_once_with("Exception in test_func: Test error")
    
    def test_safe_call_with_kwargs(self):
        """Test safe_call with keyword arguments."""
        def test_func(x, y=10):
            return x * y
        
        result = safe_call(test_func, 5, y=3)
        assert result == 15


class TestRetryOnException:
    """Test suite for retry_on_exception decorator."""
    
    def test_retry_success_first_attempt(self):
        """Test retry decorator with successful first attempt."""
        call_count = 0
        
        @retry_on_exception(max_attempts=3)
        def test_func():
            nonlocal call_count
            call_count += 1
            return "success"
        
        result = test_func()
        
        assert result == "success"
        assert call_count == 1
    
    def test_retry_success_second_attempt(self):
        """Test retry decorator with successful second attempt."""
        call_count = 0
        
        @retry_on_exception(max_attempts=3, delay=0.1)
        def test_func():
            nonlocal call_count
            call_count += 1
            if call_count == 1:
                raise ValueError("First attempt fails")
            return "success"
        
        result = test_func()
        
        assert result == "success"
        assert call_count == 2
    
    def test_retry_all_attempts_fail(self):
        """Test retry decorator when all attempts fail."""
        call_count = 0
        
        @retry_on_exception(max_attempts=3, delay=0.1)
        def test_func():
            nonlocal call_count
            call_count += 1
            raise ValueError(f"Attempt {call_count} fails")
        
        with pytest.raises(ValueError, match="Attempt 3 fails"):
            test_func()
        
        assert call_count == 3
    
    def test_retry_specific_exceptions(self):
        """Test retry decorator with specific exception types."""
        call_count = 0
        
        @retry_on_exception(max_attempts=3, exceptions=(ValueError,))
        def test_func():
            nonlocal call_count
            call_count += 1
            if call_count == 1:
                raise ValueError("Retryable error")
            return "success"
        
        result = test_func()
        
        assert result == "success"
        assert call_count == 2
    
    def test_retry_non_retryable_exception(self):
        """Test retry decorator with non-retryable exception."""
        call_count = 0
        
        @retry_on_exception(max_attempts=3, exceptions=(ValueError,))
        def test_func():
            nonlocal call_count
            call_count += 1
            raise TypeError("Non-retryable error")
        
        with pytest.raises(TypeError, match="Non-retryable error"):
            test_func()
        
        assert call_count == 1


class TestLogExceptions:
    """Test suite for log_exceptions decorator."""
    
    def test_log_exceptions_success(self):
        """Test log_exceptions decorator with successful function."""
        logger = Mock()
        
        @log_exceptions(logger)
        def test_func(x, y):
            return x + y
        
        result = test_func(5, 3)
        
        assert result == 8
        logger.error.assert_not_called()
    
    def test_log_exceptions_failure(self):
        """Test log_exceptions decorator with failing function."""
        logger = Mock()
        
        @log_exceptions(logger)
        def test_func():
            raise ValueError("Test error")
        
        with pytest.raises(ValueError, match="Test error"):
            test_func()
        
        logger.error.assert_called_once_with("Exception in test_func: Test error")
        logger.debug.assert_called_once()
    
    def test_log_exceptions_no_logger(self):
        """Test log_exceptions decorator without logger."""
        @log_exceptions()
        def test_func():
            raise ValueError("Test error")
        
        with pytest.raises(ValueError, match="Test error"):
            test_func()


class TestErrorReporter:
    """Test suite for ErrorReporter class."""
    
    def test_init(self):
        """Test ErrorReporter initialization."""
        reporter = ErrorReporter()
        assert reporter.destinations == []
    
    def test_add_destination(self):
        """Test adding error destinations."""
        reporter = ErrorReporter()
        
        def destination1(msg, exc):
            pass
        
        def destination2(msg, exc):
            pass
        
        reporter.add_destination(destination1)
        reporter.add_destination(destination2)
        
        assert len(reporter.destinations) == 2
        assert destination1 in reporter.destinations
        assert destination2 in reporter.destinations
    
    def test_report_error(self):
        """Test reporting error to destinations."""
        reporter = ErrorReporter()
        
        dest1 = Mock()
        dest2 = Mock()
        reporter.add_destination(dest1)
        reporter.add_destination(dest2)
        
        test_exception = ValueError("Test error")
        reporter.report_error("Test message", test_exception)
        
        dest1.assert_called_once_with("Test message", test_exception)
        dest2.assert_called_once_with("Test message", test_exception)
    
    def test_report_error_destination_failure(self):
        """Test reporting error when destination fails."""
        reporter = ErrorReporter()
        
        def bad_destination(msg, exc):
            raise RuntimeError("Destination error")
        
        reporter.add_destination(bad_destination)
        
        test_exception = ValueError("Test error")
        
        # Should not raise exception, just print error
        with patch('builtins.print') as mock_print:
            reporter.report_error("Test message", test_exception)
            mock_print.assert_called_once_with("Error in error reporter: Destination error")
    
    def test_report_to_file(self):
        """Test file destination for error reporting."""
        reporter = ErrorReporter()
        
        with tempfile.NamedTemporaryFile(mode='w', delete=False) as temp_file:
            temp_path = temp_file.name
        
        try:
            reporter.report_to_file(temp_path)
            
            test_exception = ValueError("Test error")
            reporter.report_error("Test message", test_exception)
            
            # Check file contents
            with open(temp_path, 'r', encoding='utf-8') as f:
                content = f.read()
                assert "Test message: Test error" in content
                assert "=" * 50 in content
                
        finally:
            os.unlink(temp_path)
    
    def test_report_to_console(self):
        """Test console destination for error reporting."""
        reporter = ErrorReporter()
        reporter.report_to_console()
        
        test_exception = ValueError("Test error")
        
        with patch('builtins.print') as mock_print:
            reporter.report_error("Test message", test_exception)
            
            # Should print error message and traceback
            assert mock_print.call_count == 2
            mock_print.assert_any_call("ERROR: Test message: Test error")


if __name__ == '__main__':
    pytest.main([__file__])