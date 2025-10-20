import logging
import os
import sys
import time
from pathlib import Path
from typing import Dict, Any

# Color codes for terminal output
RESET = "\033[0m"
RED = "\033[31m"
GREEN = "\033[32m"
YELLOW = "\033[33m"
BLUE = "\033[34m"
MAGENTA = "\033[35m"
CYAN = "\033[36m"
WHITE = "\033[37m"

# Map log levels to colors
LEVEL_COLORS = {
    logging.DEBUG: BLUE,
    logging.INFO: GREEN,
    logging.WARNING: YELLOW,
    logging.ERROR: RED,
    logging.CRITICAL: MAGENTA,
}

class ColoredFormatter(logging.Formatter):
    """Custom formatter that adds colors to the log output."""
    
    def __init__(self, fmt=None, datefmt=None, style='%', validate=True):
        super().__init__(fmt, datefmt, style, validate)
    
    def format(self, record):
        # Save original message
        original_msg = record.msg
        
        # Add colors to the message based on log level
        color = LEVEL_COLORS.get(record.levelno, RESET)
        record.msg = f"{color}{record.msg}{RESET}"
        
        # Format the message
        formatted = super().format(record)
        
        # Restore original message
        record.msg = original_msg
        
        return formatted


class RequestIdFilter(logging.Filter):
    """Filter that adds request_id to log records."""
    
    def __init__(self, request_id=None):
        super().__init__()
        self.request_id = request_id

    def filter(self, record):
        record.request_id = getattr(record, 'request_id', self.request_id or '-')
        return True


def setup_logging():
    """
    Configure logging for the application.
    
    Sets up console handler with colored output and configures log level
    based on DEBUG environment variable.
    """
    # Determine log level from environment
    log_level = logging.DEBUG if os.getenv("DEBUG", "").lower() in ("true", "1", "yes") else logging.INFO
    
    # Create root logger
    logger = logging.getLogger()
    logger.setLevel(log_level)
    
    # Remove existing handlers to avoid duplication
    if logger.handlers:
        for handler in logger.handlers:
            logger.removeHandler(handler)
    
    # Create console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(log_level)
    
    # Create formatter
    log_format = "%(asctime)s | %(levelname)-8s | [%(request_id)s] | %(name)s:%(lineno)d - %(message)s"
    date_format = "%Y-%m-%d %H:%M:%S"
    formatter = ColoredFormatter(log_format, date_format)
    console_handler.setFormatter(formatter)
    
    # Add request ID filter
    console_handler.addFilter(RequestIdFilter())
    
    # Add handler to root logger
    logger.addHandler(console_handler)
    
    # Set propagate=False for uvicorn loggers to avoid duplicate logs
    for logger_name in ("uvicorn", "uvicorn.access"):
        uvicorn_logger = logging.getLogger(logger_name)
        uvicorn_logger.propagate = False
        
        # Add the same handler to uvicorn logger
        if not uvicorn_logger.handlers:
            uvicorn_logger.addHandler(console_handler)
    
    return logger


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger with the specified name.
    
    Args:
        name: The name of the logger, typically the module name.
        
    Returns:
        A logger instance.
    """
    return logging.getLogger(name)


# Setup logging when this module is imported
setup_logging()