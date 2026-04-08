"""Violation categories and policy-section mappings."""

POLICY_CATEGORY_MAP: dict[str, str] = {
    "ABUSE-1": "harassment_or_threats",
    "SATIRE-1": "satire_and_context",
    "SPAM-1": "spam_and_scams",
    "DOGPILE-3": "brigading_and_false_reports",
    "SELF-HARM-ESC": "crisis_escalation",
    "MISINFO-2": "public_harm_misinformation",
}


def policy_category(section: str) -> str:
    """Return a normalized category label for a policy section."""

    return POLICY_CATEGORY_MAP.get(section, "unknown")
