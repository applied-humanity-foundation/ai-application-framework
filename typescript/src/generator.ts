/**
 * TextGenerator -- high-level text generation with safety filters
 * and optional streaming support.
 */

import { BaseClient } from "./client.js";
import { countTokens, estimateCost } from "./utils/token-counter.js";
import type { GenerateOptions, GenerationResult, Message } from "./types/index.js";

export class TextGenerator extends BaseClient {
  /**
   * Generate text from a prompt. Returns the full result once complete.
   */
  async generate(options: GenerateOptions): Promise<GenerationResult> {
    // Safety-check the input
    const inputCheck = this.safety.checkInput(options.prompt);
    if (!inputCheck.isSafe) {
      return {
        text: "",
        usage: { promptTokens: 0, completionTokens: 0, totalTokens: 0, estimatedCost: 0 },
        model: this.config.model,
        finishReason: "safety",
        safetyFiltered: true,
      };
    }

    const messages: Message[] = [];
    if (options.systemPrompt) {
      messages.push({ role: "system", content: options.systemPrompt });
    }
    messages.push({ role: "user", content: options.prompt });

    const raw = await this.request(messages);
    this.validateResponse(raw.text);

    // Safety-check the output
    const { text, safetyResult } = this.applySafetyFilters(raw.text);
    const promptTokens = raw.promptTokens || countTokens(options.prompt);
    const completionTokens = raw.completionTokens || countTokens(text);
    const totalTokens = promptTokens + completionTokens;

    return {
      text,
      usage: {
        promptTokens,
        completionTokens,
        totalTokens,
        estimatedCost: estimateCost(this.config.model, promptTokens, completionTokens),
      },
      model: this.config.model,
      finishReason: raw.finishReason === "stop" ? "stop" : raw.finishReason === "length" ? "length" : "stop",
      safetyFiltered: !safetyResult.isSafe,
    };
  }

  /**
   * Stream generated text token-by-token.
   */
  async *stream(options: GenerateOptions): AsyncIterableIterator<string> {
    const inputCheck = this.safety.checkInput(options.prompt);
    if (!inputCheck.isSafe) {
      return;
    }

    const messages: Message[] = [];
    if (options.systemPrompt) {
      messages.push({ role: "system", content: options.systemPrompt });
    }
    messages.push({ role: "user", content: options.prompt });

    await this.rateLimiter.acquire();
    const chunks = this.provider.stream(messages);

    for await (const chunk of chunks) {
      if (chunk.text) {
        yield chunk.text;
      }
      if (chunk.done) break;
    }
  }
}
