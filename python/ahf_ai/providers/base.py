"""Abstract base class for LLM providers.

Every concrete provider (OpenAI, Anthropic, local) implements this interface
so the rest of the framework can call any backend through a uniform API.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, AsyncIterator


class BaseProvider(ABC):
    """Abstract LLM provider interface.

    Subclasses must implement ``complete`` and ``stream`` at minimum.
    """

    @abstractmethod
    async def complete(
        self,
        messages: list[dict[str, str]],
        **kwargs: Any,
    ) -> str:
        """Send a chat-completion request and return the assistant response.

        Args:
            messages: Conversation history in OpenAI-style
                ``[{"role": "...", "content": "..."}]`` format.
            **kwargs: Provider-specific overrides (temperature, max_tokens, ...).

        Returns:
            The assistant's reply as a plain string.
        """
        ...

    @abstractmethod
    async def stream(
        self,
        messages: list[dict[str, str]],
        **kwargs: Any,
    ) -> AsyncIterator[str]:
        """Stream a chat-completion response token by token.

        Yields:
            Text chunks as they arrive from the provider.
        """
        ...
        # Unreachable -- required for the type checker to accept an
        # abstract async generator.
        yield ""  # pragma: no cover

    @property
    @abstractmethod
    def model_name(self) -> str:
        """Return the identifier of the model this provider is configured to use."""
        ...

    @property
    @abstractmethod
    def max_context_length(self) -> int:
        """Return the maximum context window in tokens for the active model."""
        ...

    @property
    def supports_streaming(self) -> bool:
        """Whether this provider supports the ``stream`` method (default True)."""
        return True
