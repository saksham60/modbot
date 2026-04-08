"""Dependency helpers for the API layer."""

from modbot.app.api.services.session_store import SessionStore

SESSION_STORE = SessionStore()


def get_session_store() -> SessionStore:
    """Return the shared in-memory session store."""

    return SESSION_STORE
