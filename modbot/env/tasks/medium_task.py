"""Medium task loader."""

from modbot.env.tasks.base import BaseTaskLoader


class MediumTaskLoader(BaseTaskLoader):
    """Loads medium contextual moderation scenarios."""

    data_subdir = "medium"
