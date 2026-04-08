"""Parse model output into the existing ModBot action schema."""

from __future__ import annotations

import json
from typing import Any

from modbot.env.models.action import ActionModel
from modbot.env.models.config import ActionType
from modbot.env.models.observation import ObservationModel


def extract_json_object(raw_text: str) -> dict[str, Any]:
    """Extract the first JSON object from raw model text."""

    text = raw_text.strip()
    if not text:
        raise ValueError("Model output is empty.")

    try:
        payload = json.loads(text)
    except json.JSONDecodeError:
        payload = None

    if isinstance(payload, dict):
        return payload

    start = text.find("{")
    if start == -1:
        raise ValueError(f"Model output does not contain a JSON object: {text}")

    depth = 0
    in_string = False
    escaped = False
    for index in range(start, len(text)):
        char = text[index]
        if in_string:
            if escaped:
                escaped = False
            elif char == "\\":
                escaped = True
            elif char == '"':
                in_string = False
            continue

        if char == '"':
            in_string = True
        elif char == "{":
            depth += 1
        elif char == "}":
            depth -= 1
            if depth == 0:
                candidate = text[start : index + 1]
                try:
                    payload = json.loads(candidate)
                except json.JSONDecodeError as error:
                    raise ValueError(f"Failed to parse action JSON: {error.msg}") from error
                if isinstance(payload, dict):
                    return payload
                raise ValueError("Model output JSON must be an object.")

    raise ValueError("Model output contains an unterminated JSON object.")


def parse_action(raw_text: str) -> ActionModel:
    """Parse a model response into the existing Pydantic action model."""

    payload = extract_json_object(raw_text)
    return ActionModel.model_validate(payload)


def build_fallback_action(observation: ObservationModel, error: str | None = None) -> ActionModel:
    """Build a safe best-effort fallback action when parsing fails."""

    note = _truncate_note(error)
    current_report = observation.current_report
    allowed_actions = set(observation.allowed_actions)

    if (
        current_report is not None
        and observation.active_decision is not None
        and ActionType.COMPLETE_CASE in allowed_actions
    ):
        return ActionModel(
            action_type=ActionType.COMPLETE_CASE,
            report_id=current_report.report_id,
            notes=note,
        )

    if current_report is not None and ActionType.IGNORE_REPORT in allowed_actions:
        return ActionModel(
            action_type=ActionType.IGNORE_REPORT,
            report_id=current_report.report_id,
            notes=note,
        )

    if observation.queue_snapshot and ActionType.REVIEW_REPORT in allowed_actions:
        return ActionModel(
            action_type=ActionType.REVIEW_REPORT,
            report_id=observation.queue_snapshot[0].report_id,
            notes=note,
        )

    if current_report is not None and ActionType.ESCALATE_CASE in allowed_actions:
        return ActionModel(
            action_type=ActionType.ESCALATE_CASE,
            report_id=current_report.report_id,
            notes=note,
        )

    if observation.queue_snapshot:
        return ActionModel(
            action_type=ActionType.REVIEW_REPORT,
            report_id=observation.queue_snapshot[0].report_id,
            notes=note,
        )

    if current_report is not None:
        return ActionModel(
            action_type=ActionType.IGNORE_REPORT,
            report_id=current_report.report_id,
            notes=note,
        )

    return ActionModel(
        action_type=ActionType.REVIEW_REPORT,
        report_id="unknown-report",
        notes=note,
    )


def _truncate_note(error: str | None) -> str | None:
    """Keep fallback notes short enough for logs and traces."""

    if not error:
        return None
    return error[:180]
