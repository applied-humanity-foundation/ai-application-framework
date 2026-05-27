"""Configuration management for the AHF AI Application Framework.

Supports loading settings from environment variables, dictionaries, or
JSON/YAML files. Sensible defaults are provided for every field.
"""

from __future__ import annotations

import json
import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Literal, Optional


@dataclass
class Config:
    """Central configuration for AHF AI clients.

    Attributes:
        provider: Backend LLM provider to use.
        api_key: API key (defaults to the ``AHF_AI_API_KEY`` env var).
        model: Model identifier passed to the provider.
        temperature: Sampling temperature, 0.0 -- 2.0.
        max_tokens: Maximum tokens per completion.
        safety_level: Content safety strictness.
        rate_limit_rpm: Requests-per-minute cap for the rate limiter.
        timeout: HTTP request timeout in seconds.
        verbose: Enable debug-level logging.
        base_url: Override the provider's default API base URL.
    """

    provider: Literal["openai", "anthropic", "local"] = "openai"
    api_key: Optional[str] = field(
        default_factory=lambda: os.environ.get("AHF_AI_API_KEY")
    )
    model: str = "gpt-4"
    temperature: float = 0.7
    max_tokens: int = 1024
    safety_level: Literal["strict", "moderate", "permissive"] = "moderate"
    rate_limit_rpm: int = 60
    timeout: float = 30.0
    verbose: bool = False
    base_url: Optional[str] = None

    # -- factory class methods ------------------------------------------------

    @classmethod
    def from_env(cls) -> "Config":
        """Build a Config entirely from environment variables.

        Recognised env vars (all prefixed ``AHF_AI_``):
            AHF_AI_API_KEY, AHF_AI_PROVIDER, AHF_AI_MODEL,
            AHF_AI_TEMPERATURE, AHF_AI_MAX_TOKENS, AHF_AI_SAFETY_LEVEL,
            AHF_AI_RATE_LIMIT_RPM, AHF_AI_TIMEOUT, AHF_AI_VERBOSE,
            AHF_AI_BASE_URL.
        """
        env = os.environ.get
        return cls(
            provider=env("AHF_AI_PROVIDER", "openai"),  # type: ignore[arg-type]
            api_key=env("AHF_AI_API_KEY"),
            model=env("AHF_AI_MODEL", "gpt-4"),
            temperature=float(env("AHF_AI_TEMPERATURE", "0.7")),
            max_tokens=int(env("AHF_AI_MAX_TOKENS", "1024")),
            safety_level=env("AHF_AI_SAFETY_LEVEL", "moderate"),  # type: ignore[arg-type]
            rate_limit_rpm=int(env("AHF_AI_RATE_LIMIT_RPM", "60")),
            timeout=float(env("AHF_AI_TIMEOUT", "30.0")),
            verbose=env("AHF_AI_VERBOSE", "").lower() in ("1", "true", "yes"),
            base_url=env("AHF_AI_BASE_URL"),
        )

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Config":
        """Build a Config from an arbitrary dictionary, ignoring unknown keys."""
        known_fields = {f.name for f in cls.__dataclass_fields__.values()}
        filtered = {k: v for k, v in data.items() if k in known_fields}
        return cls(**filtered)

    @classmethod
    def from_file(cls, path: str | Path) -> "Config":
        """Load configuration from a JSON file.

        Args:
            path: Filesystem path to a JSON configuration file.

        Raises:
            FileNotFoundError: If the file does not exist.
            json.JSONDecodeError: If the file is not valid JSON.
        """
        raw = Path(path).read_text(encoding="utf-8")
        return cls.from_dict(json.loads(raw))
