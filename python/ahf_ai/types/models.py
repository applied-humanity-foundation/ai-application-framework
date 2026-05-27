"""Pydantic v2 data models for the AHF AI Application Framework.

All result types returned by framework components are defined here,
providing structured, validated outputs with serialization support.
"""

from __future__ import annotations

from typing import Optional

from pydantic import BaseModel, Field


class Usage(BaseModel):
    """Token usage statistics for an API call."""

    prompt_tokens: int = Field(ge=0, description="Tokens in the prompt")
    completion_tokens: int = Field(ge=0, description="Tokens in the completion")
    total_tokens: int = Field(ge=0, description="Total tokens consumed")
    estimated_cost: float = Field(
        default=0.0, ge=0.0, description="Estimated cost in USD"
    )

    def model_post_init(self, __context: object) -> None:
        """Auto-compute total if not explicitly set."""
        if self.total_tokens == 0 and (self.prompt_tokens or self.completion_tokens):
            object.__setattr__(
                self, "total_tokens", self.prompt_tokens + self.completion_tokens
            )


class GenerationResult(BaseModel):
    """Result from a text generation call."""

    text: str = Field(description="Generated text content")
    usage: Usage = Field(description="Token usage for this generation")
    model: str = Field(description="Model identifier used")
    finish_reason: str = Field(
        default="stop", description="Reason generation ended: stop, length, or safety"
    )
    safety_filtered: bool = Field(
        default=False, description="Whether safety filters were applied"
    )


class SummaryResult(BaseModel):
    """Result from a summarization call."""

    summary: str = Field(description="The generated summary text")
    original_length: int = Field(ge=0, description="Character count of original text")
    compressed_length: int = Field(ge=0, description="Character count of the summary")
    format: str = Field(
        default="paragraph", description="Output format: paragraph or bullets"
    )
    usage: Optional[Usage] = Field(default=None, description="Token usage if available")


class TranslationResult(BaseModel):
    """Result from a translation call."""

    translated_text: str = Field(description="The translated output")
    source_lang: str = Field(description="Detected or specified source language code")
    target_lang: str = Field(description="Target language code")
    confidence: float = Field(
        default=1.0, ge=0.0, le=1.0, description="Confidence in translation quality"
    )
    usage: Optional[Usage] = Field(default=None, description="Token usage if available")


class CategoryScore(BaseModel):
    """A single category with its confidence score."""

    name: str = Field(description="Category label")
    confidence: float = Field(
        ge=0.0, le=1.0, description="Model confidence for this category"
    )


class ClassificationResult(BaseModel):
    """Result from a classification call."""

    categories: list[CategoryScore] = Field(
        description="All categories with confidence scores, sorted descending"
    )
    top_category: str = Field(description="Highest-confidence category name")
    usage: Optional[Usage] = Field(default=None, description="Token usage if available")

    def above_threshold(self, threshold: float = 0.5) -> list[CategoryScore]:
        """Return only categories meeting the confidence threshold."""
        return [c for c in self.categories if c.confidence >= threshold]


class SafetyResult(BaseModel):
    """Result from a safety check."""

    is_safe: bool = Field(description="Whether the text passed all safety checks")
    flags: list[str] = Field(
        default_factory=list,
        description="List of safety flag identifiers triggered",
    )
    filtered_text: Optional[str] = Field(
        default=None,
        description="Text with unsafe content redacted, if applicable",
    )
    details: dict[str, str] = Field(
        default_factory=dict,
        description="Additional details per flag",
    )
