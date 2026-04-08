# File Responsibilities

## Application Layer

- `app/api/server.py`: FastAPI app bootstrap and router registration.
- `app/api/deps.py`: shared API dependencies such as the session store.
- `app/api/routes/`: HTTP endpoints for `reset`, `step`, `state`, and health/task discovery.
- `app/ui/app.py`: Gradio app bootstrap and top-level event wiring.
- `app/ui/components/`: pure UI formatting and reusable rendering helpers.
- `app/ui/pages/`: console page layout and visual composition.
- `app/ui/services/`: adapter layer between UI events and environment sessions.

## Environment Layer

- `env/core/environment.py`: public `ModBotEnv` interface and environment orchestration.
- `env/core/episode_manager.py`: done logic and episode lifecycle control.
- `env/core/transition_engine.py`: validation, execution, reward, grading, and observation refresh per step.
- `env/models/action.py`: typed action schema and action-specific field validation.
- `env/models/observation.py`: agent-visible observation schema only.
- `env/models/state.py`: hidden runtime state plus public state projection models.
- `env/models/info.py`: per-step info and reward decomposition schema.
- `env/models/config.py`: enums, task config, policy snippets, report scenario/config types.
- `env/tasks/task_factory.py`: task routing and seeded scenario construction.
- `env/tasks/easy_task.py`: easy-task fixture loading.
- `env/tasks/medium_task.py`: medium-task fixture loading.
- `env/tasks/hard_task.py`: hard-task fixture loading.
- `env/reward/reward_engine.py`: dense reward aggregation.
- `env/reward/reward_components.py`: low-level reward helper functions.
- `env/grader/base_grader.py`: deterministic grader interface.
- `env/grader/easy_grader.py`: easy-task grading policy.
- `env/grader/medium_grader.py`: medium-task grading policy.
- `env/grader/hard_grader.py`: hard-task grading policy.
- `env/policy/policy_store.py`: canonical policy catalog.
- `env/policy/categories.py`: violation-category constants and mappings.
- `env/policy/retrieval.py`: policy lookup helpers.
- `env/state/state_manager.py`: hidden state initialization and public-state projection.
- `env/state/queue_manager.py`: queue activation/completion/snapshot helpers.
- `env/state/trust_manager.py`: trust and backlog computations.
- `env/state/appeal_manager.py`: appeal pressure and case impact helpers.
- `env/observation/builder.py`: hidden-state to observation transformation.
- `env/actions/validator.py`: invalid/redundant action checks and budget checks.
- `env/actions/executor.py`: state mutations for valid actions.
- `env/utils/seeds.py`: deterministic seed handling.
- `env/utils/logging.py`: logger creation.
- `env/utils/serialization.py`: model-to-JSON-safe serialization.

## Runtime Surfaces

- `scripts/eval.py`: multi-task evaluation loop against a model client.
- `scripts/local_run.py`: local UI entrypoint.
- `scripts/demo_rollout.py`: simple scripted rollout for demos and debugging.
- `clients/llm_client.py`: model client abstraction and provider compatibility layer.
- `clients/prompt_builder.py`: observation-to-prompt conversion.

## Support Assets

- `configs/*.yaml`: environment, reward, task, and UI configuration.
- `data/*/*.json`: deterministic seeded task fixtures.
- `deployment/Dockerfile`: container build for local use and Hugging Face Spaces.
- `deployment/start.sh`: runtime startup entrypoint.
- `deployment/hf_space_notes.md`: HF deployment notes.
- `tests/*.py`: grouped test suites by subsystem.
- `docs/*.md`: architecture and design notes.
- `examples/*.json`: reference payloads for observation/action/trajectory formats.
