"""OpenAI-backed LLM client used by the benchmark inference wrapper."""

from __future__ import annotations

from dataclasses import dataclass

from openai import OpenAI

from clients.prompt_builder import build_messages
from modbot.env.models.observation import ObservationModel


@dataclass(slots=True)
class LLMClientConfig:
    """Runtime configuration for one benchmark inference session."""

    model_name: str
    timeout_seconds: float = 30.0
    temperature: float = 0.0


class OpenAIActionClient:
    """Thin adapter over the OpenAI chat completions client."""

    def __init__(self, client: OpenAI, config: LLMClientConfig) -> None:
        self.client = client
        self.config = config

    def generate_action_text(self, observation: ObservationModel) -> str:
        """Return the raw model text for the next action."""

        response = self.client.chat.completions.create(
            model=self.config.model_name,
            messages=build_messages(observation),
            temperature=self.config.temperature,
            response_format={"type": "json_object"},
            timeout=self.config.timeout_seconds,
        )
        content = response.choices[0].message.content
        if not content:
            raise RuntimeError("Model returned an empty response.")
        return content
