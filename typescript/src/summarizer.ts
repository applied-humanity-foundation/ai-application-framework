/**
 * Summarizer -- condense long text into shorter summaries,
 * supporting paragraph and bullet-point output formats.
 */

import { BaseClient } from "./client.js";
import type { SummaryOptions, SummaryResult, Message } from "./types/index.js";
import { countTokens, estimateCost } from "./utils/token-counter.js";

const DEFAULT_MAX_LENGTH = 200;

export class Summarizer extends BaseClient {
  /**
   * Summarize the given text according to the provided options.
   */
  async summarize(text: string, options?: SummaryOptions): Promise<SummaryResult> {
    const format = options?.format ?? "paragraph";
    const maxLength = options?.maxLength ?? DEFAULT_MAX_LENGTH;

    const formatInstruction = format === "bullets"
      ? "Use bullet points."
      : "Write a single concise paragraph.";

    const systemPrompt =
      `You are a precise summarizer. Summarize the following text in at most ${maxLength} words. ${formatInstruction} Output ONLY the summary.`;

    const messages: Message[] = [
      { role: "system", content: systemPrompt },
      { role: "user", content: text },
    ];

    const raw = await this.request(messages);
    this.validateResponse(raw.text);
    const { text: safeText } = this.applySafetyFilters(raw.text);

    const promptTokens = raw.promptTokens || countTokens(text);
    const completionTokens = raw.completionTokens || countTokens(safeText);

    return {
      summary: safeText,
      originalLength: text.length,
      compressedLength: safeText.length,
      format,
      usage: {
        promptTokens,
        completionTokens,
        totalTokens: promptTokens + completionTokens,
        estimatedCost: estimateCost(this.config.model, promptTokens, completionTokens),
      },
    };
  }
}
