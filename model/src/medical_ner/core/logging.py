"""
Logging configuration for the application.
This module sets up logging with appropriate formatters and handlers.
"""

import logging
import sys

from ..core.config import settings


def configure_logging() -> None:
    """
    Configure logging for the application based on settings.

    Creates console handlers with appropriate formatting and sets the log level
    based on configuration.
    """
    # Get log level from settings
    log_level = getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO)

    # Create formatters
    simple_formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    detailed_formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(pathname)s:%(lineno)d - %(message)s"
    )

    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)

    # Clear existing handlers if any
    if root_logger.handlers:
        for handler in root_logger.handlers:
            root_logger.removeHandler(handler)

    # Create console handler for info and below
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(log_level)
    console_handler.setFormatter(simple_formatter)
    console_handler.addFilter(lambda record: record.levelno <= logging.INFO)
    root_logger.addHandler(console_handler)

    # Create error console handler for warnings and above
    error_console_handler = logging.StreamHandler(sys.stderr)
    error_console_handler.setLevel(logging.WARNING)
    error_console_handler.setFormatter(detailed_formatter)
    root_logger.addHandler(error_console_handler)

    # Reduce verbosity of some loggers
    for logger_name in ["uvicorn", "uvicorn.access"]:
        mod_logger = logging.getLogger(logger_name)
        mod_logger.setLevel(max(log_level, logging.WARNING))


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger with the given name.

    Args:
        name: The name for the logger

    Returns:
        logging.Logger: Configured logger instance
    """
    return logging.getLogger(name)
