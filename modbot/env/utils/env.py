"""Environment variable bootstrap helpers."""

from __future__ import annotations

from pathlib import Path

from dotenv import load_dotenv

_LOADED = False


def load_environment() -> None:
    """Load a repo-root `.env` file once without overriding real env vars."""

    global _LOADED
    if _LOADED:
        return

    repo_root = Path(__file__).resolve().parents[3]
    dotenv_path = repo_root / ".env"
    load_dotenv(dotenv_path=dotenv_path, override=False)
    _LOADED = True
