/**
 * Translator -- translate text between languages with
 * optional formality control and auto-detection of source language.
 */

import { BaseClient } from "./client.js";
import type { TranslationOptions, TranslationResult, Message } from "./types/index.js";
import { countTokens, estimateCost } from "./utils/token-counter.js";

export class Translator extends BaseClient {
  /**
   * Translate text to the target language.
   * If sourceLang is omitted, the model auto-detects it.
   */
  async translate(text: string, options: TranslationOptions): Promise<TranslationResult> {
    const { targetLang, sourceLang, formality } = options;

    let formalityNote = "";
    if (formality === "formal") formalityNote = " Use formal register.";
    else if (formality === "informal") formalityNote = " Use informal register.";

    const detectClause = sourceLang
      ? `from ${sourceLang}`
      : "(auto-detect the source language)";

    const systemPrompt =
      `You are a professional translator. Translate the text ${detectClause} to ${targetLang}.${formalityNote} ` +
      `Reply with ONLY a JSON object: {"translated_text": "...", "source_lang": "...", "confidence": 0.0-1.0}`;

    const messages: Message[] = [
      { role: "system", content: systemPrompt },
      { role: "user", content: text },
    ];

    const raw = await this.request(messages);
    this.validateResponse(raw.text);

    // Parse the structured response
    let parsed: { translated_text: string; source_lang: string; confidence: number };
    try {
      parsed = JSON.parse(raw.text) as typeof parsed;
    } catch {
      // Fallback: treat the entire response as translated text
      parsed = { translated_text: raw.text, source_lang: sourceLang ?? "unknown", confidence: 0.5 };
    }

    const { text: safeText } = this.applySafetyFilters(parsed.translated_text);
    const promptTokens = raw.promptTokens || countTokens(text);
    const completionTokens = raw.completionTokens || countTokens(safeText);

    return {
      translatedText: safeText,
      sourceLang: parsed.source_lang,
      targetLang,
      confidence: parsed.confidence,
      usage: {
        promptTokens,
        completionTokens,
        totalTokens: promptTokens + completionTokens,
        estimatedCost: estimateCost(this.config.model, promptTokens, completionTokens),
      },
    };
  }
}
