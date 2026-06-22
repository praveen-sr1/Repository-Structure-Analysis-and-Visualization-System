"""AI explanation service.

Provider-agnostic wrapper around OpenAI and Google Gemini. The service builds a
prompt asking the model to explain a source file in plain English and returns
the text. When no provider/key is configured it reports that AI is unavailable
rather than fabricating a summary.

All network calls go through :mod:`httpx`. Provider selection and credentials
come from application settings.
"""
from __future__ import annotations

from dataclasses import dataclass

import httpx

from app.config import Settings, settings


class AIServiceError(RuntimeError):
    """Raised when an AI provider call fails."""


@dataclass(slots=True)
class AIResult:
    """The outcome of an AI explanation request."""

    summary: str
    provider: str
    model: str
    available: bool = True


_SYSTEM_PROMPT = (
    "You are a senior software engineer helping a developer understand an "
    "unfamiliar codebase. Explain what the given code does in 3 simple "
    "sentences, in clear plain English. Focus on the file's overall purpose "
    "and its most important behaviour. Do not repeat the code verbatim and do "
    "not exceed three sentences."
)


def _build_user_prompt(file_path: str, language: str, content: str) -> str:
    return (
        "Explain what this code does in 3 simple sentences.\n\n"
        f"File path: {file_path}\n"
        f"Language: {language}\n\n"
        f"Source:\n```{language}\n{content}\n```"
    )


class AIService:
    """Generates natural-language explanations of source files."""

    def __init__(self, config: Settings | None = None) -> None:
        self._settings = config or settings
        self._timeout = httpx.Timeout(60.0, connect=10.0)

    @property
    def provider(self) -> str:
        return self._settings.ai_provider.lower()

    @property
    def available(self) -> bool:
        return self._settings.ai_enabled

    def explain_file(self, *, file_path: str, language: str, content: str) -> AIResult:
        """Generate an explanation for a file's contents.

        Returns an :class:`AIResult` with ``available=False`` when no provider is
        configured. Raises :class:`AIServiceError` if a configured provider call
        fails.
        """
        if not self.available:
            return AIResult(
                summary=(
                    "AI explanations are not configured. Set AI_PROVIDER and the "
                    "matching API key (OPENAI_API_KEY or GEMINI_API_KEY) to enable "
                    "natural-language file summaries."
                ),
                provider="none",
                model="",
                available=False,
            )

        # Cap content sent to the model to keep requests bounded.
        trimmed = self._trim_content(content)
        prompt = _build_user_prompt(file_path, language, trimmed)

        if self.provider == "openai":
            return self._explain_openai(prompt)
        if self.provider == "gemini":
            return self._explain_gemini(prompt)
        raise AIServiceError(f"Unsupported AI provider: {self.provider!r}")

    # ------------------------------------------------------------------ #
    # Providers
    # ------------------------------------------------------------------ #
    def _explain_openai(self, prompt: str) -> AIResult:
        model = self._settings.openai_model
        url = "https://api.openai.com/v1/chat/completions"
        headers = {"Authorization": f"Bearer {self._settings.openai_api_key}"}
        payload = {
            "model": model,
            "messages": [
                {"role": "system", "content": _SYSTEM_PROMPT},
                {"role": "user", "content": prompt},
            ],
            "max_tokens": self._settings.ai_max_tokens,
            "temperature": self._settings.ai_temperature,
        }
        data = self._post_json(url, headers=headers, json=payload)
        try:
            text = data["choices"][0]["message"]["content"].strip()
        except (KeyError, IndexError, TypeError) as exc:
            raise AIServiceError("Unexpected OpenAI response shape.") from exc
        return AIResult(summary=text, provider="openai", model=model)

    def _explain_gemini(self, prompt: str) -> AIResult:
        model = self._settings.gemini_model
        url = (
            f"https://generativelanguage.googleapis.com/v1beta/models/"
            f"{model}:generateContent"
        )
        params = {"key": self._settings.gemini_api_key}
        payload = {
            "system_instruction": {"parts": [{"text": _SYSTEM_PROMPT}]},
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {
                "maxOutputTokens": self._settings.ai_max_tokens,
                "temperature": self._settings.ai_temperature,
            },
        }
        data = self._post_json(url, params=params, json=payload)
        try:
            text = data["candidates"][0]["content"]["parts"][0]["text"].strip()
        except (KeyError, IndexError, TypeError) as exc:
            raise AIServiceError("Unexpected Gemini response shape.") from exc
        return AIResult(summary=text, provider="gemini", model=model)

    # ------------------------------------------------------------------ #
    # Helpers
    # ------------------------------------------------------------------ #
    def _post_json(self, url: str, **kwargs: object) -> dict:
        try:
            with httpx.Client(timeout=self._timeout) as client:
                response = client.post(url, **kwargs)  # type: ignore[arg-type]
                response.raise_for_status()
                return response.json()
        except httpx.HTTPStatusError as exc:
            status_code = exc.response.status_code
            # Give the most common failures friendly, actionable messages.
            if status_code == 429:
                raise AIServiceError(
                    "AI rate limit or quota exceeded (HTTP 429). Your provider "
                    "key has hit its request quota — wait a moment and retry, or "
                    "check your plan/billing and rate limits."
                ) from exc
            if status_code in (401, 403):
                raise AIServiceError(
                    "AI authentication failed (HTTP "
                    f"{status_code}). Check that your API key is valid and the "
                    "API is enabled for your project."
                ) from exc
            detail = exc.response.text[:300]
            raise AIServiceError(
                f"AI provider returned {status_code}: {detail}"
            ) from exc
        except httpx.HTTPError as exc:
            raise AIServiceError(f"AI provider request failed: {exc}") from exc

    def _trim_content(self, content: str, *, max_chars: int = 12_000) -> str:
        """Bound the source sent to the model; note truncation if applied."""
        if len(content) <= max_chars:
            return content
        return content[:max_chars] + "\n\n/* … file truncated for summarisation … */"
