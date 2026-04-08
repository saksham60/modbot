"""Episode runner for the benchmark-compatible inference entrypoint."""

from __future__ import annotations

import inspect
from dataclasses import dataclass, field

from clients.llm_client import OpenAIActionClient
from modbot.env.core.environment import ModBotEnv
from modbot.env.models.info import StepInfoModel

from scripts.action_parser import build_fallback_action, parse_action
from scripts.logging_utils import log_step


@dataclass(slots=True)
class EpisodeResult:
    """Final benchmark output for one episode."""

    success: bool = False
    steps: int = 0
    score: float = 0.0
    rewards: list[float] = field(default_factory=list)


def create_environment(task_name: str, image_name: str | None = None):
    """Create the environment using the existing ModBot API."""

    from_docker_image = getattr(ModBotEnv, "from_docker_image", None)
    if callable(from_docker_image) and image_name:
        for kwargs in (
            {"task_name": task_name},
            {"task_id": task_name},
        ):
            try:
                return from_docker_image(image_name, **kwargs)
            except TypeError:
                continue
    return ModBotEnv(task_id=task_name)


async def run_episode(
    env,
    llm_client: OpenAIActionClient,
    task_name: str,
    max_steps: int,
    success_threshold: float,
) -> EpisodeResult:
    """Run one episode and emit benchmark step logs."""

    observation = await _maybe_await(env.reset(task_id=task_name))
    rewards: list[float] = []
    steps = 0
    done = False
    last_info: StepInfoModel | None = None

    while not done and steps < max_steps:
        action_error: str | None = None
        try:
            raw_output = llm_client.generate_action_text(observation)
            action = parse_action(raw_output)
        except Exception as error:  # noqa: BLE001 - benchmark runner must recover and continue
            action_error = str(error)
            action = build_fallback_action(observation, error=action_error)

        observation, reward, done, info = await _maybe_await(env.step(action))
        steps += 1
        rewards.append(float(reward))
        last_info = info
        log_step(
            step=steps,
            action=action,
            reward=float(reward),
            done=bool(done),
            error=_resolve_error(info, action_error),
        )

    score = _compute_score(last_info, rewards)
    return EpisodeResult(
        success=score >= success_threshold,
        steps=steps,
        score=score,
        rewards=rewards,
    )


async def close_environment(env) -> None:
    """Close the environment if it exposes a close hook."""

    close_method = getattr(env, "close", None)
    if callable(close_method):
        await _maybe_await(close_method())


async def _maybe_await(value):
    if inspect.isawaitable(value):
        return await value
    return value


def _resolve_error(info: StepInfoModel, action_error: str | None) -> str | None:
    last_action_error = getattr(info, "last_action_error", None)
    if last_action_error:
        return str(last_action_error)
    if action_error:
        return action_error
    if not info.valid_action:
        return info.message
    return None


def _compute_score(info: StepInfoModel | None, rewards: list[float]) -> float:
    if info is not None and info.final_score is not None:
        return _clamp01(float(info.final_score))
    if not rewards:
        return 0.0
    average_reward = sum(rewards) / len(rewards)
    return _clamp01((average_reward + 2.0) / 4.0)


def _clamp01(value: float) -> float:
    return max(0.0, min(1.0, value))
