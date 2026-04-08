"""Factory for task-specific deterministic graders."""

from modbot.env.grader.easy_grader import EasyTaskGrader
from modbot.env.grader.hard_grader import HardTaskGrader
from modbot.env.grader.medium_grader import MediumTaskGrader


class GraderFactory:
    """Create the grader associated with a task id."""

    def __init__(self) -> None:
        self._graders = {
            "easy": EasyTaskGrader(),
            "medium": MediumTaskGrader(),
            "hard": HardTaskGrader(),
        }

    def grade(self, state):
        """Return the deterministic grade for a finished episode."""

        grader = self._graders[state.task.config.grader_key]
        return grader.grade(state)

