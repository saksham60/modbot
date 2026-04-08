"""Gradio moderation operations console."""

from __future__ import annotations

import gradio as gr

from modbot.app.ui.services.session_service import auto_run_session, ensure_session, step_session
from modbot.env.models.config import ActionType
from modbot.env.policy.retrieval import list_policy_sections

CUSTOM_CSS = """
:root {
  --modbot-ink: #102a43;
  --modbot-panel: #f5f7f2;
  --modbot-accent: #1f6f5f;
  --modbot-accent-2: #d97b2d;
  --modbot-border: rgba(16, 42, 67, 0.12);
}
body, .gradio-container {
  font-family: 'IBM Plex Sans', 'Segoe UI', sans-serif;
  background:
    radial-gradient(circle at top left, rgba(217,123,45,0.14), transparent 30%),
    linear-gradient(180deg, #f7f3ea 0%, #edf2ef 100%);
}
.topbar {
  padding: 20px 24px;
  border: 1px solid var(--modbot-border);
  border-radius: 20px;
  background: linear-gradient(135deg, #12343b 0%, #1f6f5f 55%, #6fb98f 100%);
  color: white;
  box-shadow: 0 16px 40px rgba(18, 52, 59, 0.18);
}
.topbar h1 {
  margin: 0;
  font-size: 2rem;
  letter-spacing: 0.03em;
}
.topbar p {
  margin: 8px 0 0;
  max-width: 760px;
  color: rgba(255,255,255,0.84);
}
.metrics-strip {
  display: grid;
  grid-template-columns: repeat(6, minmax(0, 1fr));
  gap: 12px;
}
.metric-card {
  border: 1px solid var(--modbot-border);
  border-radius: 16px;
  background: rgba(255,255,255,0.86);
  padding: 12px 14px;
  box-shadow: 0 8px 24px rgba(16, 42, 67, 0.06);
}
.metric-card span {
  display: block;
  font-size: 0.75rem;
  letter-spacing: 0.06em;
  text-transform: uppercase;
  color: #486581;
}
.metric-card strong {
  display: block;
  margin-top: 6px;
  font-size: 1.25rem;
  color: var(--modbot-ink);
}
.panel-block {
  border: 1px solid var(--modbot-border);
  border-radius: 18px;
  background: rgba(255,255,255,0.78);
}
"""

UI_THEME = gr.themes.Soft()


def build_ui() -> gr.Blocks:
    """Build the Gradio console."""

    with gr.Blocks(title="ModBot Console") as demo:
        session_id = gr.State("")

        gr.HTML(
            """
            <div class='topbar'>
              <h1>ModBot Console</h1>
              <p>Sequential trust and safety simulator with queue pressure, review budget, appeals, and policy-aware moderation actions.</p>
            </div>
            """
        )

        with gr.Row():
            task_id = gr.Dropdown(["easy", "medium", "hard"], value="easy", label="Task")
            seed = gr.Number(value=7, precision=0, label="Seed")
            reset_button = gr.Button("Reset Episode", variant="primary")
            auto_button = gr.Button("Auto-Run Baseline")

        metrics_html = gr.HTML(elem_classes=["panel-block"])

        with gr.Row(equal_height=False):
            with gr.Column(scale=1):
                queue_table = gr.Dataframe(
                    headers=["Report", "Reason", "Reporters", "Priority", "Status"],
                    datatype=["str", "str", "str", "str", "str"],
                    interactive=False,
                    label="Review Queue",
                )
                trajectory_table = gr.Dataframe(
                    headers=["Step", "Action", "Report", "Reward", "Message"],
                    datatype=["str", "str", "str", "str", "str"],
                    interactive=False,
                    label="Trajectory Log",
                )
            with gr.Column(scale=2):
                report_panel = gr.Markdown(elem_classes=["panel-block"])
                context_panel = gr.Markdown(elem_classes=["panel-block"])
                status_panel = gr.Markdown(elem_classes=["panel-block"])

        with gr.Row():
            action_type = gr.Dropdown(
                choices=[action.value for action in ActionType],
                value=ActionType.REVIEW_REPORT.value,
                label="Action Type",
            )
            report_id = gr.Textbox(label="Report ID", placeholder="active report id or queued report id")
            user_id = gr.Textbox(label="User ID", placeholder="needed for fetch_user_history")
            policy_section = gr.Dropdown(
                choices=list_policy_sections(),
                value=None,
                label="Policy Section",
                allow_custom_value=True,
            )
        notes = gr.Textbox(label="Notes", placeholder="Optional moderation notes")
        step_button = gr.Button("Step Action", variant="primary")
        summary_panel = gr.Markdown(elem_classes=["panel-block"])

        outputs = [
            session_id,
            metrics_html,
            queue_table,
            report_panel,
            context_panel,
            status_panel,
            trajectory_table,
            summary_panel,
        ]

        demo.load(lambda: ensure_session("easy", 7, None), outputs=outputs)
        reset_button.click(ensure_session, inputs=[task_id, seed, session_id], outputs=outputs)
        step_button.click(
            step_session,
            inputs=[session_id, task_id, seed, action_type, report_id, user_id, policy_section, notes],
            outputs=outputs,
        )
        auto_button.click(auto_run_session, inputs=[session_id, task_id, seed], outputs=outputs)

    return demo

