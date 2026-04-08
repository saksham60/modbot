"""In-memory environment session store."""

from __future__ import annotations

from dataclasses import dataclass
from uuid import uuid4

from modbot.env.core.environment import ModBotEnv


@dataclass
class SessionRecord:
    """Track an environment and its latest observation."""

    env: ModBotEnv
    observation: object


class SessionStore:
    """Manage multiple local environment sessions."""

    def __init__(self) -> None:
        self._sessions: dict[str, SessionRecord] = {}

    def create_session(self, task_id: str = "easy", seed: int | None = None):
        env = ModBotEnv(task_id=task_id, seed=seed)
        observation = env.reset(task_id=task_id, seed=seed)
        session_id = uuid4().hex[:12]
        self._sessions[session_id] = SessionRecord(env=env, observation=observation)
        return session_id, observation

    def has_session(self, session_id: str) -> bool:
        return session_id in self._sessions

    def active_session_count(self) -> int:
        return len(self._sessions)

    def _get_record(self, session_id: str) -> SessionRecord:
        if session_id not in self._sessions:
            raise KeyError(session_id)
        return self._sessions[session_id]

    def reset_session(self, session_id: str, task_id: str | None = None, seed: int | None = None):
        record = self._get_record(session_id)
        observation = record.env.reset(task_id=task_id, seed=seed)
        record.observation = observation
        return observation

    def step_session(self, session_id: str, action):
        record = self._get_record(session_id)
        observation, reward, done, info = record.env.step(action)
        record.observation = observation
        return observation, reward, done, info

    def observation(self, session_id: str):
        return self._get_record(session_id).observation

    def state(self, session_id: str):
        return self._get_record(session_id).env.state()
