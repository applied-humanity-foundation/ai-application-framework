/**
 * Classifier -- classify text into user-defined categories
 * with confidence scores for each.
 */

import { BaseClient } from "./client.js";
import type { ClassificationResult, CategoryScore, Message } from "./types/index.js";
import { countTokens, estimateCost } from "./utils/token-counter.js";

export class Classifier extends BaseClient {
  /**
   * Classify text into the given categories.
   * Returns all categories with confidence scores, sorted descending.
   */
  async classify(text: string, categories: string[]): Promise<ClassificationResult> {
    if (categories.length === 0) {
      throw new Error("At least one category is required");
    }

    const categoryList = categories.map((c) => `"${c}"`).join(", ");
    const systemPrompt =
      `You are a text classifier. Classify the following text into these categories: [${categoryList}]. ` +
      `Reply with ONLY a JSON object: {"scores": [{"name": "...", "confidence": 0.0-1.0}, ...]}. ` +
      `Confidence values must sum to 1.0.`;

    const messages: Message[] = [
      { role: "system", content: systemPrompt },
      { role: "user", content: text },
    ];

    const raw = await this.request(messages);
    this.validateResponse(raw.text);

    let scores: CategoryScore[];
    try {
      const parsed = JSON.parse(raw.text) as { scores: CategoryScore[] };
      scores = parsed.scores.sort((a, b) => b.confidence - a.confidence);
    } catch {
      // Fallback: equal distribution
      const equal = 1 / categories.length;
      scores = categories.map((name) => ({ name, confidence: equal }));
    }

    const topCategory = scores[0]?.name ?? categories[0] ?? "";
    const promptTokens = raw.promptTokens || countTokens(text);
    const completionTokens = raw.completionTokens || countTokens(raw.text);

    return {
      categories: scores,
      topCategory,
      usage: {
        promptTokens,
        completionTokens,
        totalTokens: promptTokens + completionTokens,
        estimatedCost: estimateCost(this.config.model, promptTokens, completionTokens),
      },
    };
  }
}
