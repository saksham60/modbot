---
title: ModBot
emoji: "🛡️"
colorFrom: blue
colorTo: gray
sdk: docker
app_port: 7860
short_description: Stateful trust and safety simulator for RL agents.
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

The benchmark-compatible inference entrypoint is the repo-root `inference.py`.

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

## Multi-Mode Deployment Readiness

The repository includes the validator-facing files required for multi-mode deployment:

- repo-root `inference.py`
- repo-root `server/app.py`
- `[project.scripts].server` in `pyproject.toml`
- `openenv-core>=0.2.0`
- checked-in `uv.lock`

Useful commands:

```bash
uv lock
uv run server
```

## Environment Variables

The project supports an optional root `.env` file for local development.

```bash
cp .env.example .env
```

Runtime environment variables still take priority over `.env` values. This means local `.env` support does not interfere with Hugging Face Spaces, where configuration should still be set through Space Variables and Secrets.

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
uv run server
```

Key endpoints:

- `GET /health`
- `POST /reset`
- `POST /step`
- `GET /state`
- `GET /tasks`
- `POST /sessions`
- `POST /sessions/{session_id}/reset`
- `POST /sessions/{session_id}/step`
- `GET /sessions/{session_id}/state`

OpenEnv-compatible smoke test commands:

```bash
curl -X POST http://127.0.0.1:8000/reset -H "Content-Type: application/json" -d "{\"task_id\":\"easy\",\"seed\":7}"
curl -X POST http://127.0.0.1:8000/step -H "Content-Type: application/json" -d "{\"action_type\":\"review_report\",\"report_id\":\"easy-001\"}"
curl http://127.0.0.1:8000/state
```

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

## Benchmark Inference

The benchmark runner must be invoked from the repo root:

```bash
python inference.py
```

Required benchmark-facing environment variables:

- `API_BASE_URL`
- `MODEL_NAME`
- `HF_TOKEN`
- `LOCAL_IMAGE_NAME` or `IMAGE_NAME`

Optional ModBot controls:

- `MODBOT_TASK`
- `MODBOT_BENCHMARK`
- `MODBOT_MAX_STEPS`
- `MODBOT_SUCCESS_THRESHOLD`

## Docker

```bash
docker build -t modbot .
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

Manual verification checklist:

- confirm repo-root `inference.py` exists
- run `python inference.py`
- run `python -m modbot.app.api.server`
- verify `POST /reset`, `POST /step`, and `GET /state`
- run `python -m modbot.app.ui.app`
- verify the UI panels render with readable dark text

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
- `modbot/docs/testing.md`
- `modbot/docs/task_design.md`
- `modbot/docs/reward_design.md`
- `modbot/docs/grading_design.md`
- `modbot/docs/ui_design.md`
- `modbot/docs/structure_plan.md`
- `modbot/docs/file_responsibilities.md`
- `modbot/docs/dependency_flow.md`
