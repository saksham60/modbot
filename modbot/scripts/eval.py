"""Baseline evaluation runner for all ModBot tasks."""

from __future__ import annotations

import argparse
import json
from statistics import mean

from modbot.env.core.environment import ModBotEnv
from modbot.env.models.action import ActionModel
from modbot.clients.llm_client import build_model_client
from modbot.clients.prompt_builder import observation_to_prompt


def run_episode(task_id: str, seed: int, max_steps: int | None = None) -> dict:
    """Run a single task episode using the configured model client."""

    env = ModBotEnv(task_id=task_id, seed=seed)
    client = build_model_client()
    observation = env.reset(task_id=task_id, seed=seed)
    done = False
    steps = 0
    last_info = None

    while not done:
        prompt = observation_to_prompt(observation)
        action_payload = client.generate_action(prompt, observation)
        action = ActionModel.model_validate(action_payload)
        observation, reward, done, info = env.step(action)
        steps += 1
        last_info = info
        if max_steps is not None and steps >= max_steps and not done:
            break

    score, components = env.grade()
    return {
        "task_id": task_id,
        "seed": seed,
        "steps": steps,
        "score": score,
        "components": components,
        "done_reason": last_info.done_reason if last_info else None,
        "total_reward": env.state().total_reward,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Run baseline evaluation across all ModBot tasks.")
    parser.add_argument("--seed", type=int, default=7, help="Seed used for all tasks.")
    parser.add_argument("--max-steps", type=int, default=None, help="Optional cap for evaluation steps.")
    args = parser.parse_args()

    task_ids = ["easy", "medium", "hard"]
    results = [run_episode(task_id, seed=args.seed, max_steps=args.max_steps) for task_id in task_ids]
    aggregate_score = round(mean(result["score"] for result in results), 4)

    print(json.dumps({"results": results, "aggregate_score": aggregate_score}, indent=2))


if __name__ == "__main__":
    main()

