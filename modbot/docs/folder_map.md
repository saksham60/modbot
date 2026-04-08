# Folder Map

## Root Files

- `README.md`: project overview and usage documentation.
- `pyproject.toml`: Python packaging, dependencies, and test config.
- `openenv.yaml`: OpenEnv-facing metadata and entrypoint declarations.

## Package Layout

- `modbot/app/ui`: Hugging Face Space UI and moderation console components.
- `modbot/app/api`: FastAPI server, routers, and environment session services.
- `modbot/env/core`: main environment class, episode lifecycle, and transition logic.
- `modbot/env/models`: typed Pydantic models for actions, observations, state, info, and task config.
- `modbot/env/tasks`: scenario loading, task-specific factories, and seeded task selection.
- `modbot/env/reward`: dense reward shaping and reward decomposition utilities.
- `modbot/env/grader`: deterministic end-of-episode graders returning a score in `[0.0, 1.0]`.
- `modbot/env/policy`: moderation policy catalog and retrieval helpers.
- `modbot/env/state`: hidden simulator state, queue bookkeeping, and platform metrics.
- `modbot/env/observation`: transforms hidden state into agent-visible observations.
- `modbot/env/actions`: action validation and execution helper logic.
- `modbot/env/utils`: seeding, serialization, ids, and lightweight logging helpers.
- `modbot/scripts`: baseline evaluation, simulation, and local run entrypoints.
- `modbot/configs`: environment, reward, and UI configuration files.
- `modbot/tests`: unit and integration tests.
- `modbot/data`: deterministic scenario fixtures for easy, medium, and hard tasks.
- `modbot/docs`: architecture and design notes.
- `modbot/deployment`: Docker and Hugging Face Spaces deployment assets.
- `modbot/examples`: sample actions, observations, and trajectories.
