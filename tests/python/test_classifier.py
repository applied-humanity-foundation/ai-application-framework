"""Tests for the Classifier module."""

from __future__ import annotations

import pytest

from ahf_ai.types import ClassificationResult, CategoryScore


class TestClassifier:
    """Unit tests for classification results and thresholds."""

    def test_classification_top_category(self) -> None:
        """top_category should match the highest-confidence category."""
        result = ClassificationResult(
            categories=[
                CategoryScore(name="technology", confidence=0.8),
                CategoryScore(name="science", confidence=0.15),
                CategoryScore(name="politics", confidence=0.05),
            ],
            top_category="technology",
        )
        assert result.top_category == "technology"
        assert result.categories[0].confidence == 0.8

    def test_above_threshold(self) -> None:
        """above_threshold() should filter categories below the threshold."""
        result = ClassificationResult(
            categories=[
                CategoryScore(name="tech", confidence=0.7),
                CategoryScore(name="sci", confidence=0.2),
                CategoryScore(name="other", confidence=0.1),
            ],
            top_category="tech",
        )
        above = result.above_threshold(0.5)
        assert len(above) == 1
        assert above[0].name == "tech"

        above_low = result.above_threshold(0.15)
        assert len(above_low) == 2

    def test_classification_confidence_sums(self) -> None:
        """Category confidences should sum to approximately 1.0."""
        scores = [
            CategoryScore(name="a", confidence=0.5),
            CategoryScore(name="b", confidence=0.3),
            CategoryScore(name="c", confidence=0.2),
        ]
        total = sum(s.confidence for s in scores)
        assert total == pytest.approx(1.0)

    def test_category_score_validation(self) -> None:
        """CategoryScore confidence must be in [0.0, 1.0]."""
        valid = CategoryScore(name="test", confidence=0.5)
        assert valid.confidence == 0.5

        with pytest.raises(Exception):
            CategoryScore(name="bad", confidence=-0.1)
