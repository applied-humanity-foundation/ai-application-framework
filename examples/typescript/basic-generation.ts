/**
 * Basic text generation example using the AHF AI framework (TypeScript).
 *
 * Run: npx tsx examples/typescript/basic-generation.ts
 */

import { TextGenerator, Config } from "../../typescript/src/index.js";

async function main(): Promise<void> {
  const config = Config.fromObject({
    provider: "openai",
    apiKey: process.env["AHF_API_KEY"] ?? "sk-your-key-here",
    model: "gpt-4o",
    temperature: 0.7,
    maxTokens: 512,
    safetyLevel: "medium",
  });

  const generator = new TextGenerator(config);

  // Full generation
  const result = await generator.generate({
    prompt: "Explain the importance of open-source AI safety tools in three sentences.",
    systemPrompt: "You are a concise technical writer.",
  });

  console.log("Generated text:", result.text);
  console.log("Tokens used:", result.usage.totalTokens);
  console.log("Estimated cost: $" + result.usage.estimatedCost.toFixed(6));

  // Streaming generation
  console.log("\nStreaming output:");
  for await (const chunk of generator.stream({ prompt: "Count from 1 to 5." })) {
    process.stdout.write(chunk);
  }
  console.log();
}

main().catch(console.error);
