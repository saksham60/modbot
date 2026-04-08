"""Deployment entrypoint expected by multi-mode validators."""

from __future__ import annotations

from modbot.app.ui.app import app as app
from modbot.app.ui.app import launch


def main() -> None:
    """Run the combined API and UI server."""

    launch()
