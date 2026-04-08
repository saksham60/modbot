"""Shared configuration, enum, policy, and scenario models."""

from enum import Enum

from pydantic import BaseModel, Field


class DifficultyLevel(str, Enum):
    """Supported task difficulty levels."""

    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"


class ActionType(str, Enum):
    """The full action space exposed to agents."""

    REVIEW_REPORT = "review_report"
    FETCH_USER_HISTORY = "fetch_user_history"
    FETCH_THREAD_CONTEXT = "fetch_thread_context"
    FETCH_POLICY = "fetch_policy"
    REMOVE_CONTENT = "remove_content"
    WARN_USER = "warn_user"
    ESCALATE_CASE = "escalate_case"
    IGNORE_REPORT = "ignore_report"
    COMPLETE_CASE = "complete_case"


class ReportStatus(str, Enum):
    """Lifecycle of a moderation case inside the simulator."""

    PENDING = "pending"
    IN_REVIEW = "in_review"
    DECISION_MADE = "decision_made"
    COMPLETED = "completed"


class SeverityLevel(str, Enum):
    """Hidden severity assigned to a report."""

    NONE = "none"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class PolicySnippetModel(BaseModel):
    """A policy snippet visible to the agent after lookup."""

    section: str
    title: str
    summary: str
    recommended_actions: list[str] = Field(default_factory=list)
    escalation_threshold: str = ""
    notes: str = ""


class UserHistoryModel(BaseModel):
    """User history revealed only after explicit fetch actions."""

    prior_warnings: int = 0
    prior_removals: int = 0
    recent_reports_against: int = 0
    account_age_days: int = 0
    trust_tier: str = "standard"
    note: str = ""


class ThreadContextModel(BaseModel):
    """Thread context revealed after fetching nearby conversation state."""

    thread_id: str
    summary: str
    neighboring_posts: list[str] = Field(default_factory=list)
    hostility_signal: float = Field(default=0.0, ge=0.0, le=1.0)
    irony_signal: float = Field(default=0.0, ge=0.0, le=1.0)
    brigading_signal: float = Field(default=0.0, ge=0.0, le=1.0)


class ReportVisibleModel(BaseModel):
    """Agent-visible report payload."""

    report_id: str
    content_id: str
    user_id: str
    thread_id: str
    author_handle: str
    content_text: str
    content_type: str
    report_reason: str
    reporter_count: int
    queue_priority: int
    created_at: str
    language: str = "en"
    visible_note: str = ""


class ReviewQueueItemModel(BaseModel):
    """Condensed report information shown in queue snapshots."""

    report_id: str
    author_handle: str
    report_reason: str
    reporter_count: int
    queue_priority: int
    status: ReportStatus


class ReportTruthModel(BaseModel):
    """Hidden truth labels used only by the simulator and graders."""

    gold_action: ActionType
    severity: SeverityLevel
    harmful: bool
    ambiguous: bool = False
    severe_violation: bool = False
    requires_user_history: bool = False
    requires_thread_context: bool = False
    requires_policy_lookup: bool = False
    likely_appeal_if_overenforced: float = Field(default=0.0, ge=0.0, le=1.0)
    likely_harm_if_ignored: float = Field(default=0.0, ge=0.0, le=1.0)
    brigading_target: bool = False
    false_report: bool = False
    recommended_notes: str = ""


class ReportScenarioModel(BaseModel):
    """A full scenario case containing visible and hidden fields."""

    report_id: str
    content_id: str
    user_id: str
    thread_id: str
    author_handle: str
    content_text: str
    content_type: str
    report_reason: str
    reporter_count: int
    queue_priority: int
    created_at: str
    language: str = "en"
    visible_note: str = ""
    available_user_history: UserHistoryModel
    available_thread_context: ThreadContextModel
    relevant_policy_section: str
    truth: ReportTruthModel

    def to_visible_report(self) -> ReportVisibleModel:
        """Return the agent-visible portion of the report."""

        return ReportVisibleModel(
            report_id=self.report_id,
            content_id=self.content_id,
            user_id=self.user_id,
            thread_id=self.thread_id,
            author_handle=self.author_handle,
            content_text=self.content_text,
            content_type=self.content_type,
            report_reason=self.report_reason,
            reporter_count=self.reporter_count,
            queue_priority=self.queue_priority,
            created_at=self.created_at,
            language=self.language,
            visible_note=self.visible_note,
        )

    def to_queue_item(self, status: ReportStatus) -> ReviewQueueItemModel:
        """Return a queue item representation for dashboard views."""

        return ReviewQueueItemModel(
            report_id=self.report_id,
            author_handle=self.author_handle,
            report_reason=self.report_reason,
            reporter_count=self.reporter_count,
            queue_priority=self.queue_priority,
            status=status,
        )


class TaskConfigModel(BaseModel):
    """Configuration for a task family."""

    task_id: str
    difficulty: DifficultyLevel
    display_name: str
    description: str
    max_steps: int = 30
    review_budget: int = 20
    initial_community_trust: float = 70.0
    initial_appeal_pressure: float = 5.0
    initial_backlog_pressure: float = 10.0
    grader_key: str


class TaskScenarioModel(BaseModel):
    """Concrete scenario loaded for an episode."""

    seed: int
    config: TaskConfigModel
    reports: list[ReportScenarioModel] = Field(default_factory=list)

    @property
    def task_id(self) -> str:
        return self.config.task_id

    @property
    def difficulty(self) -> DifficultyLevel:
        return self.config.difficulty

    def report_map(self) -> dict[str, ReportScenarioModel]:
        """Return reports keyed by report id."""

        return {report.report_id: report for report in self.reports}
