/**
 * Lightweight token counting and cost estimation utilities.
 *
 * Uses a heuristic approximation (1 token ~ 4 chars for English)
 * rather than requiring a full tokenizer dependency.
 */

const CHARS_PER_TOKEN = 4;

const COST_PER_1K: Record<string, { input: number; output: number }> = {
  "gpt-4o": { input: 0.005, output: 0.015 },
  "gpt-4o-mini": { input: 0.00015, output: 0.0006 },
  "claude-sonnet-4-20250514": { input: 0.003, output: 0.015 },
  "claude-haiku-4-20250414": { input: 0.0008, output: 0.004 },
};

export function countTokens(text: string): number {
  // Heuristic: ~4 characters per token for English text.
  // CJK characters count roughly as 1 token each.
  const cjkCount = (text.match(/[一-鿿぀-ヿ가-힯]/g) ?? []).length;
  const nonCjkLength = text.length - cjkCount;
  return Math.ceil(nonCjkLength / CHARS_PER_TOKEN) + cjkCount;
}

export function estimateCost(
  model: string,
  promptTokens: number,
  completionTokens: number,
): number {
  const pricing = COST_PER_1K[model];
  if (!pricing) {
    return 0;
  }
  const inputCost = (promptTokens / 1000) * pricing.input;
  const outputCost = (completionTokens / 1000) * pricing.output;
  return Math.round((inputCost + outputCost) * 1_000_000) / 1_000_000;
}
