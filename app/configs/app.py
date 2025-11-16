"""Application configuration constants."""

import logging

# Application metadata
APP_NAME: str = "Yale Alumni Assistant"
VERSION: str = "1.0.0"

# Default agent mode configuration
DEFAULT_AGENT_MODE: str = "background_finder"  # Options: "background_finder, "email_finder"

# Logging configuration
# Set to logging.INFO for production, logging.DEBUG for verbose logging
# To disable terminal logging, set to logging.CRITICAL or use a file handler only
LOG_LEVEL = logging.CRITICAL


# Configure logging
def setup_logging():
    """Setup application logging configuration."""
    # Create logger
    logger = logging.getLogger(APP_NAME)
    logger.setLevel(LOG_LEVEL)

    # Clear any existing handlers
    logger.handlers.clear()

    # Create console handler with a higher log level
    console_handler = logging.StreamHandler()
    console_handler.setLevel(LOG_LEVEL)

    # Create formatter and add it to the handler
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    console_handler.setFormatter(formatter)

    # Add the handler to the logger
    logger.addHandler(console_handler)

    return logger


# Initialize logger
logger = setup_logging()
