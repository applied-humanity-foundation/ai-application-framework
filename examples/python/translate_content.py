"""Translate content between languages using the AHF AI framework.

Demonstrates English-to-Chinese translation with formality control
and automatic source-language detection.
"""

import asyncio
from ahf_ai import Translator, Config

async def main() -> None:
    config = Config(
        provider="anthropic",
        api_key="sk-ant-your-api-key-here",
        model="claude-sonnet-4-20250514",
    )

    translator = Translator(config)

    # Explicit source language
    result = await translator.translate(
        text="Open-source AI safety tools help ensure that artificial intelligence benefits everyone.",
        source_lang="en",
        target_lang="zh",
        formality="formal",
    )
    print(f"Translation (EN -> ZH): {result.translated_text}")
    print(f"Confidence: {result.confidence:.2f}\n")

    # Auto-detect source language
    result = await translator.translate(
        text="La transparencia es esencial para la confianza en la inteligencia artificial.",
        target_lang="en",
    )
    print(f"Detected source: {result.source_lang}")
    print(f"Translation: {result.translated_text}")

if __name__ == "__main__":
    asyncio.run(main())
