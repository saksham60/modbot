"""Static moderation policy catalog for the simulator."""

from modbot.env.models.config import PolicySnippetModel

POLICY_CATALOG: dict[str, PolicySnippetModel] = {
    "ABUSE-1": PolicySnippetModel(
        section="ABUSE-1",
        title="Direct Abuse and Harassment",
        summary="Remove direct threats, slurs, or targeted dehumanizing attacks. Warn borderline personal attacks.",
        recommended_actions=["remove_content", "warn_user"],
        escalation_threshold="Escalate when coordinated or cross-thread.",
        notes="Satire and reclaimed language require context before enforcement.",
    ),
    "SATIRE-1": PolicySnippetModel(
        section="SATIRE-1",
        title="Satire and Contextual Speech",
        summary="Do not remove satirical or quoted content without reviewing surrounding thread context and target intent.",
        recommended_actions=["ignore_report", "escalate_case"],
        escalation_threshold="Escalate when context remains ambiguous after review.",
        notes="Context lookup is explicitly encouraged for ambiguous speech.",
    ),
    "SPAM-1": PolicySnippetModel(
        section="SPAM-1",
        title="Spam and Promotional Manipulation",
        summary="Remove coordinated spam, scam links, and repetitive commercial deception.",
        recommended_actions=["remove_content", "warn_user"],
        escalation_threshold="Escalate only when linked to broader abuse networks.",
        notes="Fresh accounts with repeated removals should generally be warned or escalated.",
    ),
    "DOGPILE-3": PolicySnippetModel(
        section="DOGPILE-3",
        title="Brigading and Coordinated Reporting",
        summary="Avoid actioning content solely due to mass reports. Investigate coordination signals and thread history.",
        recommended_actions=["ignore_report", "escalate_case"],
        escalation_threshold="Escalate when a reporting surge appears coordinated or platform-wide.",
        notes="Queue pressure should not justify shortcut removals.",
    ),
    "SELF-HARM-ESC": PolicySnippetModel(
        section="SELF-HARM-ESC",
        title="Crisis and Immediate Safety Escalation",
        summary="Escalate imminent self-harm, credible threats, or emergency risks to specialized review.",
        recommended_actions=["escalate_case"],
        escalation_threshold="Always escalate when imminent risk is present.",
        notes="Removing content alone is insufficient for crisis cases.",
    ),
    "MISINFO-2": PolicySnippetModel(
        section="MISINFO-2",
        title="Misleading Context and Public Harm",
        summary="Escalate ambiguous public-harm claims and remove clearly harmful coordinated misinformation.",
        recommended_actions=["escalate_case", "remove_content"],
        escalation_threshold="Escalate when intent and impact remain uncertain.",
        notes="Historical behavior and thread cues are important in borderline cases.",
    ),
}

