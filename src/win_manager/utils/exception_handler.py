"""
Exception handling utilities for Win-Manager.
"""

import logging
import traceback
import sys
from typing import Optional, Callable, Any
from functools import wraps


class WinManagerException(Exception):
    """Base exception for Win-Manager."""
    pass


class WindowDetectionException(WinManagerException):
    """Exception raised during window detection."""
    pass


class WindowControlException(WinManagerException):
    """Exception raised during window control operations."""
    pass


class LayoutException(WinManagerException):
    """Exception raised during layout operations."""
    pass


class ConfigurationException(WinManagerException):
    """Exception raised during configuration operations."""
    pass


class HotkeyException(WinManagerException):
    """Exception raised during hotkey operations."""
    pass


class ExceptionHandler:
    """Centralized exception handling for the application."""
    
    def __init__(self, logger: Optional[logging.Logger] = None):
        self.logger = logger or logging.getLogger(__name__)
        self.error_callbacks: list = []
    
    def add_error_callback(self, callback: Callable[[Exception], None]):
        """Add callback to be called when an exception occurs."""
        self.error_callbacks.append(callback)
    
    def handle_exception(self, exception: Exception, context: str = "") -> None:
        """Handle an exception with logging and callbacks."""
        error_msg = f"Exception in {context}: {str(exception)}"
        self.logger.error(error_msg)
        self.logger.debug(traceback.format_exc())
        
        # Call error callbacks
        for callback in self.error_callbacks:
            try:
                callback(exception)
            except Exception as callback_error:
                self.logger.error(f"Error in exception callback: {callback_error}")
    
    def safe_execute(self, func: Callable, *args, **kwargs) -> tuple[bool, Any]:
        """Execute function safely with exception handling."""
        try:
            result = func(*args, **kwargs)
            return True, result
        except Exception as e:
            self.handle_exception(e, f"safe_execute({func.__name__})")
            return False, None
    
    def with_exception_handling(self, context: str = ""):
        """Decorator for automatic exception handling."""
        def decorator(func: Callable) -> Callable:
            @wraps(func)
            def wrapper(*args, **kwargs):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    self.handle_exception(e, context or func.__name__)
                    return None
            return wrapper
        return decorator
    
    def setup_global_exception_handler(self):
        """Setup global exception handler for unhandled exceptions."""
        def handle_exception(exc_type, exc_value, exc_traceback):
            if issubclass(exc_type, KeyboardInterrupt):
                sys.__excepthook__(exc_type, exc_value, exc_traceback)
                return
            
            self.logger.critical(
                "Uncaught exception",
                exc_info=(exc_type, exc_value, exc_traceback)
            )
        
        sys.excepthook = handle_exception


def safe_call(func: Callable, *args, default=None, logger: Optional[logging.Logger] = None, **kwargs):
    """Safely call a function with exception handling."""
    try:
        return func(*args, **kwargs)
    except Exception as e:
        if logger:
            logger.error(f"Exception in {func.__name__}: {e}")
        return default


def retry_on_exception(max_attempts: int = 3, delay: float = 1.0, exceptions: tuple = (Exception,)):
    """Decorator to retry function on exception."""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            import time
            last_exception = None
            
            for attempt in range(max_attempts):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    last_exception = e
                    if attempt < max_attempts - 1:
                        time.sleep(delay)
                    else:
                        raise last_exception
            
            return None
        return wrapper
    return decorator


def log_exceptions(logger: Optional[logging.Logger] = None):
    """Decorator to log exceptions without suppressing them."""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                if logger:
                    logger.error(f"Exception in {func.__name__}: {e}")
                    logger.debug(traceback.format_exc())
                raise
        return wrapper
    return decorator


class ErrorReporter:
    """Reports errors to various destinations."""
    
    def __init__(self):
        self.destinations = []
    
    def add_destination(self, destination: Callable[[str, Exception], None]):
        """Add error reporting destination."""
        self.destinations.append(destination)
    
    def report_error(self, message: str, exception: Exception):
        """Report error to all destinations."""
        for destination in self.destinations:
            try:
                destination(message, exception)
            except Exception as e:
                # Avoid recursive error reporting
                print(f"Error in error reporter: {e}")
    
    def report_to_file(self, filepath: str):
        """Add file destination for error reporting."""
        def file_reporter(message: str, exception: Exception):
            with open(filepath, 'a', encoding='utf-8') as f:
                f.write(f"{message}: {exception}\n")
                f.write(traceback.format_exc())
                f.write("\n" + "="*50 + "\n")
        
        self.add_destination(file_reporter)
    
    def report_to_console(self):
        """Add console destination for error reporting."""
        def console_reporter(message: str, exception: Exception):
            print(f"ERROR: {message}: {exception}")
            print(traceback.format_exc())
        
        self.add_destination(console_reporter)