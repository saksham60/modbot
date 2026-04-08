---
title: ModBot
emoji: "🛡️"
colorFrom: blue
colorTo: gray
sdk: docker
app_port: 7860
short_description: Stateful trust and safety moderation simulator for RL agents.
---

# ModBot: Trust & Safety Policy Simulator

ModBot is a production-style, OpenEnv-compatible trust and safety environment built as a sequential RL simulator rather than a static classifier. An agent operates a fictional moderation queue, explicitly reviews cases, fetches context, consults policy, chooses moderation actions, and manages limited review capacity while platform metrics evolve over time.

## Why This Project

Real moderation work is operational, sequential, and resource-constrained. A useful benchmark needs hidden world state, queue pressure, appeals, trust dynamics, action costs, and delayed consequences. ModBot models that process directly.

## RL Framing

Each episode is a moderation shift.

- Observation: visible report data, queue snapshot, fetched context, remaining review budget, visible platform metrics, and allowed actions.
- Hidden state: gold policy truth, ambiguity, harmfulness, brigading signals, full user history, thread context, and runtime case state.
- Action: inspect, fetch context, consult policy, decide moderation, or finalize a case.
- Transition: actions mutate queue status, budget, trust, appeal pressure, backlog pressure, and future observations.
- Dense reward: stepwise shaping encourages correct handling, useful context fetches, efficient queue management, and budget discipline.
- Final grade: deterministic task-specific scorer returns a reproducible value in `[0.0, 1.0]`.

## OpenEnv Compatibility

ModBot exposes the standard environment interface:

- `reset(task_id=None, seed=None) -> ObservationModel`
- `step(action) -> (ObservationModel, reward, done, StepInfoModel)`
- `state() -> EnvironmentStateModel`
- `grade() -> (score, components)`

Metadata is declared in `openenv.yaml`.

## Project Layout

```text
modbot/
  app/
    api/
      routes/
    ui/
      components/
      pages/
      services/
  env/
    core/
    models/
    tasks/
    reward/
    grader/
    policy/
    state/
    observation/
    actions/
    utils/
  scripts/
  clients/
  configs/
  tests/
  data/
    easy/
    medium/
    hard/
  docs/
  deployment/
  examples/
```

## Action Space

Supported typed actions:

- `review_report`
- `fetch_user_history`
- `fetch_thread_context`
- `fetch_policy`
- `remove_content`
- `warn_user`
- `escalate_case`
- `ignore_report`
- `complete_case`

The Pydantic `ActionModel` enforces action-specific required fields such as `report_id`, `user_id`, or `policy_section`.

## Observation Space

Each observation contains:

- task id and step number
- current active report or queue snapshot
- allowed actions
- fetched user history, thread context, and policy snippets
- remaining review budget
- visible metrics: trust, appeals, backlog, pending queue depth, completed cases
- recent trajectory summary

Hidden labels are not exposed.

## Tasks

### Easy: Clear-Cut Violations

- obvious harmful content and obvious benign cases
- deterministic labels
- low ambiguity
- objective: exact moderation actions

### Medium: Contextual Moderation

- sarcasm, satire, harassment patterns, and public-harm ambiguity
- context fetches matter
- objective: avoid both over-removal and under-enforcement

### Hard: Brigading Surge

- coordinated false reports mixed with genuine abuse
- limited review budget
- backlog pressure and queue collapse risk
- objective: optimize long-term platform health under operational stress

## Reward Design

Dense shaping components include:

- correct moderation action quality
- severe-violation bonuses
- benign-preservation bonuses
- relevant context fetch bonuses
- queue-efficiency bonuses
- invalid-action penalties
- redundant-action penalties
- wasted-budget penalties
- backlog-pressure penalties
- trust and appeal deltas

The reward function is separate from the final graders. See `modbot/docs/reward_design.md`.

## Deterministic Final Grading

Task-specific graders compute weighted final scores using combinations of:

- action accuracy
- severe-violation recall
- removal precision
- context discipline
- queue efficiency
- final trust score
- appeal control
- backlog control

## Quick Start

```bash
python -m venv .venv
. .venv/Scripts/activate
pip install -e .[dev]
python -m modbot.scripts.demo_rollout easy --seed 7
```

## Baseline Evaluation

The baseline evaluator supports a deterministic heuristic client by default and an OpenAI-compatible HTTP client through environment variables.

```bash
python -m modbot.scripts.eval --seed 7
```

Environment variables:

- `MODEL_BACKEND=heuristic|openai_compatible|huggingface`
- `MODEL_NAME=<provider model name>`
- `MODEL_BASE_URL=<OpenAI-compatible base URL>`
- `MODEL_API_KEY=<api key>`
- `HF_TOKEN=<compatibility fallback for MODEL_API_KEY>`
- `OPENAI_API_KEY=<secondary compatibility fallback>`

Example output from the local heuristic baseline:

```json
{
  "aggregate_score": 0.7919,
  "results": [
    {"task_id": "easy", "score": 0.7912},
    {"task_id": "medium", "score": 0.8399},
    {"task_id": "hard", "score": 0.7446}
  ]
}
```

## API Server

```bash
python -m modbot.app.api.server
```

Key endpoints:

- `GET /health`
- `GET /tasks`
- `POST /sessions`
- `POST /sessions/{session_id}/reset`
- `POST /sessions/{session_id}/step`
- `GET /sessions/{session_id}/state`

## UI Demo

```bash
python -m modbot.app.ui.app
```

The UI is a moderation console with:

- top bar and task selector
- queue panel
- current report panel
- context panel
- action panel
- metrics strip
- trajectory log
- episode summary

## Docker

```bash
docker build -f modbot/deployment/Dockerfile -t modbot .
docker run --rm -p 7860:7860 modbot
```

The Docker image launches the Gradio UI on port `7860` by default.

## Hugging Face Spaces

This repository is prepared for Docker-based Spaces deployment.

- use `modbot/deployment/Dockerfile`
- the startup command is `bash modbot/deployment/start.sh`
- expose port `7860`
- set optional model credentials such as `HF_TOKEN` in the Space secrets panel

## Testing

```bash
pytest
```

The test suite covers:

- reset correctness
- step transitions
- invalid action penalties
- seed determinism
- grader reproducibility
- reward shaping
- task loading
- API smoke tests
- UI smoke tests when Gradio is installed

## Additional Docs

- `modbot/docs/architecture.md`
- `modbot/docs/task_design.md`
- `modbot/docs/reward_design.md`
- `modbot/docs/grading_design.md`
- `modbot/docs/ui_design.md`
- `modbot/docs/structure_plan.md`
- `modbot/docs/file_responsibilities.md`
- `modbot/docs/dependency_flow.md`
