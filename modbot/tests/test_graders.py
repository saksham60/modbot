from modbot.env.core.environment import ModBotEnv
from modbot.clients.llm_client import choose_action


def test_grader_is_reproducible_for_identical_seed_and_policy() -> None:
    env_a = ModBotEnv(task_id="hard", seed=7)
    env_b = ModBotEnv(task_id="hard", seed=7)

    for env in (env_a, env_b):
        observation = env.reset()
        done = False
        while not done:
            action = choose_action(observation)
            observation, _, done, _ = env.step(action)

    assert env_a.grade() == env_b.grade()
