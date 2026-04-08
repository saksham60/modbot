"""Launch the Gradio UI for local use or Hugging Face Spaces."""

from __future__ import annotations

import os

import gradio as gr

from modbot.app.api.server import create_app
from modbot.app.ui.pages.console_page import CUSTOM_CSS, UI_THEME, build_ui
from modbot.env.utils.env import load_environment

load_environment()

demo = build_ui()
app = gr.mount_gradio_app(
    create_app(),
    demo,
    path="/",
    css=CUSTOM_CSS,
    theme=UI_THEME,
    footer_links=[],
)


def launch() -> None:
    """Launch the combined API and UI application."""

    import uvicorn

    uvicorn.run(
        "modbot.app.ui.app:app",
        host=os.getenv("HOST", "0.0.0.0"),
        port=int(os.getenv("PORT", "7860")),
        reload=False,
    )


if __name__ == "__main__":
    launch()
