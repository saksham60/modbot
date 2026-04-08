"""Task factory for creating seeded scenarios by difficulty."""

from modbot.env.models.config import DifficultyLevel
from modbot.env.models.config import TaskScenarioModel
from modbot.env.tasks.easy_task import EasyTaskLoader
from modbot.env.tasks.hard_task import HardTaskLoader
from modbot.env.tasks.medium_task import MediumTaskLoader


class TaskFactory:
    """Create task scenarios for environment resets."""

    def __init__(self) -> None:
        self._loaders = {
            DifficultyLevel.EASY.value: EasyTaskLoader(),
            DifficultyLevel.MEDIUM.value: MediumTaskLoader(),
            DifficultyLevel.HARD.value: HardTaskLoader(),
        }

    def create(self, task_id: str, seed: int | None = None) -> TaskScenarioModel:
        """Return a seeded scenario for a named task."""

        if task_id not in self._loaders:
            supported = ", ".join(sorted(self._loaders))
            raise ValueError(f"Unsupported task '{task_id}'. Expected one of: {supported}")
        return self._loaders[task_id].load(seed=seed)

