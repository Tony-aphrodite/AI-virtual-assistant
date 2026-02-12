"""
Structured logging configuration using structlog.
Provides JSON-formatted logs with context for production environments.
"""

import logging
import sys
from typing import Any

import structlog
from structlog.types import EventDict, Processor

from src.config import settings


def add_app_context(logger: Any, method_name: str, event_dict: EventDict) -> EventDict:
    """Add application context to every log entry."""
    event_dict["app"] = settings.app_name
    event_dict["environment"] = settings.environment
    return event_dict


def censor_sensitive_data(logger: Any, method_name: str, event_dict: EventDict) -> EventDict:
    """
    Censor sensitive data from logs.
    Redacts API keys, tokens, passwords, and other sensitive information.
    """
    sensitive_keys = {
        "password",
        "token",
        "api_key",
        "secret",
        "authorization",
        "auth_token",
        "access_token",
        "refresh_token",
        "private_key",
    }

    def censor_dict(d: dict) -> dict:
        """Recursively censor sensitive keys in dictionary."""
        censored = {}
        for key, value in d.items():
            key_lower = key.lower()
            if any(sensitive in key_lower for sensitive in sensitive_keys):
                censored[key] = "***REDACTED***"
            elif isinstance(value, dict):
                censored[key] = censor_dict(value)
            elif isinstance(value, list):
                censored[key] = [
                    censor_dict(item) if isinstance(item, dict) else item
                    for item in value
                ]
            else:
                censored[key] = value
        return censored

    return censor_dict(event_dict)


def setup_logging() -> None:
    """
    Configure structured logging for the application.

    In development: Pretty console output with colors
    In production: JSON formatted logs for log aggregation
    """
    # Determine processors based on environment
    processors: list[Processor] = [
        structlog.contextvars.merge_contextvars,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        add_app_context,
        censor_sensitive_data,
    ]

    if settings.is_development:
        # Development: Pretty console output
        processors.extend([
            structlog.dev.ConsoleRenderer(
                colors=True,
                exception_formatter=structlog.dev.plain_traceback,
            )
        ])
    else:
        # Production: JSON output
        processors.extend([
            structlog.processors.format_exc_info,
            structlog.processors.JSONRenderer(),
        ])

    # Configure structlog
    structlog.configure(
        processors=processors,
        wrapper_class=structlog.make_filtering_bound_logger(
            logging.getLevelName(settings.log_level)
        ),
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )

    # Configure standard library logging
    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=logging.getLevelName(settings.log_level),
    )

    # Set log levels for noisy libraries
    logging.getLogger("uvicorn").setLevel(logging.INFO)
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)
    logging.getLogger("openai").setLevel(logging.INFO)
    logging.getLogger("twilio").setLevel(logging.INFO)


def get_logger(name: str) -> structlog.stdlib.BoundLogger:
    """
    Get a logger instance with the given name.

    Args:
        name: Logger name (usually __name__)

    Returns:
        Configured structlog logger
    """
    return structlog.get_logger(name)
