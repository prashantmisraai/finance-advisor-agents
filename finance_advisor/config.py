from __future__ import annotations

import os
from dataclasses import dataclass


@dataclass(frozen=True)
class AppConfig:
    groq_api_key: str | None
    groq_model: str
    use_llm: bool


def load_config() -> AppConfig:
    api_key = os.getenv("GROQ_API_KEY")
    return AppConfig(
        groq_api_key=api_key,
        groq_model=os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile"),
        use_llm=os.getenv("USE_LLM", "true").lower() not in {"0", "false", "no"},
    )
