"""Metadata-only logging (T008, FR-030).

Requirement text MUST NEVER be logged. Helpers here emit only counts and smell-type
tallies. There is intentionally no function that accepts raw requirement text for logging.
"""

from __future__ import annotations

import logging

_LOGGER_NAME = "reqsmell"


def get_logger() -> logging.Logger:
    logger = logging.getLogger(_LOGGER_NAME)
    if not logger.handlers:
        handler = logging.StreamHandler()
        handler.setFormatter(logging.Formatter("%(name)s %(levelname)s %(message)s"))
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)
    return logger


def log_validation_metadata(*, language: str, finding_count: int, by_smell: dict[str, int]) -> None:
    """Log only metadata about a validation — never the requirement text."""
    get_logger().info(
        "validate language=%s findings=%d by_smell=%s",
        language,
        finding_count,
        {k: v for k, v in sorted(by_smell.items())},
    )
