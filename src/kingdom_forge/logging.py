"""Logging configuration for the Kingdom Forge application."""

from __future__ import annotations

import logging


def configure_logging(level: str) -> None:
    """Configure the application logger with a consistent console format."""
    logging.basicConfig(
        level=getattr(logging, level),
        format="%(levelname)s %(name)s: %(message)s",
        force=True,
    )

