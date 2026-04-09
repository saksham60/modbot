"""Environment API endpoints."""

from typing import Any

from fastapi import APIRouter, Body, Depends, HTTPException
from pydantic import ValidationError

from modbot.app.api.deps import get_session_store
from modbot.app.api.schemas import (
    HealthResponse,
    MetadataResponse,
    OpenEnvStepResponse,
    SchemaResponse,
    SessionRequest,
    SessionResponse,
    StateResponse,
    StepRequest,
    StepResponse,
)
from modbot.env.models.action import ActionModel
from modbot.env.models.observation import ObservationModel
from modbot.env.models.state import EnvironmentStateModel
from modbot.app.api.services.session_store import SessionStore

router = APIRouter(tags=["environment"])
TASKS_WITH_GRADERS = [
    {
        "id": "easy",
        "title": "Clear-Cut Moderation",
        "description": "Clear-cut harmful and benign moderation cases.",
        "difficulty": "easy",
        "data_glob": "modbot/data/easy/*.json",
        "grader": "modbot.env.grader.easy_grader:EasyTaskGrader",
        "grader_key": "easy",
    },
    {
        "id": "medium",
        "title": "Contextual Moderation",
        "description": "Context-dependent moderation with ambiguity and sarcasm.",
        "difficulty": "medium",
        "data_glob": "modbot/data/medium/*.json",
        "grader": "modbot.env.grader.medium_grader:MediumTaskGrader",
        "grader_key": "medium",
    },
    {
        "id": "hard",
        "title": "Brigading Surge",
        "description": "Brigading surge with false reports, real harm, and tight review budget.",
        "difficulty": "hard",
        "data_glob": "modbot/data/hard/*.json",
        "grader": "modbot.env.grader.hard_grader:HardTaskGrader",
        "grader_key": "hard",
    },
]
SUPPORTED_TASKS = [task["id"] for task in TASKS_WITH_GRADERS]
OPENENV_SESSION_ID = "__openenv__"


@router.get("/health", response_model=HealthResponse)
def health(session_store: SessionStore = Depends(get_session_store)) -> HealthResponse:
    """Return a service health payload."""

    return HealthResponse(
        status="healthy",
        active_sessions=session_store.active_session_count(),
        supported_tasks=SUPPORTED_TASKS,
    )


@router.get("/metadata", response_model=MetadataResponse)
def metadata() -> MetadataResponse:
    """Return OpenEnv metadata including task grader declarations."""

    return MetadataResponse(
        name="modbot",
        title="ModBot - Trust & Safety Policy Simulator",
        description=(
            "A stateful moderation operations environment with sequential actions, "
            "hidden world state, dense reward shaping, and deterministic final grading."
        ),
        tasks=TASKS_WITH_GRADERS,
    )


@router.get("/schema", response_model=SchemaResponse)
def schema() -> SchemaResponse:
    """Return the public action, observation, and state schemas."""

    return SchemaResponse(
        action=ActionModel.model_json_schema(),
        observation=ObservationModel.model_json_schema(),
        state=EnvironmentStateModel.model_json_schema(),
    )


@router.post("/mcp")
def mcp(request: dict[str, Any] | None = Body(default=None)) -> dict[str, Any]:
    """Return a minimal JSON-RPC MCP payload for OpenEnv smoke validation."""

    request = request or {}
    rpc_id = request.get("id")
    method = request.get("method")

    if method == "initialize":
        result: dict[str, Any] = {
            "protocolVersion": "2024-11-05",
            "capabilities": {"tools": {}},
            "serverInfo": {"name": "modbot", "version": "0.1.0"},
        }
    elif method == "tools/list":
        result = {"tools": []}
    else:
        result = {}

    response: dict[str, Any] = {"jsonrpc": "2.0", "result": result}
    if rpc_id is not None:
        response["id"] = rpc_id
    return response


@router.get("/tasks")
def tasks() -> dict[str, list[Any]]:
    """List task identifiers and validator-facing grader metadata."""

    return {"tasks": TASKS_WITH_GRADERS, "task_ids": SUPPORTED_TASKS}


@router.post("/sessions", response_model=SessionResponse)
def create_session(
    request: SessionRequest,
    session_store: SessionStore = Depends(get_session_store),
) -> SessionResponse:
    """Create a new environment session."""

    session_id, observation = session_store.create_session(task_id=request.task_id, seed=request.seed)
    return SessionResponse(session_id=session_id, observation=observation)


@router.post("/reset", response_model=ObservationModel)
def openenv_reset(
    request: SessionRequest | None = Body(default=None),
    session_store: SessionStore = Depends(get_session_store),
) -> ObservationModel:
    """Reset the default OpenEnv session and return the initial observation."""

    request = request or SessionRequest()
    return session_store.create_or_reset_named_session(
        OPENENV_SESSION_ID,
        task_id=request.task_id,
        seed=request.seed,
    )


@router.post("/sessions/{session_id}/reset", response_model=SessionResponse)
def reset_session(
    session_id: str,
    request: SessionRequest,
    session_store: SessionStore = Depends(get_session_store),
) -> SessionResponse:
    """Reset an existing session."""

    try:
        observation = session_store.reset_session(session_id, task_id=request.task_id, seed=request.seed)
    except KeyError as error:
        raise HTTPException(status_code=404, detail="Unknown session id") from error
    return SessionResponse(session_id=session_id, observation=observation)


@router.post("/step", response_model=OpenEnvStepResponse)
def openenv_step(
    request: dict[str, Any] = Body(...),
    session_store: SessionStore = Depends(get_session_store),
) -> OpenEnvStepResponse:
    """Step the default OpenEnv session with either wrapped or direct action payloads."""

    if not session_store.has_session(OPENENV_SESSION_ID):
        session_store.create_or_reset_named_session(OPENENV_SESSION_ID)

    try:
        action_payload = request.get("action", request)
        action = ActionModel.model_validate(action_payload)
    except ValidationError as error:
        raise HTTPException(status_code=422, detail=error.errors()) from error

    observation, reward, done, info = session_store.step_session(OPENENV_SESSION_ID, action)
    return OpenEnvStepResponse(
        observation=observation,
        reward=reward,
        done=done,
        info=info,
    )


@router.post("/sessions/{session_id}/step", response_model=StepResponse)
def step_session(
    session_id: str,
    request: StepRequest,
    session_store: SessionStore = Depends(get_session_store),
) -> StepResponse:
    """Apply an action to an existing session."""

    try:
        observation, reward, done, info = session_store.step_session(session_id, request.action)
    except KeyError as error:
        raise HTTPException(status_code=404, detail="Unknown session id") from error
    return StepResponse(
        session_id=session_id,
        observation=observation,
        reward=reward,
        done=done,
        info=info,
    )


@router.get("/state", response_model=EnvironmentStateModel)
def openenv_state(
    session_store: SessionStore = Depends(get_session_store),
) -> EnvironmentStateModel:
    """Return the public state for the default OpenEnv session."""

    if not session_store.has_session(OPENENV_SESSION_ID):
        session_store.create_or_reset_named_session(OPENENV_SESSION_ID)
    return session_store.state(OPENENV_SESSION_ID)


@router.get("/sessions/{session_id}/state", response_model=StateResponse)
def state_session(
    session_id: str,
    session_store: SessionStore = Depends(get_session_store),
) -> StateResponse:
    """Return a public state snapshot for a session."""

    try:
        state = session_store.state(session_id)
    except KeyError as error:
        raise HTTPException(status_code=404, detail="Unknown session id") from error
    return StateResponse(session_id=session_id, state=state)

