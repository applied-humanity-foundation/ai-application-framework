"""Logging utilities for the AHF AI Application Framework.

Provides structured JSON logging for production environments and
human-readable formatting for development, with automatic API key redaction.
"""

from __future__ import annotations

import json
import logging
import re
import time
from typing import Any


_REDACT_PATTERN = re.compile(r"(sk-[A-Za-z0-9]{4})[A-Za-z0-9]{20,}")


def _redact_secrets(text: str) -> str:
    """Replace API keys in text with a redacted version, keeping the first 7 chars."""
    return _REDACT_PATTERN.sub(r"\1***REDACTED***", text)


class StructuredFormatter(logging.Formatter):
    """Emit log records as single-line JSON objects."""

    def format(self, record: logging.LogRecord) -> str:
        entry: dict[str, Any] = {
            "ts": self.formatTime(record, self.datefmt),
            "level": record.levelname,
            "logger": record.name,
            "msg": _redact_secrets(record.getMessage()),
        }
        if hasattr(record, "duration_ms"):
            entry["duration_ms"] = record.duration_ms  # type: ignore[attr-defined]
        if hasattr(record, "tokens"):
            entry["tokens"] = record.tokens  # type: ignore[attr-defined]
        if record.exc_info and record.exc_info[1] is not None:
            entry["exception"] = self.formatException(record.exc_info)
        return json.dumps(entry, default=str)


def setup_logging(
    level: str = "INFO",
    format: str = "structured",  # noqa: A002 — shadows built-in intentionally
) -> logging.Logger:
    """Configure and return the library root logger.

    Args:
        level: Log level name (DEBUG, INFO, WARNING, ERROR, CRITICAL).
        format: Either ``"structured"`` for JSON output or ``"simple"`` for
            human-readable lines.

    Returns:
        The configured ``ahf_ai`` root logger.
    """
    logger = logging.getLogger("ahf_ai")
    logger.setLevel(getattr(logging, level.upper(), logging.INFO))

    if not logger.handlers:
        handler = logging.StreamHandler()
        if format == "structured":
            handler.setFormatter(StructuredFormatter())
        else:
            handler.setFormatter(
                logging.Formatter("%(asctime)s [%(levelname)s] %(name)s: %(message)s")
            )
        logger.addHandler(handler)

    return logger


def log_request(
    logger: logging.Logger,
    endpoint: str,
    duration_ms: float,
    tokens: int | None = None,
) -> None:
    """Log an API request with timing and optional token count."""
    extra = {"duration_ms": round(duration_ms, 2)}
    if tokens is not None:
        extra["tokens"] = tokens
    logger.info(
        "API request to %s completed in %.1fms", endpoint, duration_ms, extra=extra
    )


class Timer:
    """Simple context-manager timer that records elapsed milliseconds."""

    def __init__(self) -> None:
        self.start: float = 0.0
        self.elapsed_ms: float = 0.0

    def __enter__(self) -> "Timer":
        self.start = time.perf_counter()
        return self

    def __exit__(self, *_: Any) -> None:
        self.elapsed_ms = (time.perf_counter() - self.start) * 1000
