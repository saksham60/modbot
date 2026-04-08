"""Build strict JSON-only prompts for benchmark inference."""

from __future__ import annotations

import json

from modbot.env.models.observation import ObservationModel

SYSTEM_PROMPT = """You are an AI moderator operating a sequential trust and safety simulator.
Return exactly one JSON object for the next action.
Do not return markdown.
Do not return prose.
Do not wrap the JSON in code fences.
Use only actions listed in allowed_actions.
Only include fields that the chosen action needs.
If the case is ambiguous, fetch context before acting.
If the case is high-risk and uncertain, escalate it.
Avoid false removals of benign content.
Valid keys are: action_type, report_id, user_id, policy_section, notes."""


def build_messages(observation: ObservationModel) -> list[dict[str, str]]:
    """Convert the visible observation into chat messages for the model."""

    observation_payload = observation.model_dump(mode="json")
    allowed_actions = observation_payload.get("allowed_actions", [])
    user_prompt = "\n".join(
        [
            "Choose the next moderation action.",
            f"allowed_actions={allowed_actions}",
            "visible_observation=",
            json.dumps(observation_payload, ensure_ascii=True, separators=(",", ":")),
            "Return one JSON object only.",
        ]
    )
    return [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": user_prompt},
    ]
