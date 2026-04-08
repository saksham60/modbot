"""Environment API endpoints."""

from fastapi import APIRouter, Depends, HTTPException

from modbot.app.api.deps import get_session_store
from modbot.app.api.schemas import HealthResponse, SessionRequest, SessionResponse, StateResponse, StepRequest, StepResponse
from modbot.app.api.services.session_store import SessionStore

router = APIRouter(tags=["environment"])
SUPPORTED_TASKS = ["easy", "medium", "hard"]


@router.get("/health", response_model=HealthResponse)
def health(session_store: SessionStore = Depends(get_session_store)) -> HealthResponse:
    """Return a service health payload."""

    return HealthResponse(
        status="ok",
        active_sessions=session_store.active_session_count(),
        supported_tasks=SUPPORTED_TASKS,
    )


@router.get("/tasks")
def tasks() -> dict[str, list[str]]:
    """List task identifiers supported by the environment."""

    return {"tasks": SUPPORTED_TASKS}


@router.post("/sessions", response_model=SessionResponse)
def create_session(
    request: SessionRequest,
    session_store: SessionStore = Depends(get_session_store),
) -> SessionResponse:
    """Create a new environment session."""

    session_id, observation = session_store.create_session(task_id=request.task_id, seed=request.seed)
    return SessionResponse(session_id=session_id, observation=observation)


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

