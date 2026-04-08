"""Pydantic request and response schemas for the API layer."""

from pydantic import BaseModel

from modbot.env.models.action import ActionModel
from modbot.env.models.info import StepInfoModel
from modbot.env.models.observation import ObservationModel
from modbot.env.models.state import EnvironmentStateModel


class SessionRequest(BaseModel):
    """Create or reset a session."""

    task_id: str = "easy"
    seed: int | None = None


class StepRequest(BaseModel):
    """Step the environment with a single action."""

    action: ActionModel


class SessionResponse(BaseModel):
    """Observation returned after creating or resetting a session."""

    session_id: str
    observation: ObservationModel


class StepResponse(BaseModel):
    """Response returned by the step endpoint."""

    session_id: str
    observation: ObservationModel
    reward: float
    done: bool
    info: StepInfoModel


class OpenEnvStepResponse(BaseModel):
    """Response returned by the OpenEnv-compatible step endpoint."""

    observation: ObservationModel
    reward: float
    done: bool
    info: StepInfoModel


class StateResponse(BaseModel):
    """Public state snapshot for a session."""

    session_id: str
    state: EnvironmentStateModel


class HealthResponse(BaseModel):
    """Service-level health payload."""

    status: str
    active_sessions: int
    supported_tasks: list[str]
