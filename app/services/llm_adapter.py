from __future__ import annotations

from dataclasses import dataclass

from app.config import Settings
from app.core.safety import SafetyChecker


@dataclass(frozen=True)
class LLMResponse:
    text: str
    provider: str


class LLMAdapter:
    """Optional LLM integration stub.

    The default provider is "none"; this class never calls an external model unless a
    future implementation explicitly enables a provider after safety checking.
    """

    def __init__(self, settings: Settings, safety_checker: SafetyChecker | None = None) -> None:
        self.settings = settings
        self.safety_checker = safety_checker or SafetyChecker()

    async def generate_ctf_safe_hint(self, prompt: str) -> LLMResponse | None:
        if not self.settings.llm_enabled:
            return None

        safety = self.safety_checker.check(prompt)
        if not safety.allowed:
            return LLMResponse(text=safety.message, provider=self.settings.llm_provider)

        raise NotImplementedError(
            "LLM providers are intentionally stubbed. Future providers must return only "
            "conceptual, educational, CTF-safe hints after safety checking."
        )

