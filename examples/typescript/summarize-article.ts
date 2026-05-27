/**
 * Summarize an article using the AHF AI framework (TypeScript).
 *
 * Run: npx tsx examples/typescript/summarize-article.ts
 */

import { Summarizer, Config } from "../../typescript/src/index.js";

const ARTICLE = `
Artificial intelligence has transformed numerous industries over the past decade.
In healthcare, AI-powered diagnostic tools can detect diseases from medical images
with accuracy rivaling trained physicians. The financial sector uses machine learning
models for fraud detection, processing millions of transactions in real time.
Natural language processing has enabled conversational assistants that handle
customer service inquiries across dozens of languages. However, these advances
also raise ethical concerns about bias, transparency, and job displacement.
`;

async function main(): Promise<void> {
  const config = Config.fromObject({
    provider: "openai",
    apiKey: process.env["AHF_API_KEY"] ?? "sk-your-key-here",
    model: "gpt-4o",
  });

  const summarizer = new Summarizer(config);

  const paragraph = await summarizer.summarize(ARTICLE, { format: "paragraph", maxLength: 50 });
  console.log("=== Paragraph Summary ===");
  console.log(paragraph.summary);
  console.log(`Compression: ${paragraph.originalLength} -> ${paragraph.compressedLength} chars\n`);

  const bullets = await summarizer.summarize(ARTICLE, { format: "bullets", maxLength: 60 });
  console.log("=== Bullet Summary ===");
  console.log(bullets.summary);
}

main().catch(console.error);
