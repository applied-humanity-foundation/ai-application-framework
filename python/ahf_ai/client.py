"""Base HTTP client for the AHF AI Application Framework.

Wraps ``httpx.AsyncClient`` with retry logic, timeout handling, structured
logging, rate limiting, and automatic safety filtering.
"""

from __future__ import annotations

import logging
from typing import Any

import httpx

from ahf_ai.config import Config
from ahf_ai.providers import BaseProvider, get_provider
from ahf_ai.safety import SafetyFilter
from ahf_ai.types.models import SafetyResult
from ahf_ai.utils.logger import Timer, log_request, setup_logging
from ahf_ai.utils.rate_limiter import AsyncRateLimiter

logger = logging.getLogger("ahf_ai.client")


class BaseClient:
    """Foundation for every high-level AI wrapper (generator, summarizer, ...).

    Owns the provider instance, rate limiter, safety filter, and logging
    setup so subclasses can focus on domain logic.

    Args:
        config: A ``Config`` instance. If ``None``, ``Config.from_env()`` is used.
    """

    def __init__(self, config: Config | None = None) -> None:
        self.config = config or Config.from_env()
        if self.config.verbose:
            setup_logging(level="DEBUG", format="structured")
        else:
            setup_logging(level="INFO", format="structured")

        self._rate_limiter = AsyncRateLimiter(
            max_requests=self.config.rate_limit_rpm, time_window=60.0
        )
        self._safety = SafetyFilter(level=self.config.safety_level)

        # Build the provider
        provider_kwargs: dict[str, Any] = {
            "model": self.config.model,
            "timeout": self.config.timeout,
        }
        if self.config.api_key and self.config.provider != "local":
            provider_kwargs["api_key"] = self.config.api_key
        if self.config.base_url:
            provider_kwargs["base_url"] = self.config.base_url

        self._provider: BaseProvider = get_provider(
            self.config.provider, **provider_kwargs
        )

    # -- internal helpers subclasses use directly ------------------------------

    async def _request(
        self,
        messages: list[dict[str, str]],
        **kwargs: Any,
    ) -> str:
        """Send a chat-completion request through the provider with retries.

        Applies rate limiting, logs the request, and retries on transient
        HTTP errors up to 3 times with exponential back-off.
        """
        import asyncio

        await self._rate_limiter.acquire()

        last_exc: Exception | None = None
        for attempt in range(1, 4):
            try:
                with Timer() as t:
                    result = await self._provider.complete(messages, **kwargs)
                log_request(logger, self._provider.model_name, t.elapsed_ms)
                return result
            except httpx.HTTPStatusError as exc:
                last_exc = exc
                if exc.response.status_code in (429, 500, 502, 503):
                    wait = 2 ** attempt
                    logger.warning(
                        "Retryable error %s (attempt %d/3), waiting %ds",
                        exc.response.status_code,
                        attempt,
                        wait,
                    )
                    await asyncio.sleep(wait)
                else:
                    raise
            except httpx.TimeoutException as exc:
                last_exc = exc
                logger.warning("Timeout on attempt %d/3", attempt)
                await asyncio.sleep(2 ** attempt)

        raise RuntimeError(
            f"Request failed after 3 retries: {last_exc}"
        ) from last_exc

    def _validate_response(self, text: str) -> str:
        """Raise if the response is empty or clearly malformed."""
        if not text or not text.strip():
            raise ValueError("Received empty response from provider")
        return text.strip()

    def _apply_safety_filters(self, text: str) -> tuple[str, SafetyResult]:
        """Run the output safety filter and return (possibly redacted text, result)."""
        result = self._safety.check_output(text)
        filtered = result.filtered_text if result.filtered_text else text
        return filtered, result
