"""Model client abstraction plus a deterministic heuristic baseline."""

from __future__ import annotations

import json
import os
import urllib.error
import urllib.request
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any

from modbot.env.models.action import ActionModel
from modbot.env.models.config import ActionType
from modbot.env.models.observation import ObservationModel
from modbot.clients.prompt_builder import SYSTEM_PROMPT

SATIRE_CUES = [
    "minister of naps",
    "raccoons run the central bank",
    "sure.",
    "obviously",
    "satire",
    "joke",
]
SPAM_CUES = ["crypto", "profit", "free phones", "miracle", "dm for access", "sign up here"]
THREAT_CUES = ["coming for you", "teach that rat a lesson", "drop their address", "street", "number"]
SELF_HARM_CUES = ["end for me", "can't do this anymore", "self-harm"]


@dataclass
class ModelClientConfig:
    """Connection config for model-backed evaluation."""

    backend: str
    model_name: str
    base_url: str
    api_key: str | None
    timeout_seconds: int = 30


def _contains_any(text: str, phrases: list[str]) -> bool:
    text = text.lower()
    return any(phrase in text for phrase in phrases)


def choose_action(observation) -> ActionModel:
    """Choose a deterministic baseline action from an observation."""

    if observation.current_report is None:
        next_report = observation.queue_snapshot[0]
        return ActionModel(action_type=ActionType.REVIEW_REPORT, report_id=next_report.report_id)

    report = observation.current_report
    fetched = observation.fetched_context
    decision = observation.active_decision
    text = report.content_text.lower()
    reason = report.report_reason.lower()
    note = report.visible_note.lower()
    policy_sections = {snippet.section for snippet in fetched.policy_snippets}

    if decision is not None:
        return ActionModel(action_type=ActionType.COMPLETE_CASE, report_id=report.report_id)

    if observation.remaining_review_budget > 0:
        if _contains_any(text, SELF_HARM_CUES) and "SELF-HARM-ESC" not in policy_sections:
            return ActionModel(action_type=ActionType.FETCH_POLICY, policy_section="SELF-HARM-ESC")
        if (_contains_any(text, SATIRE_CUES) or "satirical" in note or "dogpile" in note) and fetched.thread_context is None:
            return ActionModel(action_type=ActionType.FETCH_THREAD_CONTEXT, report_id=report.report_id)
        if ("harassment" in reason or "bullying" in reason) and fetched.user_history is None and report.reporter_count <= 3:
            return ActionModel(action_type=ActionType.FETCH_USER_HISTORY, user_id=report.user_id)
        if "misinformation" in reason and "MISINFO-2" not in policy_sections and not _contains_any(text, SATIRE_CUES):
            return ActionModel(action_type=ActionType.FETCH_POLICY, policy_section="MISINFO-2")
        if "self-harm" in reason and "SELF-HARM-ESC" not in policy_sections:
            return ActionModel(action_type=ActionType.FETCH_POLICY, policy_section="SELF-HARM-ESC")

    if _contains_any(text, THREAT_CUES) or "violent threat" in reason or "doxxing" in reason:
        return ActionModel(action_type=ActionType.REMOVE_CONTENT, report_id=report.report_id)
    if _contains_any(text, SELF_HARM_CUES) or "self-harm" in reason:
        return ActionModel(action_type=ActionType.ESCALATE_CASE, report_id=report.report_id)
    if _contains_any(text, SPAM_CUES) or "spam" in reason or "scam" in reason:
        return ActionModel(action_type=ActionType.REMOVE_CONTENT, report_id=report.report_id)
    if _contains_any(text, SATIRE_CUES) or (fetched.thread_context and fetched.thread_context.irony_signal > 0.75):
        return ActionModel(action_type=ActionType.IGNORE_REPORT, report_id=report.report_id)
    if "misinformation" in reason:
        return ActionModel(action_type=ActionType.ESCALATE_CASE, report_id=report.report_id)
    if "bullying" in reason or "harassment" in reason:
        if fetched.user_history and fetched.user_history.prior_warnings >= 2:
            return ActionModel(action_type=ActionType.REMOVE_CONTENT, report_id=report.report_id)
        return ActionModel(action_type=ActionType.WARN_USER, report_id=report.report_id)
    return ActionModel(action_type=ActionType.IGNORE_REPORT, report_id=report.report_id)


class BaseModelClient(ABC):
    """Return structured next actions from prompts."""

    @abstractmethod
    def generate_action(self, prompt: str, observation: ObservationModel) -> dict[str, Any]:
        """Return a structured action dictionary."""


class HeuristicModelClient(BaseModelClient):
    """Local deterministic baseline client."""

    def generate_action(self, prompt: str, observation: ObservationModel) -> dict[str, Any]:
        action = choose_action(observation)
        return action.model_dump(exclude_none=True)


class OpenAICompatibleModelClient(BaseModelClient):
    """Call any OpenAI-compatible chat completion endpoint."""

    def __init__(self, config: ModelClientConfig) -> None:
        if not config.api_key:
            raise RuntimeError("Missing API key. Set MODEL_API_KEY, HF_TOKEN, or OPENAI_API_KEY.")
        if not config.model_name:
            raise RuntimeError("Missing model name. Set MODEL_NAME.")
        self.config = config

    def generate_action(self, prompt: str, observation: ObservationModel) -> dict[str, Any]:
        payload = {
            "model": self.config.model_name,
            "temperature": 0.0,
            "response_format": {"type": "json_object"},
            "messages": [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": prompt},
            ],
        }
        request = urllib.request.Request(
            url=f"{self.config.base_url.rstrip('/')}/chat/completions",
            data=json.dumps(payload).encode("utf-8"),
            headers={
                "Authorization": f"Bearer {self.config.api_key}",
                "Content-Type": "application/json",
            },
            method="POST",
        )
        try:
            with urllib.request.urlopen(request, timeout=self.config.timeout_seconds) as response:
                body = json.loads(response.read().decode("utf-8"))
        except urllib.error.URLError as error:
            raise RuntimeError(f"Model request failed: {error}") from error

        message = body["choices"][0]["message"]["content"]
        return parse_action_json(message)


def parse_action_json(raw_text: str) -> dict[str, Any]:
    """Extract and parse a JSON action payload from model output."""

    text = raw_text.strip()
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        start = text.find("{")
        end = text.rfind("}")
        if start == -1 or end == -1 or end <= start:
            raise ValueError(f"Model output does not contain JSON: {raw_text}")
        return json.loads(text[start : end + 1])


def build_model_client() -> BaseModelClient:
    """Build a model client from environment variables."""

    backend = os.getenv("MODEL_BACKEND", "heuristic").lower()
    if backend == "heuristic":
        return HeuristicModelClient()

    api_key = os.getenv("MODEL_API_KEY") or os.getenv("HF_TOKEN") or os.getenv("OPENAI_API_KEY")
    default_base_url = "https://router.huggingface.co/v1" if backend == "huggingface" else "https://api.openai.com/v1"
    config = ModelClientConfig(
        backend=backend,
        model_name=os.getenv("MODEL_NAME", ""),
        base_url=os.getenv("MODEL_BASE_URL", default_base_url),
        api_key=api_key,
        timeout_seconds=int(os.getenv("MODEL_TIMEOUT_SECONDS", "30")),
    )
    return OpenAICompatibleModelClient(config)

