"""Observation models exposed to the agent at each step."""

from pydantic import BaseModel, Field

from modbot.env.models.config import (
    ActionType,
    PolicySnippetModel,
    ReportVisibleModel,
    ReviewQueueItemModel,
    ThreadContextModel,
    UserHistoryModel,
)


class FetchedContextModel(BaseModel):
    """Context visible after explicit fetch actions."""

    user_history: UserHistoryModel | None = None
    thread_context: ThreadContextModel | None = None
    policy_snippets: list[PolicySnippetModel] = Field(default_factory=list)


class VisibleMetricsModel(BaseModel):
    """High-level platform metrics visible to the agent."""

    community_trust: float
    appeal_pressure: float
    backlog_pressure: float
    pending_reports: int
    completed_cases: int
    queue_depth: int


class ObservationModel(BaseModel):
    """Agent observation returned by reset and step."""

    task_id: str
    step: int
    current_report: ReportVisibleModel | None = None
    queue_snapshot: list[ReviewQueueItemModel] = Field(default_factory=list)
    allowed_actions: list[ActionType] = Field(default_factory=list)
    fetched_context: FetchedContextModel = Field(default_factory=FetchedContextModel)
    remaining_review_budget: int
    visible_metrics: VisibleMetricsModel
    recent_trajectory: list[str] = Field(default_factory=list)
    active_decision: ActionType | None = None
