"""Observation builder that hides truth fields from the agent."""

from modbot.env.models.config import ActionType
from modbot.env.models.observation import FetchedContextModel, ObservationModel, VisibleMetricsModel
from modbot.env.policy.retrieval import get_policy_snippet
from modbot.env.state.state_manager import get_active_report
from modbot.env.state.queue_manager import completed_case_count, pending_case_count, queue_snapshot
from modbot.env.utils.files import load_yaml_file, package_path


class ObservationBuilder:
    """Build agent-visible observations from hidden state."""

    def __init__(self) -> None:
        config = load_yaml_file(package_path("configs", "env.yaml"))
        self.max_visible_queue = int(config.get("max_visible_queue", 5))
        self.max_recent_actions = int(config.get("max_recent_actions", 6))

    def allowed_actions(self, state) -> list[ActionType]:
        """Return the action types available in the current state."""

        if state.done:
            return []
        if state.active_report_id is None:
            return [ActionType.REVIEW_REPORT] if state.remaining_review_budget > 0 and state.queue else []

        actions: list[ActionType] = []
        if state.remaining_review_budget > 0:
            actions.extend(
                [
                    ActionType.FETCH_USER_HISTORY,
                    ActionType.FETCH_THREAD_CONTEXT,
                    ActionType.FETCH_POLICY,
                ]
            )
        actions.extend(
            [
                ActionType.REMOVE_CONTENT,
                ActionType.WARN_USER,
                ActionType.ESCALATE_CASE,
                ActionType.IGNORE_REPORT,
            ]
        )
        runtime = state.runtime_reports[state.active_report_id]
        if runtime.decision is not None:
            actions.append(ActionType.COMPLETE_CASE)
        return actions

    def build(self, state) -> ObservationModel:
        """Build a safe observation for the agent."""

        active_report = get_active_report(state)
        fetched_context = FetchedContextModel()
        active_decision = None

        if active_report is not None:
            runtime = state.runtime_reports[active_report.report_id]
            active_decision = runtime.decision
            if runtime.fetched_context.user_history:
                fetched_context.user_history = active_report.available_user_history
            if runtime.fetched_context.thread_context:
                fetched_context.thread_context = active_report.available_thread_context
            for section in runtime.fetched_context.policy_sections:
                snippet = get_policy_snippet(section)
                if snippet is not None:
                    fetched_context.policy_snippets.append(snippet)

        recent_trajectory = [
            f"Step {entry.step}: {entry.action_type.value} ({entry.report_id or '-'}) -> {entry.message}"
            for entry in state.trajectory[-self.max_recent_actions :]
        ]

        metrics = VisibleMetricsModel(
            community_trust=state.community_trust,
            appeal_pressure=state.appeal_pressure,
            backlog_pressure=state.backlog_pressure,
            pending_reports=pending_case_count(state),
            completed_cases=completed_case_count(state),
            queue_depth=len(state.queue),
        )
        return ObservationModel(
            task_id=state.task.task_id,
            step=state.step_count,
            current_report=active_report.to_visible_report() if active_report else None,
            queue_snapshot=queue_snapshot(state, limit=self.max_visible_queue),
            allowed_actions=self.allowed_actions(state),
            fetched_context=fetched_context,
            remaining_review_budget=state.remaining_review_budget,
            visible_metrics=metrics,
            recent_trajectory=recent_trajectory,
            active_decision=active_decision,
        )

