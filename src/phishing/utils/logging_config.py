"""Enhanced logging and error handling utilities."""

import json
import logging
import sys
import traceback
from typing import Any, Dict, Optional

from src.phishing.config.settings import settings


class JSONFormatter(logging.Formatter):
    """Custom JSON formatter for structured logging."""

    def format(self, record: logging.LogRecord) -> str:
        """Format log record as JSON."""
        log_data: Dict[str, Any] = {
            "timestamp": self.formatTime(record),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }

        if record.exc_info:
            exception_type = record.exc_info[0]
            log_data["exception"] = {
                "type": exception_type.__name__ if exception_type is not None else "Unknown",
                "message": str(record.exc_info[1]),
                "traceback": traceback.format_exception(*record.exc_info),
            }

        if hasattr(record, "user_id"):
            log_data["user_id"] = record.user_id

        if hasattr(record, "request_id"):
            log_data["request_id"] = record.request_id

        return json.dumps(log_data, default=str)


class SafeErrorHandler:
    """Context manager for safe error handling with logging."""

    def __init__(
        self,
        logger: logging.Logger,
        operation: str,
        user_safe_message: Optional[str] = None,
    ):
        """
        Initialize the safe error handler.

        Args:
            logger: Logger instance
            operation: Description of the operation being performed
            user_safe_message: Safe message to return to user (no internals)
        """
        self.logger = logger
        self.operation = operation
        self.user_safe_message = user_safe_message or "An error occurred"

    def __enter__(self):
        """Enter context."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Exit context with error handling."""
        if exc_type is not None:
            error_type_name = exc_type.__name__ if exc_type is not None else "Unknown"
            self.logger.error(
                f"Error during {self.operation}: {exc_val}",
                exc_info=True,
                extra={
                    "error_type": error_type_name,
                    "operation": self.operation,
                },
            )
        return False


def get_logger(name: str, log_level: Optional[str] = None) -> logging.Logger:
    """
    Get a configured logger with JSON output.

    Args:
        name: Logger name (usually __name__)
        log_level: Override log level (default from settings)

    Returns:
        Configured logger instance
    """
    logger = logging.getLogger(name)

    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)

        if settings.log_format == "json":
            formatter = JSONFormatter()
        else:
            formatter = logging.Formatter(
                fmt="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
                datefmt="%Y-%m-%dT%H:%M:%SZ",
            )

        handler.setFormatter(formatter)
        logger.addHandler(handler)

        level = log_level or settings.log_level
        logger.setLevel(getattr(logging, level))

    return logger


def safe_error_message(exc: Exception) -> str:
    """
    Convert an exception to a user-safe error message.

    Args:
        exc: The exception

    Returns:
        Safe error message string (no internal details)
    """
    exc_type = type(exc).__name__

    error_messages = {
        "URLValidationError": "Invalid URL format. Please check your input.",
        "FileNotFoundError": "Required model files not found. Please contact support.",
        "ValueError": "Invalid input data. Please try again.",
        "TimeoutError": "Request timed out. Please try again later.",
        "ConnectionError": "Network error. Please check your connection.",
        "PermissionError": "Access denied. Please contact support.",
        "MemoryError": "Server memory exceeded. Please try again later.",
        "OSError": "System error. Please try again later.",
    }

    return error_messages.get(exc_type, "An error occurred. Please try again or contact support.")


def log_structured(
    logger: logging.Logger,
    level: str,
    message: str,
    **kwargs,
) -> None:
    """
    Log with structured data.

    Args:
        logger: Logger instance
        level: Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        message: Main message
        **kwargs: Additional structured data
    """
    log_func = getattr(logger, level.lower(), logger.info)

    for key, value in kwargs.items():
        setattr(
            logging.LogRecord(
                name=logger.name,
                level=getattr(logging, level),
                pathname="",
                lineno=0,
                msg="",
                args=(),
                exc_info=None,
            ),
            key,
            value,
        )

    log_func(message, extra=kwargs)
