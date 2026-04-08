"""Benchmark log formatting helpers."""

from __future__ import annotations

import json
from typing import Any


def log_start(task: str, env: str, model: str) -> None:
    """Emit the required benchmark start line."""

    print(f"[START] task={task} env={env} model={model}", flush=True)


def log_step(step: int, action: Any, reward: float, done: bool, error: str | None) -> None:
    """Emit the required benchmark step line."""

    error_text = error if error is not None else "null"
    print(
        f"[STEP] step={step} action={_format_action(action)} reward={reward:.2f} "
        f"done={_format_bool(done)} error={error_text}",
        flush=True,
    )


def log_end(success: bool, steps: int, score: float, rewards: list[float]) -> None:
    """Emit the required benchmark end line."""

    reward_text = ",".join(f"{reward:.2f}" for reward in rewards)
    print(
        f"[END] success={_format_bool(success)} steps={steps} score={score:.3f} rewards={reward_text}",
        flush=True,
    )


def _format_bool(value: bool) -> str:
    return "true" if value else "false"


def _format_action(action: Any) -> str:
    if isinstance(action, str):
        return action
    if hasattr(action, "model_dump"):
        payload = action.model_dump(exclude_none=True)
    elif isinstance(action, dict):
        payload = action
    else:
        payload = {"value": str(action)}
    return json.dumps(payload, ensure_ascii=True, separators=(",", ":"), sort_keys=True)
