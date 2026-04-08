"""Shared deterministic grading metrics."""

from modbot.env.models.config import ActionType
from modbot.env.models.state import HiddenWorldStateModel
from modbot.env.state.queue_manager import completed_case_count


def _completed_reports(state: HiddenWorldStateModel):
    for report in state.task.reports:
        runtime = state.runtime_reports[report.report_id]
        if runtime.completed and runtime.decision is not None:
            yield report, runtime


def action_accuracy(state: HiddenWorldStateModel) -> float:
    """Fraction of reports with an exact final action match."""

    total = len(state.task.reports)
    if total == 0:
        return 1.0
    correct = sum(
        1
        for report, runtime in _completed_reports(state)
        if runtime.decision == report.truth.gold_action
    )
    return round(correct / total, 4)


def severe_violation_recall(state: HiddenWorldStateModel) -> float:
    """Recall for severe cases that require the correct response."""

    severe_reports = [report for report in state.task.reports if report.truth.severe_violation]
    if not severe_reports:
        return 1.0
    recovered = sum(
        1
        for report in severe_reports
        if state.runtime_reports[report.report_id].completed
        and state.runtime_reports[report.report_id].decision == report.truth.gold_action
    )
    return round(recovered / len(severe_reports), 4)


def removal_precision(state: HiddenWorldStateModel) -> float:
    """Precision of content removal decisions."""

    removals = [
        report
        for report, runtime in _completed_reports(state)
        if runtime.decision == ActionType.REMOVE_CONTENT
    ]
    if not removals:
        required_removals = sum(
            1 for report in state.task.reports if report.truth.gold_action == ActionType.REMOVE_CONTENT
        )
        return 1.0 if required_removals == 0 else 0.0
    correct = sum(1 for report in removals if report.truth.gold_action == ActionType.REMOVE_CONTENT)
    return round(correct / len(removals), 4)


def context_discipline(state: HiddenWorldStateModel) -> float:
    """Measure whether ambiguous cases received required context fetches."""

    ambiguous_reports = [report for report in state.task.reports if report.truth.ambiguous]
    if not ambiguous_reports:
        return 1.0

    satisfied = 0
    for report in ambiguous_reports:
        runtime = state.runtime_reports[report.report_id]
        context_ok = True
        if report.truth.requires_user_history:
            context_ok = context_ok and runtime.fetched_context.user_history
        if report.truth.requires_thread_context:
            context_ok = context_ok and runtime.fetched_context.thread_context
        if report.truth.requires_policy_lookup:
            context_ok = context_ok and report.relevant_policy_section in runtime.fetched_context.policy_sections
        if context_ok and runtime.completed:
            satisfied += 1
    return round(satisfied / len(ambiguous_reports), 4)


def queue_efficiency(state: HiddenWorldStateModel) -> float:
    """Fraction of the queue resolved by the end of the episode."""

    total = len(state.task.reports)
    if total == 0:
        return 1.0
    return round(completed_case_count(state) / total, 4)


def final_trust_score(state: HiddenWorldStateModel) -> float:
    """Normalize final community trust to [0.0, 1.0]."""

    return round(state.community_trust / 100.0, 4)


def appeal_control(state: HiddenWorldStateModel) -> float:
    """Lower appeal pressure is better."""

    return round(1.0 - (state.appeal_pressure / 100.0), 4)


def backlog_control(state: HiddenWorldStateModel) -> float:
    """Lower backlog pressure is better."""

    return round(1.0 - (state.backlog_pressure / 100.0), 4)

