"""Local LLM provider connecting to an Ollama-compatible server.

Targets the Ollama REST API at ``localhost:11434`` by default.
"""

from __future__ import annotations

import json
from typing import Any, AsyncIterator

import httpx

from ahf_ai.providers.base import BaseProvider

_DEFAULT_BASE_URL = "http://localhost:11434"


class LocalProvider(BaseProvider):
    """Provider for a local Ollama-compatible LLM server.

    Args:
        model: Model name loaded in Ollama (e.g. ``llama3``, ``mistral``).
        base_url: Server address (default ``http://localhost:11434``).
        timeout: HTTP timeout in seconds (local models can be slow).
    """

    def __init__(
        self,
        model: str = "llama3",
        base_url: str | None = None,
        timeout: float = 120.0,
    ) -> None:
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
            "stream": False,
            **kwargs,
        }
        async with httpx.AsyncClient(timeout=self._timeout) as client:
            resp = await client.post(
                f"{self._base_url}/api/chat",
                json=payload,
            )
            resp.raise_for_status()
            data = resp.json()
        return data["message"]["content"]

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
                f"{self._base_url}/api/chat",
                json=payload,
            ) as resp:
                resp.raise_for_status()
                async for line in resp.aiter_lines():
                    if not line.strip():
                        continue
                    chunk = json.loads(line)
                    content = chunk.get("message", {}).get("content", "")
                    if content:
                        yield content
                    if chunk.get("done", False):
                        break

    @property
    def model_name(self) -> str:
        return self._model

    @property
    def max_context_length(self) -> int:
        # Most local models default to 4096; user can override per-model.
        return 4_096
