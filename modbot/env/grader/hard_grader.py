"""Deterministic grader for the hard task."""

from modbot.env.grader.base_grader import BaseGrader
from modbot.env.grader.metrics import backlog_control, final_trust_score, queue_efficiency, removal_precision, severe_violation_recall


class HardTaskGrader(BaseGrader):
    """Rewards platform-health optimization under queue pressure."""

    def grade(self, state):
        components = {
            "severe_violation_recall": severe_violation_recall(state),
            "removal_precision": removal_precision(state),
            "queue_efficiency": queue_efficiency(state),
            "final_trust_score": final_trust_score(state),
            "backlog_control": backlog_control(state),
        }
        score = round(
            components["severe_violation_recall"] * 0.3
            + components["removal_precision"] * 0.2
            + components["queue_efficiency"] * 0.2
            + components["final_trust_score"] * 0.15
            + components["backlog_control"] * 0.15,
            4,
        )
        return score, components

