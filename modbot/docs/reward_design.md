# Reward Design

## Dense Reward Principles

The reward function is designed for learning signal, not final grading.

Positive signal:

- recording a more correct moderation decision
- correctly preserving benign content
- correctly handling severe violations
- fetching context that is actually relevant to ambiguous cases
- completing cases and reducing queue pressure
- improving community trust

Negative signal:

- invalid actions
- redundant actions
- irrelevant or repeated context fetches
- missed harmful content
- false removals and over-enforcement
- increasing appeal pressure
- growing backlog pressure
- burning review budget inefficiently

## Why Reward and Grade Are Separate

Dense rewards help an RL agent learn incremental behaviors. Final graders judge episode-level outcomes such as recall, precision, trust, and queue efficiency. Keeping them separate avoids overfitting the task score to a single shaping function.

## Interpreting Reward Breakdown

Each step returns a decomposition in `info.reward_breakdown` with stable keys:

- `valid_action`
- `relevant_context`
- `moderation_correctness`
- `severe_violation_bonus`
- `benign_preservation_bonus`
- `queue_efficiency`
- `backlog_penalty`
- `appeal_penalty`
- `trust_delta`
- `invalid_action`
- `redundant_action`
- `wasted_budget`

This makes it practical to debug reward hacking and reward balance problems.
