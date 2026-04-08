"""Hard task loader."""

from modbot.env.tasks.base import BaseTaskLoader


class HardTaskLoader(BaseTaskLoader):
    """Loads hard brigading surge scenarios."""

    data_subdir = "hard"
