import logging
import os
from datetime import datetime


def setup_logger(log_dir='logs', level='INFO'):
    """
    Set up logger for the morning briefing system.

    Args:
        log_dir: Directory to store log files (default: 'logs')
        level: Logging level (default: 'INFO')

    Returns:
        Logger instance configured with file and console handlers
    """
    # Create log directory if it doesn't exist
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)

    # Create logger named 'morning_briefing'
    logger = logging.getLogger('morning_briefing')

    # Set logging level
    try:
        log_level = getattr(logging, level.upper())
    except AttributeError:
        log_level = logging.INFO
        logger.warning(f"Invalid log level '{level}', falling back to INFO")
    logger.setLevel(log_level)
    logger.propagate = False

    # Clear existing handlers to avoid duplicates
    logger.handlers.clear()

    # Create file handler with daily log file
    today = datetime.now().strftime("%Y-%m-%d")
    log_file = os.path.join(log_dir, f"briefing_{today}.log")
    file_handler = logging.FileHandler(log_file)
    file_handler.setLevel(log_level)

    # Create console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(log_level)

    # Create formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    # Add formatter to handlers
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)

    # Add both handlers to logger
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    return logger
