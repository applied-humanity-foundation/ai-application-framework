/**
 * Classify text into categories using the AHF AI framework (TypeScript).
 *
 * Run: npx tsx examples/typescript/classify-text.ts
 */

import { Classifier, Config } from "../../typescript/src/index.js";

const CATEGORIES = ["technology", "science", "politics", "sports", "entertainment"];

const SAMPLES = [
  "The new GPU architecture delivers 40% faster inference for large language models.",
  "Researchers discovered a new species of deep-sea fish near hydrothermal vents.",
  "The president signed an executive order on renewable energy incentives.",
];

async function main(): Promise<void> {
  const config = Config.fromObject({
    provider: "openai",
    apiKey: process.env["AHF_API_KEY"] ?? "sk-your-key-here",
    model: "gpt-4o",
  });

  const classifier = new Classifier(config);

  for (const text of SAMPLES) {
    const result = await classifier.classify(text, CATEGORIES);
    console.log(`Text: ${text.slice(0, 60)}...`);
    console.log(`  Top: ${result.topCategory}`);
    for (const cat of result.categories.filter((c) => c.confidence >= 0.2)) {
      console.log(`    ${cat.name}: ${(cat.confidence * 100).toFixed(1)}%`);
    }
    console.log();
  }
}

main().catch(console.error);
