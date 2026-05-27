"""Classify text into categories using the AHF AI framework.

Demonstrates multi-label classification with confidence scores
and threshold filtering.
"""

import asyncio
from ahf_ai import Classifier, Config

CATEGORIES = ["technology", "science", "politics", "sports", "entertainment"]

SAMPLE_TEXTS = [
    "The new GPU architecture delivers 40% faster inference for large language models.",
    "Researchers discovered a new species of deep-sea fish near hydrothermal vents.",
    "The president signed an executive order on renewable energy incentives.",
]

async def main() -> None:
    config = Config(
        provider="openai",
        api_key="sk-your-api-key-here",
        model="gpt-4o",
    )

    classifier = Classifier(config)

    for text in SAMPLE_TEXTS:
        result = await classifier.classify(text=text, categories=CATEGORIES)
        print(f"Text: {text[:60]}...")
        print(f"  Top category: {result.top_category}")
        # Show categories above 20% confidence
        above = result.above_threshold(0.2)
        for cat in above:
            print(f"    {cat.name}: {cat.confidence:.1%}")
        print()

if __name__ == "__main__":
    asyncio.run(main())
