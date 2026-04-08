"""Small reward shaping helpers."""


def weighted_flag(flag: bool, weight: float) -> float:
    """Return a fixed weighted value when a condition holds."""

    return round(weight if flag else 0.0, 4)


def weighted_value(value: float, weight: float) -> float:
    """Scale a value by its reward weight."""

    return round(value * weight, 4)


def backlog_penalty(current_backlog: float, weight: float) -> float:
    """Convert backlog pressure into a penalty."""

    return round((current_backlog / 100.0) * weight, 4)


def appeal_penalty(appeal_delta: float, weight: float) -> float:
    """Penalize increases in appeal pressure."""

    return round(max(appeal_delta, 0.0) / 5.0 * weight, 4)


def budget_penalty(budget_spent: int, wasted_budget: float, weight: float) -> float:
    """Penalize costly or wasteful investigation steps."""

    return round(weight * ((budget_spent * 0.5) + wasted_budget), 4)
