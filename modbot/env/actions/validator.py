"""Action validation for the sequential moderation environment."""

from dataclasses import dataclass

from modbot.env.models.action import ActionModel
from modbot.env.models.config import ActionType
from modbot.env.models.state import HiddenWorldStateModel
from modbot.env.policy.retrieval import is_known_policy_section
from modbot.env.state.state_manager import get_active_report, get_report

INSPECTION_ACTIONS = {
    ActionType.REVIEW_REPORT,
    ActionType.FETCH_USER_HISTORY,
    ActionType.FETCH_THREAD_CONTEXT,
    ActionType.FETCH_POLICY,
}
MODERATION_ACTIONS = {
    ActionType.REMOVE_CONTENT,
    ActionType.WARN_USER,
    ActionType.ESCALATE_CASE,
    ActionType.IGNORE_REPORT,
}


@dataclass(slots=True)
class ActionValidationResult:
    """Validation outcome for a proposed agent action."""

    is_valid: bool
    message: str
    redundant: bool = False


def action_budget_cost(action_type: ActionType) -> int:
    """Return the review budget cost of an action."""

    return 1 if action_type in INSPECTION_ACTIONS else 0


def validate_action(state: HiddenWorldStateModel, action: ActionModel) -> ActionValidationResult:
    """Validate an action against the current hidden state."""

    if state.done:
        return ActionValidationResult(False, "Episode is already complete.")

    if action_budget_cost(action.action_type) > state.remaining_review_budget:
        return ActionValidationResult(False, "Review budget exhausted for inspection actions.")

    active_report = get_active_report(state)

    if action.action_type == ActionType.REVIEW_REPORT:
        report = get_report(state, action.report_id or "")
        if report is None:
            return ActionValidationResult(False, f"Unknown report id: {action.report_id}")
        runtime = state.runtime_reports[action.report_id]
        if runtime.completed:
            return ActionValidationResult(False, "That case is already completed.")
        if state.active_report_id and state.active_report_id != action.report_id:
            return ActionValidationResult(False, "Complete the active case before reviewing another report.")
        if state.active_report_id == action.report_id:
            return ActionValidationResult(True, "Report is already active.", redundant=True)
        return ActionValidationResult(True, "Report moved into active review.")

    if active_report is None:
        return ActionValidationResult(False, "Review a report before fetching context or taking action.")

    runtime = state.runtime_reports[active_report.report_id]
    if action.report_id and action.action_type != ActionType.FETCH_USER_HISTORY and action.report_id != active_report.report_id:
        return ActionValidationResult(False, "Actions must target the active report.")

    if action.action_type == ActionType.FETCH_USER_HISTORY:
        if action.user_id != active_report.user_id:
            return ActionValidationResult(False, "User history fetch must target the active report author.")
        return ActionValidationResult(
            True,
            "Fetched user history." if not runtime.fetched_context.user_history else "User history already fetched.",
            redundant=runtime.fetched_context.user_history,
        )

    if action.action_type == ActionType.FETCH_THREAD_CONTEXT:
        return ActionValidationResult(
            True,
            "Fetched thread context." if not runtime.fetched_context.thread_context else "Thread context already fetched.",
            redundant=runtime.fetched_context.thread_context,
        )

    if action.action_type == ActionType.FETCH_POLICY:
        if not is_known_policy_section(action.policy_section or ""):
            return ActionValidationResult(False, f"Unknown policy section: {action.policy_section}")
        redundant = (action.policy_section or "") in runtime.fetched_context.policy_sections
        return ActionValidationResult(
            True,
            "Fetched policy section." if not redundant else "Policy section already fetched.",
            redundant=redundant,
        )

    if action.action_type in MODERATION_ACTIONS:
        redundant = runtime.decision == action.action_type
        return ActionValidationResult(
            True,
            "Moderation decision recorded." if not redundant else "Moderation decision already matches the active draft.",
            redundant=redundant,
        )

    if action.action_type == ActionType.COMPLETE_CASE:
        if runtime.decision is None:
            return ActionValidationResult(False, "Choose a moderation action before completing the case.")
        return ActionValidationResult(True, "Case completed and removed from queue.")

    return ActionValidationResult(False, "Unsupported action.")

