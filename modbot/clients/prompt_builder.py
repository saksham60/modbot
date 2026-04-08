"""Prompt construction helpers for model-driven evaluation."""

from modbot.env.models.observation import ObservationModel

SYSTEM_PROMPT = """You are an AI moderator operating a sequential trust and safety simulator.
Choose exactly one next action.
Return JSON only with these fields when needed: action_type, report_id, user_id, policy_section, notes.
Do not add explanation outside JSON."""


def observation_to_prompt(observation: ObservationModel) -> str:
    """Render a structured observation into a compact action prompt."""

    queue_lines = [
        f"- {item.report_id}: reason={item.report_reason}, reporters={item.reporter_count}, priority={item.queue_priority}, status={item.status.value}"
        for item in observation.queue_snapshot
    ]
    policy_lines = [
        f"- {snippet.section}: {snippet.title}"
        for snippet in observation.fetched_context.policy_snippets
    ]
    current_report = "none"
    if observation.current_report is not None:
        current_report = (
            f"id={observation.current_report.report_id}\n"
            f"reason={observation.current_report.report_reason}\n"
            f"content={observation.current_report.content_text}\n"
            f"note={observation.current_report.visible_note}\n"
            f"author={observation.current_report.author_handle}\n"
        )

    return "\n".join(
        [
            f"Task: {observation.task_id}",
            f"Step: {observation.step}",
            f"Remaining budget: {observation.remaining_review_budget}",
            f"Allowed actions: {[action.value for action in observation.allowed_actions]}",
            f"Metrics: trust={observation.visible_metrics.community_trust}, appeal={observation.visible_metrics.appeal_pressure}, backlog={observation.visible_metrics.backlog_pressure}",
            "Current report:",
            current_report,
            "Queue snapshot:",
            *queue_lines,
            "Fetched policy:",
            *(policy_lines or ["- none"]),
            f"User history fetched: {observation.fetched_context.user_history is not None}",
            f"Thread context fetched: {observation.fetched_context.thread_context is not None}",
            "Return only a single JSON object for the next action.",
        ]
    )
