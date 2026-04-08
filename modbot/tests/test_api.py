import pytest

pytest.importorskip("fastapi")

from fastapi.testclient import TestClient

from modbot.app.api.server import create_app


def test_api_health_and_step_flow() -> None:
    client = TestClient(create_app())

    health = client.get("/health")
    assert health.status_code == 200
    assert health.json()["status"] == "ok"

    created = client.post("/sessions", json={"task_id": "easy", "seed": 7})
    assert created.status_code == 200
    payload = created.json()
    session_id = payload["session_id"]
    first_report = payload["observation"]["queue_snapshot"][0]["report_id"]

    stepped = client.post(
        f"/sessions/{session_id}/step",
        json={"action": {"action_type": "review_report", "report_id": first_report}},
    )
    assert stepped.status_code == 200
    assert stepped.json()["info"]["valid_action"] is True


def test_openenv_root_reset_step_and_state() -> None:
    client = TestClient(create_app())

    reset = client.post("/reset", json={"task_id": "easy", "seed": 7})
    assert reset.status_code == 200
    observation = reset.json()
    assert observation["task_id"] == "easy"
    assert observation["queue_snapshot"]

    first_report = observation["queue_snapshot"][0]["report_id"]
    step = client.post("/step", json={"action_type": "review_report", "report_id": first_report})
    assert step.status_code == 200
    assert step.json()["info"]["valid_action"] is True

    state = client.get("/state")
    assert state.status_code == 200
    assert state.json()["active_report_id"] == first_report


def test_build_ui_returns_blocks() -> None:
    pytest.importorskip("gradio", reason="UI smoke requires gradio")
    from modbot.app.ui.pages.console_page import build_ui

    demo = build_ui()
    assert demo is not None

