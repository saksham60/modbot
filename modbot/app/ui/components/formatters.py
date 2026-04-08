"""Formatting helpers for the Gradio moderation console."""

from modbot.env.utils.serialization import to_serializable


def queue_rows(observation) -> list[list[str]]:
    """Return tabular queue rows for the UI."""

    return [
        [
            item.report_id,
            item.report_reason,
            str(item.reporter_count),
            str(item.queue_priority),
            item.status.value,
        ]
        for item in observation.queue_snapshot
    ]


def trajectory_rows(state) -> list[list[str]]:
    """Return tabular trajectory rows for the UI."""

    return [
        [
            str(entry.step),
            entry.action_type.value,
            entry.report_id or "-",
            f"{entry.reward:.2f}",
            entry.message,
        ]
        for entry in state.trajectory
    ]


def render_report_panel(observation) -> str:
    """Render the active report panel."""

    if observation.current_report is None:
        return "## Current Report\nNo active report. Use `review_report` on the next queue item."

    report = observation.current_report
    return "\n".join(
        [
            "## Current Report",
            f"**Report ID:** `{report.report_id}`",
            f"**Author:** `{report.author_handle}` (`{report.user_id}`)",
            f"**Reason:** {report.report_reason}",
            f"**Reporters:** {report.reporter_count}",
            f"**Priority:** {report.queue_priority}",
            f"**Content Type:** {report.content_type}",
            f"**Visible Note:** {report.visible_note}",
            "",
            report.content_text,
        ]
    )


def render_context_panel(observation) -> str:
    """Render fetched user history, thread context, and policy snippets."""

    fetched = observation.fetched_context
    lines = ["## Fetched Context"]
    if fetched.user_history is not None:
        lines.extend(
            [
                "### User History",
                f"Warnings: {fetched.user_history.prior_warnings}",
                f"Removals: {fetched.user_history.prior_removals}",
                f"Recent reports: {fetched.user_history.recent_reports_against}",
                f"Trust tier: {fetched.user_history.trust_tier}",
                fetched.user_history.note,
            ]
        )
    else:
        lines.append("### User History\nNot fetched.")

    if fetched.thread_context is not None:
        lines.extend(
            [
                "### Thread Context",
                fetched.thread_context.summary,
                f"Hostility signal: {fetched.thread_context.hostility_signal}",
                f"Irony signal: {fetched.thread_context.irony_signal}",
                f"Brigading signal: {fetched.thread_context.brigading_signal}",
            ]
        )
    else:
        lines.append("### Thread Context\nNot fetched.")

    if fetched.policy_snippets:
        lines.append("### Policy")
        for snippet in fetched.policy_snippets:
            lines.append(f"`{snippet.section}` {snippet.title}: {snippet.summary}")
    else:
        lines.append("### Policy\nNo policy sections fetched.")
    return "\n\n".join(lines)


def render_metrics_strip(observation, state) -> str:
    """Render the operations metric strip as HTML cards."""

    score = "-" if state.final_score is None else f"{state.final_score:.2f}"
    return f"""
    <div class='metrics-strip'>
      <div class='metric-card'><span>Trust</span><strong>{observation.visible_metrics.community_trust:.1f}</strong></div>
      <div class='metric-card'><span>Appeal Pressure</span><strong>{observation.visible_metrics.appeal_pressure:.1f}</strong></div>
      <div class='metric-card'><span>Backlog</span><strong>{observation.visible_metrics.backlog_pressure:.1f}</strong></div>
      <div class='metric-card'><span>Budget</span><strong>{observation.remaining_review_budget}</strong></div>
      <div class='metric-card'><span>Total Return</span><strong>{state.total_reward:.2f}</strong></div>
      <div class='metric-card'><span>Final Score</span><strong>{score}</strong></div>
    </div>
    """


def render_status_panel(observation, last_message: str) -> str:
    """Render high-level step guidance and the latest event."""

    allowed = ", ".join(action.value for action in observation.allowed_actions) or "none"
    message = last_message or "Session ready."
    return "\n".join(
        [
            "## Operator Feed",
            f"**Latest event:** {message}",
            f"**Allowed actions:** {allowed}",
        ]
    )


def render_summary(state) -> str:
    """Render the episode summary pane."""

    if not state.done:
        return "## Episode Summary\nEpisode still in progress."

    lines = [
        "## Episode Summary",
        f"**Done reason:** {state.done_reason}",
        f"**Final score:** {state.final_score:.3f}",
        "### Grader Components",
    ]
    for key, value in state.grader_components.items():
        lines.append(f"- {key}: {value:.3f}")
    return "\n".join(lines)


def render_state_json(state) -> str:
    """Return a compact serialized state payload for debugging."""

    return str(to_serializable(state))
