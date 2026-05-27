"""Text summarization client for the AHF AI Application Framework.

Summarizes long-form text into either a concise paragraph or bullet points,
with input validation and token usage tracking.
"""

from __future__ import annotations

import logging
from typing import Literal

from ahf_ai.client import BaseClient
from ahf_ai.config import Config
from ahf_ai.types.models import SummaryResult, Usage
from ahf_ai.utils.token_counter import count_tokens, estimate_cost, warn_if_exceeds

logger = logging.getLogger("ahf_ai.summarizer")

_MIN_INPUT_LENGTH = 50
_MAX_INPUT_CHARS = 500_000

_PARAGRAPH_SYSTEM = (
    "You are a precise summarizer. Produce a single concise paragraph "
    "that captures the key points of the user's text. Do not include "
    "preamble like 'Here is a summary'."
)
_BULLETS_SYSTEM = (
    "You are a precise summarizer. Produce a concise bulleted list "
    "capturing the key points of the user's text. Use '- ' for each bullet. "
    "Do not include preamble."
)


class Summarizer(BaseClient):
    """High-level text summarization interface.

    Example::

        s = Summarizer(Config(provider="anthropic", api_key="sk-..."))
        result = await s.summarize(long_article, format="bullets")
        print(result.summary)
    """

    def __init__(self, config: Config | None = None) -> None:
        super().__init__(config)

    async def summarize(
        self,
        text: str,
        max_length: int = 200,
        format: Literal["paragraph", "bullets"] = "paragraph",  # noqa: A002
    ) -> SummaryResult:
        """Summarize *text* into at most *max_length* tokens.

        Args:
            text: The source text to summarize.
            max_length: Approximate maximum token budget for the summary.
            format: Output style -- ``"paragraph"`` or ``"bullets"``.

        Returns:
            A ``SummaryResult`` with the summary and metadata.

        Raises:
            ValueError: If the input is too short or too long.
        """
        if len(text.strip()) < _MIN_INPUT_LENGTH:
            raise ValueError(
                f"Input text is too short to summarize "
                f"(minimum {_MIN_INPUT_LENGTH} characters)."
            )
        if len(text) > _MAX_INPUT_CHARS:
            raise ValueError(
                f"Input text exceeds maximum length of {_MAX_INPUT_CHARS:,} characters."
            )

        warn_if_exceeds(text, self._provider.max_context_length, label="summarizer")

        system_prompt = _PARAGRAPH_SYSTEM if format == "paragraph" else _BULLETS_SYSTEM
        user_msg = (
            f"Summarize the following text in no more than {max_length} tokens:\n\n"
            f"{text}"
        )
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_msg},
        ]

        raw = await self._request(messages, max_tokens=max_length, temperature=0.3)
        raw = self._validate_response(raw)
        filtered, _ = self._apply_safety_filters(raw)

        prompt_tokens = count_tokens(user_msg, self._provider.model_name)
        completion_tokens = count_tokens(filtered, self._provider.model_name)
        cost = estimate_cost(
            prompt_tokens, completion_tokens, self._provider.model_name
        )

        return SummaryResult(
            summary=filtered,
            original_length=len(text),
            compressed_length=len(filtered),
            format=format,
            usage=Usage(
                prompt_tokens=prompt_tokens,
                completion_tokens=completion_tokens,
                total_tokens=prompt_tokens + completion_tokens,
                estimated_cost=cost,
            ),
        )
