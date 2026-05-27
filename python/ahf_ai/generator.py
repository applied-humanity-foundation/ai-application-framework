"""Text generation client for the AHF AI Application Framework.

Provides both one-shot ``generate()`` and streaming ``stream()`` interfaces
with integrated safety filtering and token usage tracking.
"""

from __future__ import annotations

import logging
from typing import AsyncIterator, Literal

from ahf_ai.client import BaseClient
from ahf_ai.config import Config
from ahf_ai.types.models import GenerationResult, Usage
from ahf_ai.utils.logger import Timer
from ahf_ai.utils.token_counter import count_tokens, estimate_cost

logger = logging.getLogger("ahf_ai.generator")


class TextGenerator(BaseClient):
    """High-level text generation interface.

    Example::

        gen = TextGenerator(Config(provider="openai", api_key="sk-..."))
        result = await gen.generate("Explain quantum computing in one paragraph.")
        print(result.text)
    """

    def __init__(self, config: Config | None = None) -> None:
        super().__init__(config)

    async def generate(
        self,
        prompt: str,
        max_tokens: int = 500,
        temperature: float = 0.7,
        safety_level: Literal["strict", "moderate", "permissive"] = "moderate",
        system_prompt: str | None = None,
    ) -> GenerationResult:
        """Generate text from a prompt.

        Args:
            prompt: The user prompt.
            max_tokens: Maximum tokens to generate.
            temperature: Sampling temperature.
            safety_level: Override the default safety level for this call.
            system_prompt: Optional system instruction prepended to messages.

        Returns:
            A ``GenerationResult`` with the generated text, usage stats,
            and safety metadata.
        """
        # Check input safety
        input_check = self._safety.check_input(prompt)
        if not input_check.is_safe and safety_level == "strict":
            return GenerationResult(
                text="",
                usage=Usage(prompt_tokens=0, completion_tokens=0, total_tokens=0),
                model=self._provider.model_name,
                finish_reason="safety",
                safety_filtered=True,
            )

        messages: list[dict[str, str]] = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        raw = await self._request(
            messages, max_tokens=max_tokens, temperature=temperature
        )
        raw = self._validate_response(raw)

        # Apply output safety
        filtered_text, safety_result = self._apply_safety_filters(raw)

        prompt_tokens = count_tokens(prompt, self._provider.model_name)
        completion_tokens = count_tokens(filtered_text, self._provider.model_name)
        cost = estimate_cost(
            prompt_tokens, completion_tokens, self._provider.model_name
        )

        return GenerationResult(
            text=filtered_text,
            usage=Usage(
                prompt_tokens=prompt_tokens,
                completion_tokens=completion_tokens,
                total_tokens=prompt_tokens + completion_tokens,
                estimated_cost=cost,
            ),
            model=self._provider.model_name,
            finish_reason="safety" if not safety_result.is_safe else "stop",
            safety_filtered=not safety_result.is_safe,
        )

    async def stream(
        self,
        prompt: str,
        max_tokens: int = 500,
        temperature: float = 0.7,
        system_prompt: str | None = None,
    ) -> AsyncIterator[str]:
        """Stream generated text chunk by chunk.

        Each yielded string is a token or small group of tokens as they
        arrive from the provider. Safety filtering is applied per-chunk.

        Args:
            prompt: The user prompt.
            max_tokens: Maximum tokens to generate.
            temperature: Sampling temperature.
            system_prompt: Optional system instruction.

        Yields:
            Text chunks as they arrive.
        """
        messages: list[dict[str, str]] = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        await self._rate_limiter.acquire()

        async for chunk in self._provider.stream(
            messages, max_tokens=max_tokens, temperature=temperature
        ):
            # Lightweight per-chunk PII redaction
            filtered, _ = self._apply_safety_filters(chunk)
            yield filtered
