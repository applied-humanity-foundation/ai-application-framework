"""Summarize a long article using the AHF AI framework.

Demonstrates paragraph and bullet-point summary formats
with configurable maximum length.
"""

import asyncio
from ahf_ai import Summarizer, Config

ARTICLE = """
Artificial intelligence has transformed numerous industries over the past decade.
In healthcare, AI-powered diagnostic tools can detect diseases from medical images
with accuracy rivaling trained physicians. The financial sector uses machine learning
models for fraud detection, processing millions of transactions in real time.
Natural language processing has enabled conversational assistants that handle
customer service inquiries across dozens of languages. However, these advances
also raise ethical concerns about bias, transparency, and job displacement.
Researchers and policymakers are working together to develop governance frameworks
that ensure AI systems are fair, accountable, and beneficial to society as a whole.
"""

async def main() -> None:
    config = Config(
        provider="openai",
        api_key="sk-your-api-key-here",
        model="gpt-4o",
    )

    summarizer = Summarizer(config)

    # Paragraph summary
    result = await summarizer.summarize(ARTICLE, max_length=50, format="paragraph")
    print("=== Paragraph Summary ===")
    print(result.summary)
    print(f"Compression: {result.original_length} -> {result.compressed_length} chars\n")

    # Bullet-point summary
    result = await summarizer.summarize(ARTICLE, max_length=60, format="bullets")
    print("=== Bullet Summary ===")
    print(result.summary)

if __name__ == "__main__":
    asyncio.run(main())
