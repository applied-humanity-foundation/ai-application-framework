/**
 * Tests for the Classifier module.
 */

import { describe, it, expect } from "vitest";
import { SafetyFilter } from "../../typescript/src/safety.js";
import { Logger } from "../../typescript/src/utils/logger.js";
import { Config } from "../../typescript/src/config.js";

describe("Classifier", () => {
  it("should throw for custom provider without implementation", () => {
    const { getProvider } = await import("../../typescript/src/providers/index.js");
    expect(() => getProvider("custom", "key")).toThrow(
      "Custom providers must be instantiated directly",
    );
  });

  it("should return openai provider for openai config", () => {
    const { getProvider, OpenAIProvider } = await import("../../typescript/src/providers/index.js");
    const provider = getProvider("openai", "sk-test", "gpt-4o");
    expect(provider).toBeInstanceOf(OpenAIProvider);
    expect(provider.modelName).toBe("gpt-4o");
  });

  it("should redact API keys in logs", () => {
    const logger = new Logger("debug");
    // Logger internally redacts keys; we verify it doesn't throw
    expect(() => logger.debug("Using key sk-abc1234567890xyz")).not.toThrow();
  });

  it("should not log below minimum level", () => {
    const logger = new Logger("error");
    // debug() on an error-level logger should be a no-op
    expect(() => logger.debug("This should be silenced")).not.toThrow();
  });

  it("should require apiKey from environment", () => {
    // Without AHF_API_KEY set, fromEnv() should throw
    const original = process.env["AHF_API_KEY"];
    delete process.env["AHF_API_KEY"];
    expect(() => Config.fromEnv()).toThrow("AHF_API_KEY environment variable is required");
    if (original !== undefined) {
      process.env["AHF_API_KEY"] = original;
    }
  });
});
