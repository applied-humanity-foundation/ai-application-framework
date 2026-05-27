"""OpenAI-compatible provider using raw httpx requests.

Talks directly to the OpenAI Chat Completions API without pulling in the
``openai`` Python package, keeping the dependency tree minimal.
"""

from __future__ import annotations

import json
from typing import Any, AsyncIterator

import httpx

from ahf_ai.providers.base import BaseProvider

_DEFAULT_BASE_URL = "https://api.openai.com/v1"

_MODEL_CONTEXT: dict[str, int] = {
    "gpt-4": 8_192,
    "gpt-4-turbo": 128_000,
    "gpt-4o": 128_000,
    "gpt-3.5-turbo": 16_385,
}


class OpenAIProvider(BaseProvider):
    """Provider for the OpenAI Chat Completions API.

    Args:
        api_key: OpenAI API key.
        model: Model identifier (default ``gpt-4``).
        base_url: Override the API base URL (useful for proxies / Azure).
        timeout: HTTP timeout in seconds.
    """

    def __init__(
        self,
        api_key: str,
        model: str = "gpt-4",
        base_url: str | None = None,
        timeout: float = 30.0,
    ) -> None:
        self._api_key = api_key
        self._model = model
        self._base_url = (base_url or _DEFAULT_BASE_URL).rstrip("/")
        self._timeout = timeout

    # -- BaseProvider implementation ------------------------------------------

    async def complete(
        self,
        messages: list[dict[str, str]],
        **kwargs: Any,
    ) -> str:
        payload: dict[str, Any] = {
            "model": self._model,
            "messages": messages,
            **kwargs,
        }
        async with httpx.AsyncClient(timeout=self._timeout) as client:
            resp = await client.post(
                f"{self._base_url}/chat/completions",
                headers=self._headers(),
                json=payload,
            )
            resp.raise_for_status()
            data = resp.json()
        return data["choices"][0]["message"]["content"]

    async def stream(
        self,
        messages: list[dict[str, str]],
        **kwargs: Any,
    ) -> AsyncIterator[str]:
        payload: dict[str, Any] = {
            "model": self._model,
            "messages": messages,
            "stream": True,
            **kwargs,
        }
        async with httpx.AsyncClient(timeout=self._timeout) as client:
            async with client.stream(
                "POST",
                f"{self._base_url}/chat/completions",
                headers=self._headers(),
                json=payload,
            ) as resp:
                resp.raise_for_status()
                async for line in resp.aiter_lines():
                    if not line.startswith("data: "):
                        continue
                    data_str = line[len("data: "):]
                    if data_str.strip() == "[DONE]":
                        break
                    chunk = json.loads(data_str)
                    delta = chunk["choices"][0].get("delta", {})
                    content = delta.get("content")
                    if content:
                        yield content

    @property
    def model_name(self) -> str:
        return self._model

    @property
    def max_context_length(self) -> int:
        return _MODEL_CONTEXT.get(self._model, 8_192)

    # -- helpers --------------------------------------------------------------

    def _headers(self) -> dict[str, str]:
        return {
            "Authorization": f"Bearer {self._api_key}",
            "Content-Type": "application/json",
        }
