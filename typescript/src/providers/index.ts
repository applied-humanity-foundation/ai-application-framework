/**
 * Provider factory -- returns the correct provider instance
 * based on the config's provider field.
 */

import type { BaseProvider } from "./base.js";
import { OpenAIProvider } from "./openai.js";
import { AnthropicProvider } from "./anthropic.js";

export { BaseProvider } from "./base.js";
export { OpenAIProvider } from "./openai.js";
export { AnthropicProvider } from "./anthropic.js";

export function getProvider(
  provider: "openai" | "anthropic" | "custom",
  apiKey: string,
  model?: string,
  baseUrl?: string,
): BaseProvider {
  switch (provider) {
    case "openai":
      return new OpenAIProvider(apiKey, model, baseUrl);
    case "anthropic":
      return new AnthropicProvider(apiKey, model, baseUrl);
    case "custom":
      throw new Error(
        "Custom providers must be instantiated directly by extending BaseProvider.",
      );
  }
}
