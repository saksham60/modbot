"""Dense reward engine for the moderation environment."""

from modbot.env.reward.reward_components import appeal_penalty, backlog_penalty, budget_penalty, weighted_flag, weighted_value
from modbot.env.utils.files import load_yaml_file, package_path


class RewardEngine:
    """Compute dense step rewards and their decomposition."""

    def __init__(self) -> None:
        reward_config = load_yaml_file(package_path("configs", "reward.yaml"))
        self.weights = reward_config["weights"]

    def compute(self, state, is_valid: bool, outcome) -> tuple[float, dict[str, float]]:
        """Return the total dense reward and its named components."""

        breakdown = {
            "valid_action": weighted_flag(is_valid, self.weights["valid_action"]),
            "relevant_context": weighted_value(outcome.relevant_context, self.weights["relevant_context"]),
            "moderation_correctness": weighted_value(
                outcome.decision_quality,
                self.weights["moderation_correctness"],
            ),
            "severe_violation_bonus": weighted_flag(
                outcome.severe_correct,
                self.weights["severe_violation_bonus"],
            ),
            "benign_preservation_bonus": weighted_flag(
                outcome.benign_preserved,
                self.weights["benign_preservation_bonus"],
            ),
            "queue_efficiency": weighted_value(
                outcome.queue_progress,
                self.weights["queue_efficiency"],
            ),
            "backlog_penalty": backlog_penalty(
                state.backlog_pressure,
                self.weights["backlog_penalty"],
            ),
            "appeal_penalty": appeal_penalty(
                outcome.appeal_delta,
                self.weights["appeal_penalty"],
            ),
            "trust_delta": weighted_value(
                outcome.trust_delta,
                self.weights["trust_delta"],
            ),
            "invalid_action": 0.0 if is_valid else round(self.weights["invalid_action"], 4),
            "redundant_action": weighted_flag(
                outcome.redundant,
                self.weights["redundant_action"],
            ),
            "wasted_budget": budget_penalty(
                outcome.budget_spent,
                outcome.wasted_budget,
                self.weights["wasted_budget"],
            ),
        }
        total = round(sum(breakdown.values()), 4)
        return total, breakdown

