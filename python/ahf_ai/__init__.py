"""AHF AI Application Framework -- by Applied Humanity Foundation.

A provider-agnostic Python toolkit for text generation, summarization,
translation, and classification with built-in safety filtering, rate
limiting, and structured logging.

Example::

    from ahf_ai import TextGenerator, Config

    config = Config(provider="openai", api_key="sk-...")
    gen = TextGenerator(config)
    result = await gen.generate("Explain gravity in one sentence.")
    print(result.text)
"""

from __future__ import annotations

from ahf_ai.classifier import Classifier
from ahf_ai.config import Config
from ahf_ai.generator import TextGenerator
from ahf_ai.summarizer import Summarizer
from ahf_ai.translator import Translator

__version__: str = "0.1.0"
__author__: str = "Applied Humanity Foundation"
__license__: str = "Apache-2.0"

__all__ = [
    "Classifier",
    "Config",
    "Summarizer",
    "TextGenerator",
    "Translator",
    "__version__",
]
