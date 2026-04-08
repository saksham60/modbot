"""Deterministic grader for the easy task."""

from modbot.env.grader.base_grader import BaseGrader
from modbot.env.grader.metrics import action_accuracy, final_trust_score, queue_efficiency


class EasyTaskGrader(BaseGrader):
    """Prioritizes exact actions on clear-cut cases."""

    def grade(self, state):
        components = {
            "action_accuracy": action_accuracy(state),
            "queue_efficiency": queue_efficiency(state),
            "final_trust_score": final_trust_score(state),
        }
        score = round(
            components["action_accuracy"] * 0.7
            + components["queue_efficiency"] * 0.15
            + components["final_trust_score"] * 0.15,
            4,
        )
        return score, components

