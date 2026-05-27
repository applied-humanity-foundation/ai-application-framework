"""Content safety filtering for the AHF AI Application Framework.

Provides regex-based PII detection (emails, phone numbers, SSN patterns) and
configurable safety levels (strict / moderate / permissive) for both inputs
and outputs.
"""

from __future__ import annotations

import re
from typing import Literal

from ahf_ai.types.models import SafetyResult

# -- PII regex patterns -------------------------------------------------------

_EMAIL_RE = re.compile(
    r"\b[A-Za-z0-9._%+\-]+@[A-Za-z0-9.\-]+\.[A-Z|a-z]{2,}\b"
)
_PHONE_RE = re.compile(
    r"(?<!\d)"
    r"(?:\+?1[\s\-.]?)?"
    r"(?:\(?\d{3}\)?[\s\-.]?)"
    r"\d{3}[\s\-.]?\d{4}"
    r"(?!\d)"
)
_SSN_RE = re.compile(r"\b\d{3}[\s\-]?\d{2}[\s\-]?\d{4}\b")
_CREDIT_CARD_RE = re.compile(r"\b(?:\d[ \-]?){13,19}\b")

_PII_PATTERNS: dict[str, re.Pattern[str]] = {
    "email": _EMAIL_RE,
    "phone_number": _PHONE_RE,
    "ssn": _SSN_RE,
    "credit_card": _CREDIT_CARD_RE,
}

# -- Blocked / flagged keyword lists per level --------------------------------

_STRICT_KEYWORDS: list[str] = [
    "kill", "bomb", "hack into", "steal", "exploit vulnerability",
    "make weapon", "synthesize drug", "bypass security",
]
_MODERATE_KEYWORDS: list[str] = [
    "hack into", "exploit vulnerability", "make weapon",
    "synthesize drug", "bypass security",
]

_REDACTION = "[REDACTED]"


class SafetyFilter:
    """Configurable text safety checker.

    Args:
        level: One of ``strict``, ``moderate``, or ``permissive``.
    """

    def __init__(
        self, level: Literal["strict", "moderate", "permissive"] = "moderate"
    ) -> None:
        self.level = level

    # -- public API -----------------------------------------------------------

    def check_input(self, text: str) -> SafetyResult:
        """Validate *text* before sending it to a model.

        Returns a ``SafetyResult`` indicating whether the text is safe and,
        if not, which flags were triggered.
        """
        flags: list[str] = []
        details: dict[str, str] = {}

        # PII detection (always on for strict/moderate)
        if self.level in ("strict", "moderate"):
            pii_flags, pii_details = self._detect_pii(text)
            flags.extend(pii_flags)
            details.update(pii_details)

        # Keyword / intent check
        keyword_flags = self._check_keywords(text)
        flags.extend(keyword_flags)

        filtered_text = self._redact_pii(text) if flags else None

        return SafetyResult(
            is_safe=len(flags) == 0,
            flags=flags,
            filtered_text=filtered_text,
            details=details,
        )

    def check_output(self, text: str) -> SafetyResult:
        """Validate model *output* before returning it to the caller.

        Applies the same PII redaction and keyword checks as ``check_input``,
        but always produces a ``filtered_text`` with PII removed.
        """
        flags: list[str] = []
        details: dict[str, str] = {}

        pii_flags, pii_details = self._detect_pii(text)
        flags.extend(pii_flags)
        details.update(pii_details)

        keyword_flags = self._check_keywords(text)
        flags.extend(keyword_flags)

        filtered_text = self._redact_pii(text)

        return SafetyResult(
            is_safe=len(flags) == 0,
            flags=flags,
            filtered_text=filtered_text,
            details=details,
        )

    # -- internals ------------------------------------------------------------

    def _detect_pii(self, text: str) -> tuple[list[str], dict[str, str]]:
        """Return flags and details for any PII patterns found."""
        flags: list[str] = []
        details: dict[str, str] = {}
        for label, pattern in _PII_PATTERNS.items():
            matches = pattern.findall(text)
            if matches:
                flags.append(f"pii_{label}")
                details[f"pii_{label}"] = f"Found {len(matches)} occurrence(s)"
        return flags, details

    def _check_keywords(self, text: str) -> list[str]:
        """Return flags for dangerous keywords found in *text*."""
        lower = text.lower()
        if self.level == "permissive":
            return []
        keywords = _STRICT_KEYWORDS if self.level == "strict" else _MODERATE_KEYWORDS
        found: list[str] = []
        for kw in keywords:
            if kw in lower:
                found.append(f"blocked_keyword:{kw}")
        return found

    def _redact_pii(self, text: str) -> str:
        """Return a copy of *text* with all matched PII replaced."""
        result = text
        for pattern in _PII_PATTERNS.values():
            result = pattern.sub(_REDACTION, result)
        return result
