"""Anthropic Messages API provider using raw httpx requests.

Talks directly to the Anthropic Messages API without the ``anthropic``
Python package, keeping the dependency tree minimal.
"""

from __future__ import annotations

import json
from typing import Any, AsyncIterator

import httpx

from ahf_ai.providers.base import BaseProvider

_DEFAULT_BASE_URL = "https://api.anthropic.com/v1"
_API_VERSION = "2023-06-01"

_MODEL_CONTEXT: dict[str, int] = {
    "claude-sonnet-4-20250514": 200_000,
    "claude-opus-4-20250514": 200_000,
    "claude-3-haiku": 200_000,
    "claude-3-sonnet": 200_000,
    "claude-3-opus": 200_000,
}


class AnthropicProvider(BaseProvider):
    """Provider for the Anthropic Messages API.

    Args:
        api_key: Anthropic API key.
        model: Model identifier (default ``claude-sonnet-4-20250514``).
        base_url: Override the API base URL.
        timeout: HTTP timeout in seconds.
    """

    def __init__(
        self,
        api_key: str,
        model: str = "claude-sonnet-4-20250514",
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
        system_text, user_messages = self._split_system(messages)
        payload: dict[str, Any] = {
            "model": self._model,
            "max_tokens": kwargs.pop("max_tokens", 1024),
            "messages": user_messages,
            **kwargs,
        }
        if system_text:
            payload["system"] = system_text

        async with httpx.AsyncClient(timeout=self._timeout) as client:
            resp = await client.post(
                f"{self._base_url}/messages",
                headers=self._headers(),
                json=payload,
            )
            resp.raise_for_status()
            data = resp.json()
        return data["content"][0]["text"]

    async def stream(
        self,
        messages: list[dict[str, str]],
        **kwargs: Any,
    ) -> AsyncIterator[str]:
        system_text, user_messages = self._split_system(messages)
        payload: dict[str, Any] = {
            "model": self._model,
            "max_tokens": kwargs.pop("max_tokens", 1024),
            "messages": user_messages,
            "stream": True,
            **kwargs,
        }
        if system_text:
            payload["system"] = system_text

        async with httpx.AsyncClient(timeout=self._timeout) as client:
            async with client.stream(
                "POST",
                f"{self._base_url}/messages",
                headers=self._headers(),
                json=payload,
            ) as resp:
                resp.raise_for_status()
                async for line in resp.aiter_lines():
                    if not line.startswith("data: "):
                        continue
                    data_str = line[len("data: "):]
                    chunk = json.loads(data_str)
                    if chunk.get("type") == "content_block_delta":
                        text = chunk["delta"].get("text", "")
                        if text:
                            yield text
                    elif chunk.get("type") == "message_stop":
                        break

    @property
    def model_name(self) -> str:
        return self._model

    @property
    def max_context_length(self) -> int:
        return _MODEL_CONTEXT.get(self._model, 200_000)

    # -- helpers --------------------------------------------------------------

    def _headers(self) -> dict[str, str]:
        return {
            "x-api-key": self._api_key,
            "anthropic-version": _API_VERSION,
            "Content-Type": "application/json",
        }

    @staticmethod
    def _split_system(
        messages: list[dict[str, str]],
    ) -> tuple[str | None, list[dict[str, str]]]:
        """Separate system messages from user/assistant messages.

        The Anthropic API takes ``system`` as a top-level parameter rather
        than as a message role.
        """
        system_parts: list[str] = []
        other: list[dict[str, str]] = []
        for msg in messages:
            if msg.get("role") == "system":
                system_parts.append(msg["content"])
            else:
                other.append(msg)
        system_text = "\n\n".join(system_parts) if system_parts else None
        return system_text, other
