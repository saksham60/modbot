"""Policy retrieval helpers."""

from modbot.env.models.config import PolicySnippetModel
from modbot.env.policy.policy_store import POLICY_CATALOG


def get_policy_snippet(section: str) -> PolicySnippetModel | None:
    """Return a policy snippet by section name."""

    return POLICY_CATALOG.get(section)


def is_known_policy_section(section: str) -> bool:
    """Return whether a policy section exists in the catalog."""

    return section in POLICY_CATALOG


def list_policy_sections() -> list[str]:
    """List policy section identifiers."""

    return sorted(POLICY_CATALOG)

