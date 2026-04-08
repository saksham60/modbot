"""Base class for deterministic task graders."""

from abc import ABC, abstractmethod

from modbot.env.models.state import HiddenWorldStateModel


class BaseGrader(ABC):
    """Return a final task score and component breakdown."""

    @abstractmethod
    def grade(self, state: HiddenWorldStateModel) -> tuple[float, dict[str, float]]:
        """Return a deterministic score in the range [0.0, 1.0]."""
