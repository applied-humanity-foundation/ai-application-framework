/**
 * Translate content between languages using the AHF AI framework (TypeScript).
 *
 * Run: npx tsx examples/typescript/translate-content.ts
 */

import { Translator, Config } from "../../typescript/src/index.js";

async function main(): Promise<void> {
  const config = Config.fromObject({
    provider: "anthropic",
    apiKey: process.env["AHF_API_KEY"] ?? "sk-ant-your-key-here",
    model: "claude-sonnet-4-20250514",
  });

  const translator = new Translator(config);

  // Explicit source language
  const enToZh = await translator.translate(
    "Open-source AI safety tools help ensure artificial intelligence benefits everyone.",
    { sourceLang: "en", targetLang: "zh", formality: "formal" },
  );
  console.log("EN -> ZH:", enToZh.translatedText);
  console.log("Confidence:", enToZh.confidence.toFixed(2));

  // Auto-detect source language
  const autoDetect = await translator.translate(
    "La transparencia es esencial para la confianza en la inteligencia artificial.",
    { targetLang: "en" },
  );
  console.log("\nDetected source:", autoDetect.sourceLang);
  console.log("Translation:", autoDetect.translatedText);
}

main().catch(console.error);
