"""Unified logging configuration for HPE Networking MCP Server.

CRITICAL: MCP protocol requires stdout for JSON-RPC messages only.
All diagnostic logs MUST go to stderr to avoid protocol corruption.
"""

import contextlib
import sys

from loguru import logger

# Remove all default loguru handlers immediately
logger.remove()

# Noisy third-party libraries to suppress at DEBUG/INFO level
_NOISY_LIBS = frozenset(("httpx", "httpcore", "urllib3", "asyncio", "mistapi"))


def _log_filter(record: dict) -> bool:
    """Suppress DEBUG/INFO from noisy third-party libraries."""
    if any(record["name"].startswith(lib) for lib in _NOISY_LIBS):
        return record["level"].no >= 30  # WARNING and above only
    return True


def mask_secret(value: str) -> str:
    """Return a redacted version of a secret safe for logging."""
    if not value or len(value) < 8:
        return "***"
    return f"{value[:4]}...{value[-4:]}"


def setup_logging(level: str = "INFO", log_file: str | None = None) -> None:
    """Configure logging for the MCP server.

    Args:
        level: Log level (DEBUG, INFO, WARNING, ERROR)
        log_file: Optional path to write logs to a file with rotation
    """
    logger.remove()

    fmt = "{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}"

    logger.add(
        sys.stderr,
        level=level.upper(),
        format=fmt,
        colorize=False,
        filter=_log_filter,
    )

    if log_file:
        logger.add(
            log_file,
            rotation="10 MB",
            retention="7 days",
            level="DEBUG",
            format=fmt,
            filter=_log_filter,
        )


def flush_logs() -> None:
    """Flush all log handlers. Called during graceful shutdown."""
    with contextlib.suppress(Exception):
        logger.complete()
