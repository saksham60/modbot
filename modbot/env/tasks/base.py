"""Base task loader implementation."""

from __future__ import annotations

from abc import ABC
from pathlib import Path

from modbot.env.models.config import TaskScenarioModel
from modbot.env.utils.files import package_path, load_json_file
from modbot.env.utils.seeds import normalize_seed, seeded_random


class BaseTaskLoader(ABC):
    """Load task scenarios from structured JSON fixtures."""

    data_subdir: str

    def scenario_files(self) -> list[Path]:
        """Return sorted scenario files for the task."""

        data_dir = package_path("data", self.data_subdir)
        return sorted(data_dir.glob("*.json"))

    def load(self, seed: int | None = None) -> TaskScenarioModel:
        """Load a concrete scenario using deterministic seed selection."""

        files = self.scenario_files()
        if not files:
            raise FileNotFoundError(f"No scenario files found for task: {self.data_subdir}")

        normalized = normalize_seed(seed)
        scenario_path = files[normalized % len(files)]
        raw = load_json_file(scenario_path)
        scenario = TaskScenarioModel.model_validate(raw)
        scenario.seed = normalized
        scenario.reports = self._seed_reports(scenario.reports, normalized)
        return scenario

    def _seed_reports(self, reports, seed: int):
        """Apply deterministic tie-breaking for queue order."""

        rng = seeded_random(seed)
        decorated = [(-report.queue_priority, rng.random(), report) for report in reports]
        decorated.sort(key=lambda item: (item[0], item[1]))
        return [item[2] for item in decorated]

