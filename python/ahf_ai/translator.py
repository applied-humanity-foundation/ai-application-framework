"""Translation client for the AHF AI Application Framework.

Supports 20+ language codes with automatic source-language detection.
"""

from __future__ import annotations

import logging
from typing import Literal

from ahf_ai.client import BaseClient
from ahf_ai.config import Config
from ahf_ai.types.models import TranslationResult, Usage
from ahf_ai.utils.token_counter import count_tokens, estimate_cost

logger = logging.getLogger("ahf_ai.translator")

SUPPORTED_LANGUAGES: dict[str, str] = {
    "en": "English",
    "es": "Spanish",
    "fr": "French",
    "de": "German",
    "it": "Italian",
    "pt": "Portuguese",
    "nl": "Dutch",
    "pl": "Polish",
    "ru": "Russian",
    "uk": "Ukrainian",
    "ja": "Japanese",
    "ko": "Korean",
    "zh": "Chinese",
    "ar": "Arabic",
    "hi": "Hindi",
    "tr": "Turkish",
    "vi": "Vietnamese",
    "th": "Thai",
    "sv": "Swedish",
    "da": "Danish",
    "fi": "Finnish",
    "he": "Hebrew",
    "id": "Indonesian",
    "ms": "Malay",
}

_DETECT_SYSTEM = (
    "You are a language detection assistant. Reply with ONLY the ISO 639-1 "
    "two-letter language code of the text provided. Nothing else."
)
_TRANSLATE_SYSTEM = (
    "You are an expert translator. Translate the user's text from {source} "
    "to {target}. Output ONLY the translated text, no explanations."
)


class Translator(BaseClient):
    """High-level text translation interface.

    Example::

        t = Translator(Config(provider="openai", api_key="sk-..."))
        result = await t.translate("Bonjour le monde", target="en")
        print(result.translated_text)  # "Hello world"
    """

    def __init__(self, config: Config | None = None) -> None:
        super().__init__(config)

    async def detect_language(self, text: str) -> str:
        """Detect the language of *text* and return its ISO 639-1 code.

        Uses the underlying LLM for detection. Falls back to ``"en"`` if
        the model returns an unrecognised code.
        """
        messages = [
            {"role": "system", "content": _DETECT_SYSTEM},
            {"role": "user", "content": text[:500]},  # Only send a sample
        ]
        raw = await self._request(messages, max_tokens=5, temperature=0.0)
        code = raw.strip().lower()[:2]
        if code not in SUPPORTED_LANGUAGES:
            logger.warning("Unrecognised language code %r, defaulting to 'en'", code)
            return "en"
        return code

    async def translate(
        self,
        text: str,
        source: str = "auto",
        target: str = "en",
    ) -> TranslationResult:
        """Translate *text* from *source* language to *target* language.

        Args:
            text: Text to translate.
            source: ISO 639-1 source language code, or ``"auto"`` for
                automatic detection.
            target: ISO 639-1 target language code.

        Returns:
            A ``TranslationResult`` with the translation and metadata.

        Raises:
            ValueError: If the target language is not supported.
        """
        if target not in SUPPORTED_LANGUAGES:
            raise ValueError(
                f"Unsupported target language {target!r}. "
                f"Supported: {', '.join(sorted(SUPPORTED_LANGUAGES))}"
            )

        # Auto-detect source language
        if source == "auto":
            source = await self.detect_language(text)
        elif source not in SUPPORTED_LANGUAGES:
            raise ValueError(f"Unsupported source language {source!r}.")

        # Skip if source == target
        if source == target:
            return TranslationResult(
                translated_text=text,
                source_lang=source,
                target_lang=target,
                confidence=1.0,
            )

        source_name = SUPPORTED_LANGUAGES[source]
        target_name = SUPPORTED_LANGUAGES[target]
        system_prompt = _TRANSLATE_SYSTEM.format(source=source_name, target=target_name)

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": text},
        ]

        raw = await self._request(messages, max_tokens=len(text) * 2, temperature=0.3)
        raw = self._validate_response(raw)
        filtered, _ = self._apply_safety_filters(raw)

        prompt_tokens = count_tokens(text, self._provider.model_name)
        completion_tokens = count_tokens(filtered, self._provider.model_name)
        cost = estimate_cost(
            prompt_tokens, completion_tokens, self._provider.model_name
        )

        return TranslationResult(
            translated_text=filtered,
            source_lang=source,
            target_lang=target,
            confidence=0.95,  # Heuristic; real confidence requires model logprobs
            usage=Usage(
                prompt_tokens=prompt_tokens,
                completion_tokens=completion_tokens,
                total_tokens=prompt_tokens + completion_tokens,
                estimated_cost=cost,
            ),
        )
