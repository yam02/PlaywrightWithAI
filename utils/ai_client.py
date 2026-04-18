"""Anthropic-backed locator repair — returns ranked replacement selectors from live DOM."""
from __future__ import annotations

import os
from typing import List, Optional

from utils.logger import get_logger

log = get_logger("ai_client")

_MODEL = "claude-opus-4-7"
_MAX_DOM_CHARS = 40_000
_MAX_TOKENS = 1024

_SYSTEM_PROMPT = (
    "You are a senior Playwright test-automation engineer specializing in repairing broken locators.\n"
    "The user will describe an element by its intent and provide a truncated HTML snapshot of the live page.\n"
    "Return between 3 and 6 Playwright-compatible CSS or text selectors that uniquely match the intended element,\n"
    "ranked from most to least likely. Prefer in this order: data-qa / data-testid, stable id, role + accessible name,\n"
    "unique text via :has-text(...), attribute combinations. Avoid brittle absolute XPath or nth-child selectors\n"
    "unless nothing else is unique. Each selector must resolve to exactly one element."
)


class _Suggestion:
    """Lightweight stand-in when Anthropic SDK/key is unavailable."""

    def __init__(self, selectors: List[str], reasoning: str = "") -> None:
        self.selectors = selectors
        self.reasoning = reasoning


class AILocatorHealer:
    """Suggests replacement Playwright selectors for a broken locator."""

    def __init__(self, api_key: Optional[str] = None) -> None:
        self._client = None
        self._model_cls = None
        self._api_key = api_key or os.getenv("ANTHROPIC_API_KEY")

        if not self._api_key:
            log.warning("ANTHROPIC_API_KEY not set — AI healing disabled, cached fallbacks only.")
            return

        try:
            from anthropic import Anthropic
            from pydantic import BaseModel, Field

            class HealingSuggestion(BaseModel):
                selectors: List[str] = Field(
                    description="3-6 Playwright-compatible selectors, ranked best-first.",
                )
                reasoning: str = Field(
                    default="",
                    description="One-sentence justification for the top pick.",
                )

            self._client = Anthropic(api_key=self._api_key)
            self._model_cls = HealingSuggestion
        except ImportError as exc:
            log.warning("Anthropic SDK not installed (%s) — AI healing disabled.", exc)
        except Exception as exc:  # noqa: BLE001
            log.warning("Failed to initialize Anthropic client: %s", exc)

    @property
    def enabled(self) -> bool:
        return self._client is not None and self._model_cls is not None

    def suggest(self, description: str, dom: str, exclude: Optional[List[str]] = None) -> List[str]:
        """Ask Claude for replacement selectors. Returns [] on failure or when disabled."""
        if not self.enabled:
            return []

        exclude = exclude or []
        trimmed = dom[:_MAX_DOM_CHARS]
        if len(dom) > _MAX_DOM_CHARS:
            trimmed += "\n<!-- truncated -->"

        exclusion_block = ""
        if exclude:
            joined = "\n".join(f"- {sel}" for sel in exclude)
            exclusion_block = f"\n\nDo NOT suggest any of these already-tried selectors:\n{joined}"

        user_prompt = (
            f"Element intent: {description}\n"
            f"Suggest Playwright selectors that uniquely match this element in the HTML below.{exclusion_block}\n\n"
            f"--- HTML SNAPSHOT START ---\n{trimmed}\n--- HTML SNAPSHOT END ---"
        )

        try:
            response = self._client.messages.parse(
                model=_MODEL,
                max_tokens=_MAX_TOKENS,
                thinking={"type": "adaptive"},
                system=_SYSTEM_PROMPT,
                messages=[{"role": "user", "content": user_prompt}],
                response_model=self._model_cls,
            )
            suggestion = response.parsed
            log.info("AI healer suggested %d selector(s): %s", len(suggestion.selectors), suggestion.reasoning)
            return [s.strip() for s in suggestion.selectors if s and s.strip()]
        except Exception as exc:  # noqa: BLE001
            log.warning("AI healer call failed: %s", exc)
            return []


_singleton: Optional[AILocatorHealer] = None


def get_healer() -> AILocatorHealer:
    global _singleton
    if _singleton is None:
        _singleton = AILocatorHealer()
    return _singleton
