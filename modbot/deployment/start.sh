#!/usr/bin/env bash
set -euo pipefail

export PORT="${PORT:-7860}"
export HOST="${HOST:-0.0.0.0}"

python -m modbot.app.ui.app
