"""Seed helpers for deterministic task loading."""

from random import Random


def normalize_seed(seed: int | None) -> int:
    """Return a stable integer seed for the environment."""

    if seed is None:
        return 7
    return int(seed)


def seeded_random(seed: int | None) -> Random:
    """Return a local random generator without touching global state."""

    return Random(normalize_seed(seed))
