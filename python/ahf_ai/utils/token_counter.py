"""Lightweight token counting and cost estimation utilities.

Uses a chars/4 heuristic by default. Cost tables are maintained for common
models so callers can estimate spend without an external tokenizer dependency.
"""

from __future__ import annotations

import logging
import math
from typing import Optional

logger = logging.getLogger("ahf_ai.utils.token_counter")

# Pricing per 1 000 tokens (USD) — input / output
_COST_TABLE: dict[str, tuple[float, float]] = {
    "gpt-4": (0.03, 0.06),
    "gpt-4-turbo": (0.01, 0.03),
    "gpt-4o": (0.005, 0.015),
    "gpt-3.5-turbo": (0.0005, 0.0015),
    "claude-sonnet-4-20250514": (0.003, 0.015),
    "claude-3-haiku": (0.00025, 0.00125),
    "claude-opus-4-20250514": (0.015, 0.075),
    "local": (0.0, 0.0),
}


def count_tokens(text: str, model: str = "gpt-4") -> int:
    """Estimate the number of tokens in *text* using a chars/4 heuristic.

    This avoids pulling in ``tiktoken`` or ``sentencepiece`` as a hard
    dependency while remaining accurate enough for budget estimates.
    """
    if not text:
        return 0
    return max(1, math.ceil(len(text) / 4))


def estimate_cost(
    tokens_in: int,
    tokens_out: int,
    model: str = "gpt-4",
) -> float:
    """Return estimated USD cost for the given token counts and model.

    Falls back to gpt-4 pricing when the model is not in the cost table.
    """
    in_rate, out_rate = _COST_TABLE.get(model, _COST_TABLE["gpt-4"])
    cost = (tokens_in / 1000) * in_rate + (tokens_out / 1000) * out_rate
    return round(cost, 6)


def warn_if_exceeds(
    text: str,
    max_tokens: int,
    model: str = "gpt-4",
    label: Optional[str] = None,
) -> bool:
    """Log a warning and return ``True`` if *text* likely exceeds *max_tokens*.

    Args:
        text: Input text to measure.
        max_tokens: Token budget.
        model: Model name for the heuristic (currently unused, reserved).
        label: Optional label for the warning message.
    """
    estimated = count_tokens(text, model)
    if estimated > max_tokens:
        tag = f" [{label}]" if label else ""
        logger.warning(
            "Text%s has ~%d tokens, exceeding limit of %d", tag, estimated, max_tokens
        )
        return True
    return False
