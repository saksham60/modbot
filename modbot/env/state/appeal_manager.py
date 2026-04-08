"""Appeal pressure and case-impact helpers."""

from modbot.env.models.config import ActionType, ReportTruthModel, SeverityLevel
from modbot.env.models.state import HiddenWorldStateModel
from modbot.env.state.trust_manager import clamp_metric


def apply_appeal_delta(state: HiddenWorldStateModel, appeal_delta: float = 0.0) -> float:
    """Apply an appeal delta and return the updated value."""

    state.appeal_pressure = clamp_metric(state.appeal_pressure + appeal_delta)
    return state.appeal_pressure


def apply_case_deltas(
    state: HiddenWorldStateModel,
    trust_delta: float = 0.0,
    appeal_delta: float = 0.0,
) -> None:
    """Apply trust and appeal changes while keeping both values bounded."""

    state.community_trust = clamp_metric(state.community_trust + trust_delta)
    state.appeal_pressure = clamp_metric(state.appeal_pressure + appeal_delta)


def resolve_case_impact(truth: ReportTruthModel, decision: ActionType) -> tuple[float, float]:
    """Return trust and appeal deltas from the finalized moderation decision."""

    if decision == truth.gold_action:
        trust_bonus = {
            SeverityLevel.NONE: 1.0,
            SeverityLevel.LOW: 1.5,
            SeverityLevel.MEDIUM: 2.0,
            SeverityLevel.HIGH: 3.0,
            SeverityLevel.CRITICAL: 4.5,
        }[truth.severity]
        if decision == ActionType.IGNORE_REPORT:
            return trust_bonus + 0.75, -1.0
        if decision == ActionType.ESCALATE_CASE:
            return trust_bonus + 1.0, -0.5
        return trust_bonus, -0.75

    if not truth.harmful and decision in {
        ActionType.REMOVE_CONTENT,
        ActionType.WARN_USER,
        ActionType.ESCALATE_CASE,
    }:
        return -2.5, 4.0 + (truth.likely_appeal_if_overenforced * 4.0)

    if truth.harmful and decision == ActionType.IGNORE_REPORT:
        return -(3.0 + truth.likely_harm_if_ignored * 5.0), 1.5

    if truth.harmful and decision == ActionType.WARN_USER and truth.gold_action == ActionType.REMOVE_CONTENT:
        return -1.5, 1.0

    if truth.harmful and decision == ActionType.REMOVE_CONTENT and truth.gold_action == ActionType.ESCALATE_CASE:
        return -1.0, 2.0

    return -0.75, 1.0
