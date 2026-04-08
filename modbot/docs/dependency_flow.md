# Dependency Flow

## Allowed Flow

```text
clients -> env.models
scripts -> clients -> env.core
app.ui -> app.ui.services -> app.api.deps -> env.core
app.api.routes -> app.api.deps -> env.core
env.core -> env.actions
env.core -> env.observation
env.core -> env.reward
env.core -> env.grader
env.core -> env.state
env.core -> env.tasks
env.actions -> env.models
env.actions -> env.state
env.observation -> env.models
env.observation -> env.state
env.reward -> env.models
env.reward -> env.state
env.grader -> env.models
env.grader -> env.state
env.tasks -> env.models
env.tasks -> env.utils
env.policy -> env.models
env.state -> env.models
env.state -> env.utils
```

## Rules

- UI must not import reward, grader, or raw task fixtures directly.
- API routes must not own environment logic.
- Reward code must not grade episodes.
- Graders must not shape per-step rewards.
- Observation builders must not mutate hidden state.
- Policy retrieval must stay independent from transition orchestration.
- Clients must not reach into hidden state internals.
