"""Tests for the Translator module."""

from __future__ import annotations

import pytest

from ahf_ai.types import TranslationResult, Usage


class TestTranslator:
    """Unit tests for translation results and language detection."""

    def test_translation_result_fields(self) -> None:
        """TranslationResult should carry all expected fields."""
        result = TranslationResult(
            translated_text="AI安全非常重要。",
            source_lang="en",
            target_lang="zh",
            confidence=0.95,
        )
        assert result.translated_text == "AI安全非常重要。"
        assert result.source_lang == "en"
        assert result.target_lang == "zh"
        assert result.confidence == pytest.approx(0.95)

    def test_translation_confidence_range(self) -> None:
        """Confidence must be between 0.0 and 1.0."""
        result = TranslationResult(
            translated_text="Hola",
            source_lang="en",
            target_lang="es",
            confidence=0.0,
        )
        assert 0.0 <= result.confidence <= 1.0

        with pytest.raises(Exception):
            TranslationResult(
                translated_text="Bad",
                source_lang="en",
                target_lang="fr",
                confidence=1.5,  # Out of range
            )

    def test_translation_default_confidence(self) -> None:
        """Default confidence should be 1.0."""
        result = TranslationResult(
            translated_text="Bonjour",
            source_lang="en",
            target_lang="fr",
        )
        assert result.confidence == 1.0

    def test_translation_with_usage(self) -> None:
        """TranslationResult should accept optional usage stats."""
        usage = Usage(prompt_tokens=50, completion_tokens=40, total_tokens=90)
        result = TranslationResult(
            translated_text="Hallo Welt",
            source_lang="en",
            target_lang="de",
            usage=usage,
        )
        assert result.usage is not None
        assert result.usage.prompt_tokens == 50

    def test_translation_auto_detect_source(self) -> None:
        """When source is auto-detected, source_lang should be populated."""
        result = TranslationResult(
            translated_text="Hello world",
            source_lang="es",
            target_lang="en",
            confidence=0.88,
        )
        assert result.source_lang == "es"
        assert len(result.source_lang) > 0
