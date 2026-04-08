"""Run a single task using the heuristic baseline and print a readable summary."""

from __future__ import annotations

import argparse

from modbot.env.core.environment import ModBotEnv
from modbot.clients.llm_client import choose_action


def main() -> None:
    parser = argparse.ArgumentParser(description="Simulate a ModBot episode with the heuristic baseline.")
    parser.add_argument("task_id", choices=["easy", "medium", "hard"], nargs="?", default="easy")
    parser.add_argument("--seed", type=int, default=7)
    args = parser.parse_args()

    env = ModBotEnv(task_id=args.task_id, seed=args.seed)
    observation = env.reset(task_id=args.task_id, seed=args.seed)
    done = False

    while not done:
        action = choose_action(observation)
        observation, reward, done, info = env.step(action)
        print(f"step={observation.step} action={action.action_type.value} reward={reward:.3f} msg={info.message}")

    score, components = env.grade()
    print(f"final_score={score:.3f} components={components}")


if __name__ == "__main__":
    main()

