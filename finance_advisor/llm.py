from __future__ import annotations

from typing import Protocol

from finance_advisor.config import AppConfig


class LLMClient(Protocol):
    provider_name: str
    last_error: str | None

    def generate(self, system_prompt: str, user_prompt: str) -> str:
        ...


class RuleBasedLLM:
    """Fallback used when LangChain dependencies or GROQ_API_KEY are unavailable."""

    provider_name = "rule_based_fallback"
    last_error: str | None = None

    def generate(self, system_prompt: str, user_prompt: str) -> str:
        return ""


class GroqLangChainLLM:
    provider_name = "groq_via_langchain"

    def __init__(self, config: AppConfig) -> None:
        self.last_error: str | None = None
        if not config.groq_api_key:
            raise ValueError("GROQ_API_KEY is required for GroqLangChainLLM.")

        try:
            from langchain_core.messages import HumanMessage, SystemMessage
            from langchain_groq import ChatGroq
        except ImportError as exc:
            raise ImportError(
                "Install dependencies with `pip install -r requirements.txt` to use Groq through LangChain."
            ) from exc

        self._human_message = HumanMessage
        self._system_message = SystemMessage
        self._chat = ChatGroq(
            model=config.groq_model,
            api_key=config.groq_api_key,
            temperature=0.2,
            timeout=60,
        )

    def generate(self, system_prompt: str, user_prompt: str) -> str:
        try:
            response = self._chat.invoke(
                [
                    self._system_message(content=system_prompt),
                    self._human_message(content=user_prompt),
                ]
            )
            self.last_error = None
            return str(response.content).strip()
        except Exception as exc:
            self.last_error = f"{exc.__class__.__name__}: {exc}"
            return ""


def build_llm(config: AppConfig) -> LLMClient:
    if not config.use_llm or not config.groq_api_key:
        return RuleBasedLLM()
    try:
        return GroqLangChainLLM(config)
    except (ImportError, ValueError):
        return RuleBasedLLM()
