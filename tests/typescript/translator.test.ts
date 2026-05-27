/**
 * Tests for the Translator module.
 */

import { describe, it, expect } from "vitest";
import { Config } from "../../typescript/src/config.js";
import { countTokens } from "../../typescript/src/utils/token-counter.js";
import { RateLimiter } from "../../typescript/src/utils/rate-limiter.js";

describe("Translator", () => {
  it("should count CJK tokens correctly", () => {
    // CJK characters should each count as ~1 token
    const tokens = countTokens("人工智能安全");
    expect(tokens).toBe(6);
  });

  it("should count mixed-language tokens", () => {
    const tokens = countTokens("AI安全 is important");
    expect(tokens).toBeGreaterThan(3);
  });

  it("should create config for anthropic provider", () => {
    const config = new Config({
      provider: "anthropic",
      apiKey: "sk-ant-test",
      model: "claude-sonnet-4-20250514",
    });
    expect(config.provider).toBe("anthropic");
    expect(config.model).toBe("claude-sonnet-4-20250514");
  });

  it("should respect rate limits", async () => {
    const limiter = new RateLimiter(120); // 120 RPM
    expect(limiter.availableTokens).toBe(120);
    await limiter.acquire();
    expect(limiter.availableTokens).toBe(119);
  });

  it("should handle zero-cost for unknown models", () => {
    const { estimateCost } = await import("../../typescript/src/utils/token-counter.js");
    const cost = estimateCost("unknown-model-xyz", 100, 50);
    expect(cost).toBe(0);
  });
});
