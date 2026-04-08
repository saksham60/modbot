"""Hidden state initialization and public state projection."""

from modbot.env.models.state import EnvironmentStateModel, HiddenWorldStateModel, ReportCaseStateModel, ReportRuntimeStateModel
from modbot.env.models.config import TaskScenarioModel


def initialize_hidden_state(task: TaskScenarioModel) -> HiddenWorldStateModel:
    """Build initial hidden state for a task scenario."""

    runtime_reports = {
        report.report_id: ReportRuntimeStateModel(report_id=report.report_id)
        for report in task.reports
    }
    return HiddenWorldStateModel(
        task=task,
        remaining_review_budget=task.config.review_budget,
        community_trust=task.config.initial_community_trust,
        appeal_pressure=task.config.initial_appeal_pressure,
        backlog_pressure=task.config.initial_backlog_pressure,
        queue=[report.report_id for report in task.reports],
        runtime_reports=runtime_reports,
    )


def get_report(state: HiddenWorldStateModel, report_id: str):
    """Return a scenario report by id."""

    return state.task.report_map().get(report_id)


def get_active_report(state: HiddenWorldStateModel):
    """Return the currently active report scenario, if any."""

    if not state.active_report_id:
        return None
    return get_report(state, state.active_report_id)


def build_public_state(state: HiddenWorldStateModel) -> EnvironmentStateModel:
    """Project the hidden world state into a safe public debug state."""

    reports = []
    for report in state.task.reports:
        runtime = state.runtime_reports[report.report_id]
        reports.append(
            ReportCaseStateModel(
                report_id=report.report_id,
                user_id=report.user_id,
                queue_priority=report.queue_priority,
                status=runtime.status,
                decision=runtime.decision,
                fetched_context=runtime.fetched_context,
                redundant_actions=runtime.redundant_actions,
                invalid_attempts=runtime.invalid_attempts,
            )
        )
    return EnvironmentStateModel(
        task_id=state.task.task_id,
        difficulty=state.task.difficulty,
        step_count=state.step_count,
        active_report_id=state.active_report_id,
        remaining_review_budget=state.remaining_review_budget,
        community_trust=state.community_trust,
        appeal_pressure=state.appeal_pressure,
        backlog_pressure=state.backlog_pressure,
        queue=list(state.queue),
        reports=reports,
        total_reward=state.total_reward,
        done=state.done,
        done_reason=state.done_reason,
        trajectory=list(state.trajectory),
        final_score=state.final_score,
        grader_components=dict(state.grader_components),
    )

