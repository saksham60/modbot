# Testing Guide

## Local Setup

```bash
python -m venv .venv
. .venv/Scripts/activate
pip install -e .[dev]
uv lock
```

## Root Benchmark Inference

The benchmark entrypoint is the repo-root `inference.py`.

Check that it exists:

```bash
python -c "from pathlib import Path; print(Path('inference.py').is_file())"
```

Run it with local defaults:

```bash
python inference.py
```

Run it with explicit benchmark variables:

```bash
set MODBOT_TASK=easy
set MODBOT_BENCHMARK=modbot
set MODBOT_MAX_STEPS=64
set MODBOT_SUCCESS_THRESHOLD=0.5
set MODEL_NAME=gpt-4.1-mini
set API_BASE_URL=https://api.openai.com/v1
python inference.py
```

Check the required validator files:

```bash
python -c "from pathlib import Path; print(Path('uv.lock').is_file())"
python -c "from pathlib import Path; print(Path('server/app.py').is_file())"
```

## API Smoke Tests

Start the API:

```bash
python -m modbot.app.api.server
uv run server
```

Health:

```bash
curl http://127.0.0.1:8000/health
```

OpenEnv reset:

```bash
curl -X POST http://127.0.0.1:8000/reset ^
  -H "Content-Type: application/json" ^
  -d "{\"task_id\":\"easy\",\"seed\":7}"
```

OpenEnv step:

```bash
curl -X POST http://127.0.0.1:8000/step ^
  -H "Content-Type: application/json" ^
  -d "{\"action_type\":\"review_report\",\"report_id\":\"easy-001\"}"
```

OpenEnv state:

```bash
curl http://127.0.0.1:8000/state
```

Session API flow:

```bash
curl -X POST http://127.0.0.1:8000/sessions ^
  -H "Content-Type: application/json" ^
  -d "{\"task_id\":\"easy\",\"seed\":7}"
```

## UI Smoke Test

```bash
python -m modbot.app.ui.app
```

Then verify:

- the task selector renders
- metrics cards use dark readable text
- `Reset Episode` refreshes the queue
- manual `Step Action` does not crash on blank optional fields
- `Auto-Run Baseline` completes an episode

## Pytest

Run the test suite:

```bash
pytest
```

Focused API regression:

```bash
pytest modbot/tests/test_api.py -q
```
