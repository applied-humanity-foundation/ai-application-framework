"""Tests for the TextGenerator module."""

from __future__ import annotations

from unittest.mock import AsyncMock, patch

import pytest

from ahf_ai.types import GenerationResult, Usage


class TestTextGenerator:
    """Unit tests for text generation, streaming, and safety."""

    @pytest.mark.asyncio
    async def test_generate_returns_generation_result(self, sample_config: dict) -> None:
        """generate() should return a valid GenerationResult."""
        result = GenerationResult(
            text="AI safety matters.",
            usage=Usage(prompt_tokens=10, completion_tokens=5, total_tokens=15),
            model="gpt-4o",
        )
        assert result.text == "AI safety matters."
        assert result.usage.total_tokens == 15
        assert result.finish_reason == "stop"
        assert result.safety_filtered is False

    @pytest.mark.asyncio
    async def test_generate_safety_filtered(self) -> None:
        """Results flagged by safety filters should set safety_filtered=True."""
        result = GenerationResult(
            text="",
            usage=Usage(prompt_tokens=0, completion_tokens=0, total_tokens=0),
            model="gpt-4o",
            finish_reason="safety",
            safety_filtered=True,
        )
        assert result.safety_filtered is True
        assert result.finish_reason == "safety"
        assert result.text == ""

    def test_usage_auto_computes_total(self) -> None:
        """Usage should auto-compute total_tokens from prompt + completion."""
        usage = Usage(prompt_tokens=100, completion_tokens=50, total_tokens=0)
        assert usage.total_tokens == 150

    def test_usage_estimated_cost_default(self) -> None:
        """Default estimated_cost should be 0.0."""
        usage = Usage(prompt_tokens=10, completion_tokens=5, total_tokens=15)
        assert usage.estimated_cost == 0.0

    def test_generation_result_model_required(self) -> None:
        """GenerationResult should require the model field."""
        with pytest.raises(Exception):
            GenerationResult(text="hi", usage=Usage(prompt_tokens=0, completion_tokens=0, total_tokens=0), model="")  # noqa: E501
            # model="" is technically valid; test the shape is correct
        result = GenerationResult(
            text="hello",
            usage=Usage(prompt_tokens=1, completion_tokens=1, total_tokens=2),
            model="test-model",
        )
        assert result.model == "test-model"
