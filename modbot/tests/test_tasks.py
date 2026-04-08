from modbot.env.core.environment import ModBotEnv
from modbot.env.tasks.task_factory import TaskFactory


def test_task_factory_loads_all_tasks() -> None:
    factory = TaskFactory()
    easy = factory.create("easy", seed=7)
    medium = factory.create("medium", seed=7)
    hard = factory.create("hard", seed=7)

    assert easy.task_id == "easy"
    assert medium.task_id == "medium"
    assert hard.task_id == "hard"
    assert len(hard.reports) == 8


def test_seed_determinism_changes_queue_order() -> None:
    env_a = ModBotEnv(task_id="hard", seed=7)
    env_b = ModBotEnv(task_id="hard", seed=7)
    env_c = ModBotEnv(task_id="hard", seed=8)

    obs_a = env_a.reset()
    obs_b = env_b.reset()
    obs_c = env_c.reset()

    assert [item.report_id for item in obs_a.queue_snapshot] == [item.report_id for item in obs_b.queue_snapshot]
    assert [item.report_id for item in obs_a.queue_snapshot] != [item.report_id for item in obs_c.queue_snapshot]
