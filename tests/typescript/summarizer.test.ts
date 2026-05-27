/**
 * Tests for the Summarizer module.
 */

import { describe, it, expect } from "vitest";
import { SafetyFilter } from "../../typescript/src/safety.js";
import { countTokens, estimateCost } from "../../typescript/src/utils/token-counter.js";

describe("Summarizer", () => {
  const longText =
    "Artificial intelligence has transformed healthcare, finance, and customer service. " +
    "AI diagnostic tools rival trained physicians. Machine learning detects fraud in real time. " +
    "NLP powers multilingual assistants. Ethical concerns about bias remain.";

  it("should count tokens for long text", () => {
    const tokens = countTokens(longText);
    expect(tokens).toBeGreaterThan(20);
    expect(tokens).toBeLessThan(500);
  });

  it("should estimate cost for summarization", () => {
    const cost = estimateCost("gpt-4o", 200, 50);
    expect(cost).toBeGreaterThan(0);
    expect(cost).toBeLessThan(1);
  });

  it("should not flag clean summary output", () => {
    const filter = new SafetyFilter("medium");
    const result = filter.checkOutput("AI transforms healthcare and finance.");
    expect(result.isSafe).toBe(true);
  });

  it("should detect PII in summary output", () => {
    const filter = new SafetyFilter("medium");
    const result = filter.checkOutput("Contact john@example.com for the report.");
    expect(result.isSafe).toBe(false);
    expect(result.flags).toContain("pii_email");
  });

  it("should redact PII in high safety mode", () => {
    const filter = new SafetyFilter("high");
    const result = filter.checkOutput("Email: test@example.com");
    expect(result.filteredText).toContain("[REDACTED_EMAIL]");
  });
});
