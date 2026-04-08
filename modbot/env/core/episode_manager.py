"""Episode termination logic."""

from modbot.env.models.config import DifficultyLevel
from modbot.env.state.queue_manager import pending_case_count


class EpisodeManager:
    """Decide when an episode is done."""

    def evaluate_done(self, state) -> str | None:
        """Return a done reason or None if the episode should continue."""

        if pending_case_count(state) == 0:
            return "all_cases_completed"
        if state.step_count >= state.task.config.max_steps:
            return "max_steps_reached"
        if state.remaining_review_budget <= 0 and state.active_report_id is None and pending_case_count(state) > 0:
            return "review_budget_exhausted"
        if state.task.difficulty == DifficultyLevel.HARD and state.backlog_pressure >= 95.0:
            return "backlog_collapse"
        return None

