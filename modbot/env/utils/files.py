"""Filesystem and config helpers for ModBot."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import yaml

PACKAGE_ROOT = Path(__file__).resolve().parents[2]
REPO_ROOT = PACKAGE_ROOT.parent


def package_path(*parts: str) -> Path:
    """Return an absolute path inside the package tree."""

    return PACKAGE_ROOT.joinpath(*parts)


def load_json_file(path: Path) -> Any:
    """Load JSON content from disk."""

    return json.loads(path.read_text(encoding="utf-8"))


def load_yaml_file(path: Path) -> dict[str, Any]:
    """Load YAML content from disk."""

    return yaml.safe_load(path.read_text(encoding="utf-8"))
