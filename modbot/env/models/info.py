"""Step info and reward decomposition models."""

from typing import Any

from pydantic import BaseModel, Field


class StepInfoModel(BaseModel):
    """Auxiliary info returned by each environment step."""

    valid_action: bool
    message: str
    reward: float
    reward_breakdown: dict[str, float] = Field(default_factory=dict)
    budget_spent: int = 0
    done_reason: str | None = None
    final_score: float | None = None
    grader_components: dict[str, float] = Field(default_factory=dict)
    state_summary: dict[str, Any] = Field(default_factory=dict)
