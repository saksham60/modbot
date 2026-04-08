"""FastAPI server bootstrap for ModBot."""

from __future__ import annotations

import os

from fastapi import FastAPI

from modbot.app.api.routes.environment import router as environment_router


def create_app() -> FastAPI:
    """Create the FastAPI application."""

    app = FastAPI(
        title="ModBot API",
        description="API surface for the ModBot trust and safety simulator.",
        version="0.1.0",
    )
    app.include_router(environment_router)
    return app


app = create_app()


def run() -> None:
    """Run the API with uvicorn."""

    import uvicorn

    uvicorn.run(
        "modbot.app.api.server:app",
        host=os.getenv("HOST", "0.0.0.0"),
        port=int(os.getenv("PORT", "8000")),
        reload=False,
    )


if __name__ == "__main__":
    run()

