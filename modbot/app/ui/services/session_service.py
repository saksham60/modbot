"""UI state handlers for the Gradio moderation console."""

from __future__ import annotations

from modbot.app.api.deps import get_session_store
from modbot.app.ui.components.formatters import (
    queue_rows,
    render_context_panel,
    render_metrics_strip,
    render_report_panel,
    render_status_panel,
    render_summary,
    trajectory_rows,
)
from modbot.env.models.action import ActionModel
from modbot.clients.llm_client import choose_action

SESSION_STORE = get_session_store()


def _normalize_text(value: str | None) -> str | None:
    if value is None:
        return None
    value = value.strip()
    return value or None


def _render(session_id: str, last_message: str = ""):
    observation = SESSION_STORE.observation(session_id)
    state = SESSION_STORE.state(session_id)
    return (
        session_id,
        render_metrics_strip(observation, state),
        queue_rows(observation),
        render_report_panel(observation),
        render_context_panel(observation),
        render_status_panel(observation, last_message),
        trajectory_rows(state),
        render_summary(state),
    )


def ensure_session(task_id: str, seed: int, session_id: str | None):
    """Create or reset a session and return UI render values."""

    if session_id and SESSION_STORE.has_session(session_id):
        SESSION_STORE.reset_session(session_id, task_id=task_id, seed=int(seed))
        return _render(session_id, last_message=f"Session reset for task '{task_id}' with seed {int(seed)}.")

    session_id, _ = SESSION_STORE.create_session(task_id=task_id, seed=int(seed))
    return _render(session_id, last_message=f"Created session for task '{task_id}' with seed {int(seed)}.")


def step_session(
    session_id: str | None,
    task_id: str,
    seed: int,
    action_type: str,
    report_id: str,
    user_id: str,
    policy_section: str,
    notes: str,
):
    """Apply a manually selected action from the UI."""

    if not session_id or not SESSION_STORE.has_session(session_id):
        session_id, _ = SESSION_STORE.create_session(task_id=task_id, seed=int(seed))

    payload = {
        "action_type": action_type,
        "report_id": _normalize_text(report_id),
        "user_id": _normalize_text(user_id),
        "policy_section": _normalize_text(policy_section),
        "notes": _normalize_text(notes),
    }
    payload = {key: value for key, value in payload.items() if value is not None}
    action = ActionModel.model_validate(payload)
    _, reward, _, info = SESSION_STORE.step_session(session_id, action)
    return _render(session_id, last_message=f"{info.message} Reward {reward:.2f}.")


def auto_run_session(session_id: str | None, task_id: str, seed: int):
    """Run the heuristic baseline until the episode completes or stalls."""

    if not session_id or not SESSION_STORE.has_session(session_id):
        session_id, _ = SESSION_STORE.create_session(task_id=task_id, seed=int(seed))

    latest_message = "Auto-run complete."
    for _ in range(64):
        observation = SESSION_STORE.observation(session_id)
        state = SESSION_STORE.state(session_id)
        if state.done:
            break
        action = choose_action(observation)
        _, reward, _, info = SESSION_STORE.step_session(session_id, action)
        latest_message = f"Auto-run used {action.action_type.value}. Reward {reward:.2f}. {info.message}"
        if info.done_reason:
            break
    return _render(session_id, last_message=latest_message)

