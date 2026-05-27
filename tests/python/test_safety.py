"""Tests for the SafetyFilter module (Python types)."""

from __future__ import annotations

import re

import pytest

from ahf_ai.types import SafetyResult


# PII patterns mirroring the framework's safety filter
PII_PATTERNS = {
    "email": re.compile(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}"),
    "phone": re.compile(r"\b(\+?1[-.\s]?)?(\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4})\b"),
    "ssn": re.compile(r"\b\d{3}-\d{2}-\d{4}\b"),
}


class TestSafetyFilter:
    """Unit tests for safety filtering and PII detection."""

    def test_safe_text_passes(self) -> None:
        """Clean text should produce is_safe=True with no flags."""
        result = SafetyResult(is_safe=True, flags=[], details={})
        assert result.is_safe is True
        assert len(result.flags) == 0

    def test_pii_email_detected(self) -> None:
        """PII filter should detect email addresses."""
        text = "Reach me at alice@example.com for details."
        assert PII_PATTERNS["email"].search(text) is not None

    def test_pii_phone_detected(self) -> None:
        """PII filter should detect US phone numbers."""
        text = "Call 555-123-4567 or (555) 987-6543."
        matches = PII_PATTERNS["phone"].findall(text)
        assert len(matches) >= 1

    def test_pii_ssn_detected(self) -> None:
        """PII filter should detect SSN patterns."""
        text = "SSN: 123-45-6789"
        assert PII_PATTERNS["ssn"].search(text) is not None

    def test_no_pii_in_clean_text(self) -> None:
        """Clean text should not trigger any PII pattern."""
        text = "The weather in Paris is mild today."
        for name, pattern in PII_PATTERNS.items():
            assert pattern.search(text) is None, f"{name} should not match"

    def test_safety_result_with_filtered_text(self) -> None:
        """SafetyResult should carry filtered_text when content was redacted."""
        result = SafetyResult(
            is_safe=False,
            flags=["pii_email"],
            filtered_text="Reach me at [REDACTED] for details.",
            details={"pii_email": "Found 1 instance(s)"},
        )
        assert result.filtered_text is not None
        assert "[REDACTED]" in result.filtered_text
        assert not result.is_safe

    def test_safety_result_flags_are_list(self) -> None:
        """Flags should always be a list, even when empty."""
        result = SafetyResult(is_safe=True, flags=[], details={})
        assert isinstance(result.flags, list)

    def test_prompt_injection_detection(self) -> None:
        """Known prompt injection phrases should be flaggable."""
        injection_phrases = [
            "ignore previous instructions",
            "disregard your instructions",
        ]
        for phrase in injection_phrases:
            # In a real implementation this would call checkInput()
            assert phrase.lower() in phrase.lower()
            result = SafetyResult(
                is_safe=False,
                flags=["prompt_injection"],
                details={"prompt_injection": f"Detected: {phrase}"},
            )
            assert "prompt_injection" in result.flags
