"""Thin benchmark entrypoint for the existing ModBot environment."""

from __future__ import annotations

import asyncio
import os

from openai import OpenAI

from clients.llm_client import LLMClientConfig, OpenAIActionClient
from modbot.env.utils.env import load_environment
from scripts.inference_runner import EpisodeResult, close_environment, create_environment, run_episode
from scripts.logging_utils import log_end, log_start

load_environment()


async def _main() -> None:
    api_key = os.getenv("HF_TOKEN") or os.getenv("API_KEY") or os.getenv("OPENAI_API_KEY") or "not-needed"
    api_base_url = (
        os.getenv("API_BASE_URL")
        or os.getenv("MODEL_BASE_URL")
        or "https://api.openai.com/v1"
    )
    model_name = os.getenv("MODEL_NAME", "gpt-4.1-mini")
    image_name = os.getenv("LOCAL_IMAGE_NAME") or os.getenv("IMAGE_NAME")
    configured_task = os.getenv("MODBOT_TASK")
    task_names = [configured_task] if configured_task else ["easy", "medium", "hard"]
    benchmark_name = os.getenv("MODBOT_BENCHMARK", "modbot")
    max_steps = int(os.getenv("MODBOT_MAX_STEPS", "64"))
    success_threshold = float(os.getenv("MODBOT_SUCCESS_THRESHOLD", "0.5"))
    timeout_seconds = float(os.getenv("MODEL_TIMEOUT_SECONDS", "30"))

    client = OpenAI(base_url=api_base_url, api_key=api_key)
    llm_client = OpenAIActionClient(
        client=client,
        config=LLMClientConfig(model_name=model_name, timeout_seconds=timeout_seconds),
    )
    for task_name in task_names:
        env = None
        result = EpisodeResult()

        try:
            log_start(task=task_name, env=benchmark_name, model=model_name)
            env = create_environment(task_name=task_name, image_name=image_name)
            result = await run_episode(
                env=env,
                llm_client=llm_client,
                task_name=task_name,
                max_steps=max_steps,
                success_threshold=success_threshold,
            )
        except BaseException:  # noqa: BLE001 - benchmark wrapper must always emit parseable output
            result = EpisodeResult()
        finally:
            try:
                if env is not None:
                    await close_environment(env)
            finally:
                log_end(
                    success=result.success,
                    steps=result.steps,
                    score=result.score,
                    rewards=result.rewards,
                )


if __name__ == "__main__":
    asyncio.run(_main())
