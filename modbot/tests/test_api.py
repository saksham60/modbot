import pytest

pytest.importorskip("fastapi")

from fastapi.testclient import TestClient

from modbot.app.api.server import create_app


def test_api_health_and_step_flow() -> None:
    client = TestClient(create_app())

    health = client.get("/health")
    assert health.status_code == 200
    assert health.json()["status"] == "healthy"

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


def test_tasks_endpoint_exposes_graders() -> None:
    client = TestClient(create_app())

    response = client.get("/tasks")
    assert response.status_code == 200
    payload = response.json()

    tasks = payload["tasks"]
    assert payload["task_ids"] == ["easy", "medium", "hard"]
    assert len([task for task in tasks if task.get("grader")]) >= 3
    assert {task["id"] for task in tasks} == {"easy", "medium", "hard"}
    assert all(task["name"] for task in tasks)
    assert all(task["has_grader"] is True for task in tasks)
    assert set(payload["graders"]) == {"easy", "medium", "hard"}


def test_metadata_and_schema_endpoints_are_openenv_ready() -> None:
    client = TestClient(create_app())

    metadata = client.get("/metadata")
    assert metadata.status_code == 200
    metadata_payload = metadata.json()
    assert len([task for task in metadata_payload["tasks"] if task.get("grader")]) >= 3
    assert set(metadata_payload["graders"]) == {"easy", "medium", "hard"}

    schema = client.get("/schema")
    assert schema.status_code == 200
    schema_payload = schema.json()
    assert {"action", "observation", "state"}.issubset(schema_payload)


def test_grader_endpoint_scores_task_trajectory() -> None:
    client = TestClient(create_app())

    response = client.post("/grader", json={"task_id": "easy", "actions": [], "seed": 7})
    assert response.status_code == 200
    payload = response.json()
    assert 0.0 <= payload["score"] <= 1.0
    assert payload["result"]["task_id"] == "easy"
    assert payload["result"]["actions_evaluated"] == 0


def test_mcp_endpoint_is_json_rpc_reachable() -> None:
    client = TestClient(create_app())

    response = client.post("/mcp", json={"jsonrpc": "2.0", "id": 1, "method": "tools/list"})
    assert response.status_code == 200
    payload = response.json()
    assert payload["jsonrpc"] == "2.0"
    assert payload["id"] == 1
    assert payload["result"] == {"tools": []}


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

