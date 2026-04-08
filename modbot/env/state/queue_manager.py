"""Queue management helpers for the moderation simulator."""

from modbot.env.models.config import ReportStatus
from modbot.env.models.config import ReviewQueueItemModel
from modbot.env.models.state import HiddenWorldStateModel
from modbot.env.state.state_manager import get_report


def pending_case_ids(state: HiddenWorldStateModel) -> list[str]:
    """Return unresolved report ids in queue order."""

    return [report_id for report_id in state.queue if not state.runtime_reports[report_id].completed]


def pending_case_count(state: HiddenWorldStateModel) -> int:
    """Return unresolved case count."""

    return len(pending_case_ids(state))


def completed_case_count(state: HiddenWorldStateModel) -> int:
    """Return count of completed cases."""

    return sum(1 for runtime in state.runtime_reports.values() if runtime.completed)


def activate_report(state: HiddenWorldStateModel, report_id: str) -> None:
    """Mark a report as currently under review."""

    runtime = state.runtime_reports[report_id]
    runtime.reviewed = True
    runtime.status = ReportStatus.IN_REVIEW
    state.active_report_id = report_id


def set_decision(state: HiddenWorldStateModel, report_id: str, decision) -> None:
    """Store the current draft moderation decision for an active case."""

    runtime = state.runtime_reports[report_id]
    runtime.decision = decision
    runtime.status = ReportStatus.DECISION_MADE


def complete_report(state: HiddenWorldStateModel, report_id: str) -> None:
    """Mark a case complete and remove it from the actionable queue."""

    runtime = state.runtime_reports[report_id]
    runtime.completed = True
    runtime.status = ReportStatus.COMPLETED
    if report_id in state.queue:
        state.queue.remove(report_id)
    if state.active_report_id == report_id:
        state.active_report_id = None


def queue_snapshot(state: HiddenWorldStateModel, limit: int = 5) -> list[ReviewQueueItemModel]:
    """Return a small queue snapshot for observations."""

    items: list[ReviewQueueItemModel] = []
    for report_id in pending_case_ids(state)[:limit]:
        report = get_report(state, report_id)
        runtime = state.runtime_reports[report_id]
        items.append(report.to_queue_item(runtime.status))
    return items

