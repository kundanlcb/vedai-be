# logger.py
import logging
import sys
from datetime import datetime
from logging.handlers import TimedRotatingFileHandler

# --- ANSI Color Codes ---
class LogColors:
    RESET = "\033[0m"
    GREY = "\033[38;21m"
    YELLOW = "\033[33;21m"
    RED = "\033[31;21m"
    BOLD_RED = "\033[31;1m"
    GREEN = "\033[32;21m"
    CYAN = "\033[36;21m"

# --- Custom Formatter with Colors ---
class ColoredFormatter(logging.Formatter):
    """Custom log formatter with color support for console output."""
    FORMAT = "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s (%(filename)s:%(lineno)d)"
    DATEFMT = "%Y-%m-%d %H:%M:%S"

    COLORS = {
        logging.DEBUG: LogColors.CYAN,
        logging.INFO: LogColors.GREEN,
        logging.WARNING: LogColors.YELLOW,
        logging.ERROR: LogColors.RED,
        logging.CRITICAL: LogColors.BOLD_RED,
    }

    def format(self, record):
        log_fmt = self.COLORS.get(record.levelno, LogColors.RESET) + self.FORMAT + LogColors.RESET
        formatter = logging.Formatter(log_fmt, datefmt=self.DATEFMT)
        return formatter.format(record)

# --- Logger Setup Function ---
def get_logger(
    name: str = "app",
    level: int = logging.INFO,
    log_to_file: bool = True,
    filename: str = "app.log"
) -> logging.Logger:
    """
    Centralized logger function.
    - name: module name (__name__)
    - level: logging level (DEBUG, INFO, etc.)
    - log_to_file: enable rotating file handler
    - filename: file path for logs
    """
    logger = logging.getLogger(name)
    logger.setLevel(level)

    # Prevent adding duplicate handlers
    if logger.handlers:
        return logger

    # Console handler with color
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(ColoredFormatter())
    logger.addHandler(console_handler)

    # File handler (no colors)
    if log_to_file:
        file_formatter = logging.Formatter(
            "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s (%(filename)s:%(lineno)d)",
            "%Y-%m-%d %H:%M:%S"
        )
        file_handler = TimedRotatingFileHandler(filename, when="midnight", backupCount=7)
        file_handler.setFormatter(file_formatter)
        logger.addHandler(file_handler)

    return logger


# --- Optional: create a root logger to import directly ---
root_logger = get_logger("root")