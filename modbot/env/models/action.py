"""Typed action model for the sequential moderation environment."""

from pydantic import BaseModel, ConfigDict, model_validator

from modbot.env.models.config import ActionType


class ActionModel(BaseModel):
    """A single agent action submitted to the environment."""

    model_config = ConfigDict(str_strip_whitespace=True)

    action_type: ActionType
    report_id: str | None = None
    user_id: str | None = None
    policy_section: str | None = None
    notes: str | None = None

    @model_validator(mode="after")
    def validate_required_fields(self) -> "ActionModel":
        """Enforce action-specific required fields."""

        required_fields = {
            ActionType.REVIEW_REPORT: ("report_id",),
            ActionType.FETCH_USER_HISTORY: ("user_id",),
            ActionType.FETCH_THREAD_CONTEXT: ("report_id",),
            ActionType.FETCH_POLICY: ("policy_section",),
            ActionType.REMOVE_CONTENT: ("report_id",),
            ActionType.WARN_USER: ("report_id",),
            ActionType.ESCALATE_CASE: ("report_id",),
            ActionType.IGNORE_REPORT: ("report_id",),
            ActionType.COMPLETE_CASE: ("report_id",),
        }

        missing = [
            field_name
            for field_name in required_fields[self.action_type]
            if not getattr(self, field_name)
        ]
        if missing:
            fields = ", ".join(missing)
            raise ValueError(f"{self.action_type.value} requires: {fields}")
        return self
