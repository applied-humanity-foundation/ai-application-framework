"""Text classification client for the AHF AI Application Framework.

Classifies text into caller-supplied categories with per-category
confidence scores.
"""

from __future__ import annotations

import json
import logging
from typing import Any

from ahf_ai.client import BaseClient
from ahf_ai.config import Config
from ahf_ai.types.models import CategoryScore, ClassificationResult, Usage
from ahf_ai.utils.token_counter import count_tokens, estimate_cost

logger = logging.getLogger("ahf_ai.classifier")

_SYSTEM_PROMPT = (
    "You are a text classification assistant. Given a text and a list of "
    "categories, return a JSON object mapping each category name to a "
    "confidence score between 0.0 and 1.0. The scores should sum to "
    "approximately 1.0. Return ONLY valid JSON, no explanation."
)


class Classifier(BaseClient):
    """High-level text classification interface.

    Example::

        c = Classifier(Config(provider="openai", api_key="sk-..."))
        result = await c.classify(
            "The stock market crashed today",
            categories=["finance", "sports", "politics", "technology"],
        )
        print(result.top_category)  # "finance"
    """

    def __init__(self, config: Config | None = None) -> None:
        super().__init__(config)

    async def classify(
        self,
        text: str,
        categories: list[str],
        threshold: float = 0.5,
    ) -> ClassificationResult:
        """Classify *text* into the given *categories*.

        Args:
            text: The text to classify.
            categories: List of category labels the model should score.
            threshold: Minimum confidence to consider a category matched
                (used by ``ClassificationResult.above_threshold``).

        Returns:
            A ``ClassificationResult`` with scores sorted by confidence.

        Raises:
            ValueError: If fewer than two categories are provided.
        """
        if len(categories) < 2:
            raise ValueError("At least two categories are required for classification.")

        user_msg = (
            f"Categories: {json.dumps(categories)}\n\n"
            f"Text to classify:\n{text}"
        )
        messages = [
            {"role": "system", "content": _SYSTEM_PROMPT},
            {"role": "user", "content": user_msg},
        ]

        raw = await self._request(messages, max_tokens=200, temperature=0.0)
        raw = self._validate_response(raw)

        scores = self._parse_scores(raw, categories)

        # Sort descending by confidence
        scores.sort(key=lambda s: s.confidence, reverse=True)

        prompt_tokens = count_tokens(user_msg, self._provider.model_name)
        completion_tokens = count_tokens(raw, self._provider.model_name)
        cost = estimate_cost(
            prompt_tokens, completion_tokens, self._provider.model_name
        )

        return ClassificationResult(
            categories=scores,
            top_category=scores[0].name if scores else categories[0],
            usage=Usage(
                prompt_tokens=prompt_tokens,
                completion_tokens=completion_tokens,
                total_tokens=prompt_tokens + completion_tokens,
                estimated_cost=cost,
            ),
        )

    @staticmethod
    def _parse_scores(
        raw: str, categories: list[str]
    ) -> list[CategoryScore]:
        """Parse the model's JSON response into ``CategoryScore`` objects.

        Falls back to equal-weight scores if parsing fails.
        """
        try:
            # Strip markdown code fences if present
            cleaned = raw.strip()
            if cleaned.startswith("```"):
                cleaned = cleaned.split("\n", 1)[1]
                cleaned = cleaned.rsplit("```", 1)[0]
            data: dict[str, Any] = json.loads(cleaned)
            scores: list[CategoryScore] = []
            for cat in categories:
                raw_score = data.get(cat, 0.0)
                confidence = max(0.0, min(1.0, float(raw_score)))
                scores.append(CategoryScore(name=cat, confidence=confidence))
            return scores
        except (json.JSONDecodeError, TypeError, KeyError) as exc:
            logger.warning("Failed to parse classification response: %s", exc)
            equal = 1.0 / len(categories)
            return [
                CategoryScore(name=cat, confidence=round(equal, 4))
                for cat in categories
            ]
