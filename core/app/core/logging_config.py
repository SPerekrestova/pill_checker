import logging
import sys
from pathlib import Path

from .config import settings


def setup_logging() -> logging.Logger:
    """
    Configure logging for the application.
    Returns a configured logger instance.
    """
    # Create logs directory if it doesn't exist
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)

    # Create logger
    logger = logging.getLogger("pillchecker")

    # Parse log level from settings, handling any comments
    log_level = (
        settings.LOG_LEVEL.split("#")[0].strip()
        if "#" in settings.LOG_LEVEL
        else settings.LOG_LEVEL
    )
    logger.setLevel(getattr(logging, log_level))

    # Create formatters
    console_format = logging.Formatter("%(levelname)s - %(message)s")
    file_format = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )

    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(getattr(logging, log_level))
    console_handler.setFormatter(console_format)

    # File handler
    file_handler = logging.FileHandler(log_dir / settings.LOG_FILE)
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(file_format)

    # Remove existing handlers to avoid duplicates
    logger.handlers.clear()

    # Add handlers
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)

    # Prevent propagation to root logger
    logger.propagate = False

    return logger


# Create and export logger instance
logger = setup_logging()
