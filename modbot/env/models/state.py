"""Hidden and visible state models for the environment."""

from pydantic import BaseModel, Field

from modbot.env.models.config import ActionType, DifficultyLevel, ReportStatus, TaskScenarioModel


class FetchedContextStateModel(BaseModel):
    """Internal fetch flags for a report case."""

    user_history: bool = False
    thread_context: bool = False
    policy_sections: list[str] = Field(default_factory=list)


class ReportRuntimeStateModel(BaseModel):
    """Mutable per-report execution state."""

    report_id: str
    status: ReportStatus = ReportStatus.PENDING
    reviewed: bool = False
    decision: ActionType | None = None
    fetched_context: FetchedContextStateModel = Field(default_factory=FetchedContextStateModel)
    notes: list[str] = Field(default_factory=list)
    invalid_attempts: int = 0
    redundant_actions: int = 0
    completed: bool = False


class TrajectoryEntryModel(BaseModel):
    """A compact action log entry for episode traces."""

    step: int
    action_type: ActionType
    report_id: str | None = None
    reward: float = 0.0
    message: str = ""


class HiddenWorldStateModel(BaseModel):
    """Full hidden environment state used internally by the simulator."""

    task: TaskScenarioModel
    step_count: int = 0
    remaining_review_budget: int
    community_trust: float
    appeal_pressure: float
    backlog_pressure: float
    active_report_id: str | None = None
    queue: list[str] = Field(default_factory=list)
    runtime_reports: dict[str, ReportRuntimeStateModel] = Field(default_factory=dict)
    total_reward: float = 0.0
    done: bool = False
    done_reason: str | None = None
    trajectory: list[TrajectoryEntryModel] = Field(default_factory=list)
    reward_history: list[dict[str, float]] = Field(default_factory=list)
    final_score: float | None = None
    grader_components: dict[str, float] = Field(default_factory=dict)


class ReportCaseStateModel(BaseModel):
    """Sanitized public state for each report case."""

    report_id: str
    user_id: str
    queue_priority: int
    status: ReportStatus
    decision: ActionType | None = None
    fetched_context: FetchedContextStateModel
    redundant_actions: int = 0
    invalid_attempts: int = 0


class EnvironmentStateModel(BaseModel):
    """Public environment state returned by `state()`."""

    task_id: str
    difficulty: DifficultyLevel
    step_count: int
    active_report_id: str | None = None
    remaining_review_budget: int
    community_trust: float
    appeal_pressure: float
    backlog_pressure: float
    queue: list[str] = Field(default_factory=list)
    reports: list[ReportCaseStateModel] = Field(default_factory=list)
    total_reward: float = 0.0
    done: bool = False
    done_reason: str | None = None
    trajectory: list[TrajectoryEntryModel] = Field(default_factory=list)
    final_score: float | None = None
    grader_components: dict[str, float] = Field(default_factory=dict)
