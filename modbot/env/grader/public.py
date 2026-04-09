"""Public callable graders for OpenEnv validators."""

from __future__ import annotations

from typing import Any

from modbot.env.core.environment import ModBotEnv
from modbot.env.models.action import ActionModel


def grade_task(task_id: str, actions: list[dict[str, Any]] | None = None, seed: int | None = None) -> dict[str, Any]:
    """Replay an action list for a task and return deterministic grader output."""

    env = ModBotEnv(task_id=task_id, seed=seed)
    env.reset(task_id=task_id, seed=seed)
    evaluated = 0

    for payload in actions or []:
        action = ActionModel.model_validate(payload)
        _, _, done, _ = env.step(action)
        evaluated += 1
        if done:
            break

    score, components = env.grade()
    return {
        "task_id": task_id,
        "score": score,
        "components": components,
        "actions_evaluated": evaluated,
    }


def grade_easy(actions: list[dict[str, Any]] | None = None, seed: int | None = None) -> dict[str, Any]:
    """Grade an easy-task trajectory."""

    return grade_task("easy", actions=actions, seed=seed)


def grade_medium(actions: list[dict[str, Any]] | None = None, seed: int | None = None) -> dict[str, Any]:
    """Grade a medium-task trajectory."""

    return grade_task("medium", actions=actions, seed=seed)


def grade_hard(actions: list[dict[str, Any]] | None = None, seed: int | None = None) -> dict[str, Any]:
    """Grade a hard-task trajectory."""

    return grade_task("hard", actions=actions, seed=seed)
