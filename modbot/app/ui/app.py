"""Launch the Gradio UI for local use or Hugging Face Spaces."""

from __future__ import annotations

import os

from modbot.app.ui.pages.console_page import build_ui
from modbot.env.utils.env import load_environment

load_environment()

demo = build_ui()


def launch() -> None:
    """Launch the Gradio UI."""

    demo.launch(
        server_name=os.getenv("HOST", "0.0.0.0"),
        server_port=int(os.getenv("PORT", "7860")),
        show_api=False,
    )


if __name__ == "__main__":
    launch()
