"""Easy task loader."""

from modbot.env.tasks.base import BaseTaskLoader


class EasyTaskLoader(BaseTaskLoader):
    """Loads easy clear-cut moderation scenarios."""

    data_subdir = "easy"
