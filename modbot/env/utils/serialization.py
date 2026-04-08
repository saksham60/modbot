"""Serialization helpers for API and script surfaces."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel


def to_serializable(data: BaseModel | dict[str, Any] | list[Any] | Any) -> Any:
    """Convert Pydantic models into plain Python data."""

    if isinstance(data, BaseModel):
        return data.model_dump(mode="json")
    if isinstance(data, list):
        return [to_serializable(item) for item in data]
    if isinstance(data, dict):
        return {key: to_serializable(value) for key, value in data.items()}
    return data
