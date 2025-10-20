"""
Core functionality for the Obsidian Chat application.

This package contains core components like logging and middleware.
"""

from app.core.logging import get_logger, setup_logging
from app.core.middleware import setup_request_logging

__all__ = ["get_logger", "setup_logging", "setup_request_logging"]