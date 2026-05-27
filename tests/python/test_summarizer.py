"""Tests for the Summarizer module."""

from __future__ import annotations

import pytest

from ahf_ai.types import SummaryResult, Usage


class TestSummarizer:
    """Unit tests for summarization results and options."""

    def test_summary_result_paragraph_format(self) -> None:
        """SummaryResult should default to paragraph format."""
        result = SummaryResult(
            summary="AI transforms healthcare and finance.",
            original_length=500,
            compressed_length=40,
        )
        assert result.format == "paragraph"
        assert result.compressed_length < result.original_length

    def test_summary_result_bullets_format(self) -> None:
        """SummaryResult should accept bullets format."""
        result = SummaryResult(
            summary="- Healthcare AI\n- Finance AI",
            original_length=500,
            compressed_length=30,
            format="bullets",
        )
        assert result.format == "bullets"
        assert result.summary.startswith("- ")

    def test_summary_result_with_usage(self) -> None:
        """SummaryResult should optionally include usage stats."""
        usage = Usage(prompt_tokens=200, completion_tokens=30, total_tokens=230)
        result = SummaryResult(
            summary="Short summary.",
            original_length=1000,
            compressed_length=15,
            usage=usage,
        )
        assert result.usage is not None
        assert result.usage.total_tokens == 230

    def test_summary_compression_ratio(self) -> None:
        """Compressed length should be strictly less than original for real summaries."""
        result = SummaryResult(
            summary="Brief.",
            original_length=2000,
            compressed_length=6,
        )
        ratio = result.compressed_length / result.original_length
        assert ratio < 1.0
        assert ratio == pytest.approx(0.003, abs=0.001)

    def test_summary_result_without_usage(self) -> None:
        """SummaryResult.usage should default to None."""
        result = SummaryResult(
            summary="No usage info.",
            original_length=100,
            compressed_length=14,
        )
        assert result.usage is None
