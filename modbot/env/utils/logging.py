"""Lightweight logging helpers."""

import logging


def get_logger(name: str) -> logging.Logger:
    """Return a module logger configured for local use."""

    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")
    return logging.getLogger(name)
