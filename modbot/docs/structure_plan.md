# Planned Folder Tree

```text
modbot/
├── app/
│   ├── api/
│   │   ├── routes/
│   │   ├── server.py
│   │   └── deps.py
│   └── ui/
│       ├── components/
│       ├── pages/
│       ├── services/
│       └── app.py
├── env/
│   ├── core/
│   │   ├── environment.py
│   │   ├── episode_manager.py
│   │   └── transition_engine.py
│   ├── models/
│   │   ├── action.py
│   │   ├── observation.py
│   │   ├── state.py
│   │   ├── info.py
│   │   └── config.py
│   ├── tasks/
│   │   ├── task_factory.py
│   │   ├── easy_task.py
│   │   ├── medium_task.py
│   │   └── hard_task.py
│   ├── reward/
│   │   ├── reward_engine.py
│   │   └── reward_components.py
│   ├── grader/
│   │   ├── base_grader.py
│   │   ├── easy_grader.py
│   │   ├── medium_grader.py
│   │   └── hard_grader.py
│   ├── policy/
│   │   ├── policy_store.py
│   │   ├── categories.py
│   │   └── retrieval.py
│   ├── state/
│   │   ├── state_manager.py
│   │   ├── queue_manager.py
│   │   ├── trust_manager.py
│   │   └── appeal_manager.py
│   ├── observation/
│   │   └── builder.py
│   ├── actions/
│   │   ├── validator.py
│   │   └── executor.py
│   └── utils/
│       ├── seeds.py
│       ├── logging.py
│       └── serialization.py
├── scripts/
│   ├── eval.py
│   ├── local_run.py
│   └── demo_rollout.py
├── clients/
│   ├── llm_client.py
│   └── prompt_builder.py
├── configs/
│   ├── env.yaml
│   ├── reward.yaml
│   ├── tasks.yaml
│   └── ui.yaml
├── data/
│   ├── easy/
│   ├── medium/
│   └── hard/
├── deployment/
│   ├── Dockerfile
│   ├── start.sh
│   └── hf_space_notes.md
├── tests/
│   ├── test_env.py
│   ├── test_reward.py
│   ├── test_graders.py
│   ├── test_tasks.py
│   └── test_api.py
├── docs/
│   ├── architecture.md
│   ├── reward_design.md
│   ├── grading_design.md
│   └── ui_design.md
├── examples/
│   ├── sample_observation.json
│   ├── sample_action.json
│   └── sample_trajectory.json
├── openenv.yaml
├── README.md
├── requirements.txt
└── pyproject.toml
```
