# Task Design

## Easy Task

The easy task contains low-ambiguity moderation cases with deterministic labels.

- direct threat -> `remove_content`
- obvious scam spam -> `remove_content`
- benign criticism -> `ignore_report`
- low-severity insult -> `warn_user`

This task checks whether the agent can use the environment correctly without relying on extra context.

## Medium Task

The medium task introduces context dependence.

- sarcasm and satire can look abusive without thread context
- repeated harassment patterns may require user history
- public-harm misinformation should often be escalated rather than guessed at

The main failure modes are over-removal of benign speech and under-enforcement of patterned abuse.

## Hard Task

The hard task simulates a surge event.

- report counts spike
- brigading and false reports coexist with real abuse
- review budget is tight
- backlog pressure can end the episode early

The optimal policy is not to investigate every case equally. High-severity harms and coordinated false-report protection both matter.

## Seeded Determinism

Each task loads scenario fixtures from disk and applies deterministic seed-based tie-breaking to queue order. This supports reproducible evaluation while preserving task difficulty.
