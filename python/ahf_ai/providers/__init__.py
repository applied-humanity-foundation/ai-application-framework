"""Provider registry and factory for the AHF AI Application Framework.

Use ``get_provider(name, **kwargs)`` to obtain a configured provider instance.
"""

from __future__ import annotations

from typing import Any

from ahf_ai.providers.anthropic import AnthropicProvider
from ahf_ai.providers.base import BaseProvider
from ahf_ai.providers.local import LocalProvider
from ahf_ai.providers.openai import OpenAIProvider

_REGISTRY: dict[str, type[BaseProvider]] = {
    "openai": OpenAIProvider,
    "anthropic": AnthropicProvider,
    "local": LocalProvider,
}


def get_provider(name: str, **kwargs: Any) -> BaseProvider:
    """Instantiate and return the provider identified by *name*.

    Args:
        name: One of ``"openai"``, ``"anthropic"``, or ``"local"``.
        **kwargs: Forwarded to the provider constructor (api_key, model, ...).

    Raises:
        ValueError: If *name* is not a registered provider.
    """
    cls = _REGISTRY.get(name)
    if cls is None:
        available = ", ".join(sorted(_REGISTRY))
        raise ValueError(
            f"Unknown provider {name!r}. Available providers: {available}"
        )
    return cls(**kwargs)


__all__ = [
    "AnthropicProvider",
    "BaseProvider",
    "LocalProvider",
    "OpenAIProvider",
    "get_provider",
]
