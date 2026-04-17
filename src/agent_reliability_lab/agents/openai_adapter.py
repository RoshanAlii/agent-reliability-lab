from __future__ import annotations

import os
from typing import Any


def openai_mode_available() -> bool:
    return bool(os.getenv("OPENAI_API_KEY")) and os.getenv("ARL_USE_OPENAI", "0") == "1"


class OpenAIAgentRuntime:
    """Optional placeholder for a live OpenAI-backed implementation.

    This file is intentionally lightweight so the repo remains runnable without external services.
    Extend this class with the OpenAI Agents SDK or Responses API in your own environment.
    """

    def __init__(self, *_args: Any, **_kwargs: Any) -> None:
        if not openai_mode_available():
            raise RuntimeError("OpenAI mode not enabled. Set OPENAI_API_KEY and ARL_USE_OPENAI=1.")

    def run(self) -> dict[str, Any]:
        raise NotImplementedError(
            "Hook this adapter to the OpenAI Agents SDK / Responses API for live agent execution."
        )
