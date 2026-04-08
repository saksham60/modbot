"""Main ModBot environment class."""

from __future__ import annotations

from modbot.env.core.episode_manager import EpisodeManager
from modbot.env.core.transition_engine import TransitionEngine
from modbot.env.grader.factory import GraderFactory
from modbot.env.models.action import ActionModel
from modbot.env.models.info import StepInfoModel
from modbot.env.models.observation import ObservationModel
from modbot.env.models.state import EnvironmentStateModel
from modbot.env.observation.builder import ObservationBuilder
from modbot.env.reward.reward_engine import RewardEngine
from modbot.env.state.state_manager import build_public_state, initialize_hidden_state
from modbot.env.state.trust_manager import recompute_backlog_pressure
from modbot.env.tasks.task_factory import TaskFactory
from modbot.env.utils.files import load_yaml_file, package_path
from modbot.env.utils.seeds import normalize_seed


class ModBotEnv:
    """Stateful RL-style moderation operations environment."""

    def __init__(self, task_id: str | None = None, seed: int | None = None) -> None:
        config = load_yaml_file(package_path("configs", "env.yaml"))
        self.default_task = task_id or config.get("default_task", "easy")
        self.default_seed = normalize_seed(seed if seed is not None else config.get("default_seed", 7))
        self.task_factory = TaskFactory()
        self.observation_builder = ObservationBuilder()
        self.reward_engine = RewardEngine()
        self.episode_manager = EpisodeManager()
        self.grader_factory = GraderFactory()
        self.transition_engine = TransitionEngine(
            observation_builder=self.observation_builder,
            reward_engine=self.reward_engine,
            episode_manager=self.episode_manager,
            grader_factory=self.grader_factory,
        )
        self._state = None
        self.current_task_id = self.default_task
        self.current_seed = self.default_seed

    def reset(self, task_id: str | None = None, seed: int | None = None) -> ObservationModel:
        """Reset the environment and return the first observation."""

        self.current_task_id = task_id or self.default_task
        self.current_seed = normalize_seed(seed if seed is not None else self.default_seed)
        scenario = self.task_factory.create(self.current_task_id, seed=self.current_seed)
        self._state = initialize_hidden_state(scenario)
        recompute_backlog_pressure(self._state)
        return self.observation_builder.build(self._state)

    def step(self, action: ActionModel | dict) -> tuple[ObservationModel, float, bool, StepInfoModel]:
        """Advance the environment by one action."""

        if self._state is None:
            self.reset()
        if self._state.done:
            observation = self.observation_builder.build(self._state)
            info = StepInfoModel(
                valid_action=False,
                message="Episode is already complete. Call reset() to start a new run.",
                reward=0.0,
                reward_breakdown={},
                done_reason=self._state.done_reason,
                final_score=self._state.final_score,
                grader_components=dict(self._state.grader_components),
                state_summary={
                    "pending_reports": 0,
                    "completed_cases": len(self._state.task.reports),
                    "active_report_id": self._state.active_report_id,
                },
            )
            return observation, 0.0, True, info

        action_model = action if isinstance(action, ActionModel) else ActionModel.model_validate(action)
        return self.transition_engine.step(self._state, action_model)

    def state(self) -> EnvironmentStateModel:
        """Return a safe state view for debugging and APIs."""

        if self._state is None:
            self.reset()
        return build_public_state(self._state)

    def grade(self) -> tuple[float, dict[str, float]]:
        """Return the deterministic grader output for the current episode."""

        if self._state is None:
            self.reset()
        if self._state.final_score is None:
            score, components = self.grader_factory.grade(self._state)
            return score, components
        return self._state.final_score, dict(self._state.grader_components)

