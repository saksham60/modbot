"""Trust and backlog metric helpers."""

from modbot.env.models.config import DifficultyLevel
from modbot.env.models.state import HiddenWorldStateModel
from modbot.env.state.queue_manager import pending_case_count


def clamp_metric(value: float, lower: float = 0.0, upper: float = 100.0) -> float:
    """Clamp a metric to a bounded range."""

    return max(lower, min(upper, round(value, 2)))


def recompute_backlog_pressure(state: HiddenWorldStateModel) -> float:
    """Update backlog pressure using queue depth, active case count, and budget burn."""

    pending = pending_case_count(state)
    total_budget = max(state.task.config.review_budget, 1)
    budget_burn = 1.0 - (state.remaining_review_budget / total_budget)
    difficulty_scale = {
        DifficultyLevel.EASY: 0.75,
        DifficultyLevel.MEDIUM: 0.95,
        DifficultyLevel.HARD: 1.2,
    }[state.task.difficulty]
    active_penalty = 2.0 if state.active_report_id else 0.0
    backlog = (
        state.task.config.initial_backlog_pressure
        + max(pending - 1, 0) * 3.0 * difficulty_scale
        + budget_burn * 18.0
        + active_penalty
    )
    state.backlog_pressure = clamp_metric(backlog)
    return state.backlog_pressure


def apply_trust_delta(state: HiddenWorldStateModel, trust_delta: float = 0.0) -> float:
    """Apply a trust delta and return the updated value."""

    state.community_trust = clamp_metric(state.community_trust + trust_delta)
    return state.community_trust
