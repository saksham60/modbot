"""Deterministic grader for the medium task."""

from modbot.env.grader.base_grader import BaseGrader
from modbot.env.grader.metrics import action_accuracy, appeal_control, context_discipline, removal_precision, severe_violation_recall


class MediumTaskGrader(BaseGrader):
    """Rewards correct actioning plus disciplined context use."""

    def grade(self, state):
        components = {
            "action_accuracy": action_accuracy(state),
            "severe_violation_recall": severe_violation_recall(state),
            "removal_precision": removal_precision(state),
            "context_discipline": context_discipline(state),
            "appeal_control": appeal_control(state),
        }
        score = round(
            components["action_accuracy"] * 0.25
            + components["severe_violation_recall"] * 0.2
            + components["removal_precision"] * 0.2
            + components["context_discipline"] * 0.2
            + components["appeal_control"] * 0.15,
            4,
        )
        return score, components

