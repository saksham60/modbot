# Architecture Notes

## Separation of Concerns

ModBot is deliberately split into narrow modules.

- `env/models`: typed contracts for observations, actions, info, task config, scenarios, and state.
- `env/tasks`: deterministic scenario loading with seeded queue ordering.
- `env/state`: hidden runtime state, queue mutation, and platform metric updates.
- `env/actions`: semantic validation and action execution.
- `env/observation`: safe projection from hidden state to agent-visible observation.
- `env/reward`: dense reward shaping only.
- `env/grader`: deterministic end-of-episode scoring only.
- `env/core`: orchestration for reset, step, state, and done logic.
- `app/api`: environment session handling and HTTP endpoints.
- `app/ui`: Gradio moderation console.

## Main Flow

1. `TaskFactory` loads a scenario from `data/<difficulty>/`.
2. `initialize_hidden_state()` creates runtime report state and queue order.
3. `ObservationBuilder` produces the reset observation.
4. `TransitionEngine` validates an action, executes it, recomputes metrics, shapes reward, appends trajectory, checks done conditions, and calls the grader when appropriate.
5. API and UI layers interact with the same `ModBotEnv` contract.

## Hidden Truth Handling

The hidden truth fields live in scenario data and hidden state only. Observations and public state omit gold labels, harmfulness markers, and ambiguity annotations.

## Why `complete_case` Exists

Moderation decisions are separated from case finalization so the agent must explicitly commit to throughput. This makes queue management and backlog pressure part of the decision process instead of side effects hidden inside moderation actions.
