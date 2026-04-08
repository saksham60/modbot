"""Action execution helpers for ModBot."""

from dataclasses import dataclass

from modbot.env.actions.validator import MODERATION_ACTIONS, action_budget_cost
from modbot.env.models.action import ActionModel
from modbot.env.models.config import ActionType
from modbot.env.models.config import ReportTruthModel
from modbot.env.models.state import HiddenWorldStateModel
from modbot.env.policy.retrieval import get_policy_snippet
from modbot.env.state.state_manager import get_active_report, get_report
from modbot.env.state.appeal_manager import apply_case_deltas, resolve_case_impact
from modbot.env.state.queue_manager import activate_report, complete_report, set_decision


@dataclass(slots=True)
class ActionExecutionResult:
    """Structured side effects used by reward shaping and debug info."""

    message: str
    budget_spent: int = 0
    redundant: bool = False
    relevant_context: float = 0.0
    decision_quality: float = 0.0
    severe_correct: bool = False
    benign_preserved: bool = False
    false_removal: bool = False
    missed_harm: bool = False
    completed_case: bool = False
    queue_progress: float = 0.0
    wasted_budget: float = 0.0
    trust_delta: float = 0.0
    appeal_delta: float = 0.0


def _decision_quality(decision: ActionType | None, truth: ReportTruthModel) -> float:
    if decision is None:
        return 0.0
    if decision == truth.gold_action:
        return 1.0
    if not truth.harmful and decision == ActionType.IGNORE_REPORT:
        return 0.8
    if not truth.harmful and decision == ActionType.ESCALATE_CASE:
        return -0.5
    if not truth.harmful and decision in {ActionType.REMOVE_CONTENT, ActionType.WARN_USER}:
        return -1.0
    if truth.harmful and decision == ActionType.IGNORE_REPORT:
        return -1.0
    if truth.gold_action == ActionType.REMOVE_CONTENT and decision == ActionType.WARN_USER:
        return 0.15
    if truth.gold_action == ActionType.WARN_USER and decision == ActionType.REMOVE_CONTENT:
        return -0.45
    if truth.gold_action == ActionType.ESCALATE_CASE and decision == ActionType.REMOVE_CONTENT:
        return 0.1
    if truth.gold_action == ActionType.ESCALATE_CASE and decision == ActionType.WARN_USER:
        return -0.4
    if truth.gold_action == ActionType.WARN_USER and decision == ActionType.ESCALATE_CASE:
        return 0.1
    return -0.35


def execute_action(state: HiddenWorldStateModel, action: ActionModel, validation) -> ActionExecutionResult:
    """Execute a validated action and mutate hidden state."""

    budget_spent = action_budget_cost(action.action_type)
    if budget_spent:
        state.remaining_review_budget = max(0, state.remaining_review_budget - budget_spent)

    if action.action_type == ActionType.REVIEW_REPORT:
        if validation.redundant:
            state.runtime_reports[action.report_id].redundant_actions += 1
            return ActionExecutionResult(
                message="Report was already the active case.",
                budget_spent=budget_spent,
                redundant=True,
                wasted_budget=1.0,
            )
        activate_report(state, action.report_id)
        return ActionExecutionResult(
            message=f"Active report set to {action.report_id}.",
            budget_spent=budget_spent,
        )

    active_report = get_active_report(state)
    runtime = state.runtime_reports[active_report.report_id]
    truth = active_report.truth

    if action.action_type == ActionType.FETCH_USER_HISTORY:
        if validation.redundant:
            runtime.redundant_actions += 1
        runtime.fetched_context.user_history = True
        relevant = 1.0 if truth.requires_user_history else 0.0
        return ActionExecutionResult(
            message="User history retrieved for the active report.",
            budget_spent=budget_spent,
            redundant=validation.redundant,
            relevant_context=relevant,
            wasted_budget=1.0 if validation.redundant or relevant == 0.0 else 0.0,
        )

    if action.action_type == ActionType.FETCH_THREAD_CONTEXT:
        if validation.redundant:
            runtime.redundant_actions += 1
        runtime.fetched_context.thread_context = True
        relevant = 1.0 if truth.requires_thread_context else 0.0
        return ActionExecutionResult(
            message="Thread context retrieved for the active report.",
            budget_spent=budget_spent,
            redundant=validation.redundant,
            relevant_context=relevant,
            wasted_budget=1.0 if validation.redundant or relevant == 0.0 else 0.0,
        )

    if action.action_type == ActionType.FETCH_POLICY:
        if validation.redundant:
            runtime.redundant_actions += 1
        section = action.policy_section or ""
        if section not in runtime.fetched_context.policy_sections:
            runtime.fetched_context.policy_sections.append(section)
        relevant = 1.0 if section == active_report.relevant_policy_section else 0.0
        title = get_policy_snippet(section).title if get_policy_snippet(section) else section
        return ActionExecutionResult(
            message=f"Policy section '{title}' retrieved.",
            budget_spent=budget_spent,
            redundant=validation.redundant,
            relevant_context=relevant,
            wasted_budget=1.0 if validation.redundant or relevant == 0.0 else 0.0,
        )

    if action.action_type in MODERATION_ACTIONS:
        if action.notes:
            runtime.notes.append(action.notes)
        previous_quality = _decision_quality(runtime.decision, truth)
        set_decision(state, active_report.report_id, action.action_type)
        new_quality = _decision_quality(action.action_type, truth)
        exact_correct = action.action_type == truth.gold_action
        return ActionExecutionResult(
            message=f"Draft decision set to {action.action_type.value}.",
            redundant=validation.redundant,
            decision_quality=0.0 if validation.redundant else round(new_quality - previous_quality, 4),
            severe_correct=exact_correct and truth.severe_violation,
            benign_preserved=exact_correct and not truth.harmful and action.action_type == ActionType.IGNORE_REPORT,
            false_removal=(not truth.harmful and action.action_type == ActionType.REMOVE_CONTENT),
            missed_harm=(truth.harmful and action.action_type == ActionType.IGNORE_REPORT),
        )

    if action.action_type == ActionType.COMPLETE_CASE:
        if action.notes:
            runtime.notes.append(action.notes)
        trust_delta, appeal_delta = resolve_case_impact(truth, runtime.decision)
        apply_case_deltas(state, trust_delta=trust_delta, appeal_delta=appeal_delta)
        complete_report(state, active_report.report_id)
        return ActionExecutionResult(
            message=f"Completed case {active_report.report_id} with final decision {runtime.decision.value}.",
            completed_case=True,
            queue_progress=1.0,
            trust_delta=trust_delta,
            appeal_delta=appeal_delta,
        )

    report = get_report(state, action.report_id or "")
    return ActionExecutionResult(message=f"No execution path found for {report.report_id if report else 'unknown'}.")

