"""Basic text generation example using the AHF AI framework.

Demonstrates how to configure a provider and generate text
with safety filters enabled.
"""

import asyncio
from ahf_ai import TextGenerator, Config

async def main() -> None:
    # Create a configuration pointing at the desired provider.
    # In production, use Config.from_env() to read AHF_API_KEY, etc.
    config = Config(
        provider="openai",
        api_key="sk-your-api-key-here",
        model="gpt-4o",
        temperature=0.7,
        max_tokens=512,
        safety_level="medium",
    )

    # Instantiate the generator and produce text
    generator = TextGenerator(config)
    result = await generator.generate(
        prompt="Explain the importance of open-source AI safety tools in three sentences.",
        system_prompt="You are a concise technical writer.",
    )

    print(f"Generated text:\n{result.text}")
    print(f"\nTokens used: {result.usage.total_tokens}")
    print(f"Estimated cost: ${result.usage.estimated_cost:.6f}")
    print(f"Safety filtered: {result.safety_filtered}")

if __name__ == "__main__":
    asyncio.run(main())
