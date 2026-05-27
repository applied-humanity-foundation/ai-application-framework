/**
 * OpenAI-compatible provider implementation.
 *
 * Uses the chat completions API via raw fetch so the framework
 * has zero runtime dependency on the openai npm package.
 */

import type { Message } from "../types/index.js";
import { BaseProvider, type StreamChunk } from "./base.js";

export class OpenAIProvider extends BaseProvider {
  readonly modelName: string;
  readonly maxContextLength: number;
  private readonly apiKey: string;
  private readonly baseUrl: string;

  constructor(apiKey: string, model = "gpt-4o", baseUrl = "https://api.openai.com/v1") {
    super();
    this.apiKey = apiKey;
    this.modelName = model;
    this.baseUrl = baseUrl;
    this.maxContextLength = model.includes("gpt-4o") ? 128_000 : 8_192;
  }

  async complete(messages: Message[]): Promise<{
    text: string;
    promptTokens: number;
    completionTokens: number;
    finishReason: string;
  }> {
    const res = await fetch(`${this.baseUrl}/chat/completions`, {
      method: "POST",
      headers: this.buildHeaders(this.apiKey),
      body: JSON.stringify({ model: this.modelName, messages }),
    });
    if (!res.ok) throw await this.formatError(res);

    const data = await res.json() as {
      choices: { message: { content: string }; finish_reason: string }[];
      usage: { prompt_tokens: number; completion_tokens: number };
    };
    const choice = data.choices[0];
    return {
      text: choice?.message.content ?? "",
      promptTokens: data.usage.prompt_tokens,
      completionTokens: data.usage.completion_tokens,
      finishReason: choice?.finish_reason ?? "stop",
    };
  }

  async *stream(messages: Message[]): AsyncIterableIterator<StreamChunk> {
    const res = await fetch(`${this.baseUrl}/chat/completions`, {
      method: "POST",
      headers: this.buildHeaders(this.apiKey),
      body: JSON.stringify({ model: this.modelName, messages, stream: true }),
    });
    if (!res.ok) throw await this.formatError(res);
    if (!res.body) throw new Error("Response body is null");

    const reader = res.body.getReader();
    const decoder = new TextDecoder();
    let buffer = "";

    while (true) {
      const { done, value } = await reader.read();
      if (done) break;
      buffer += decoder.decode(value, { stream: true });
      const lines = buffer.split("\n");
      buffer = lines.pop() ?? "";
      for (const line of lines) {
        const trimmed = line.replace(/^data: /, "").trim();
        if (!trimmed || trimmed === "[DONE]") continue;
        const parsed = JSON.parse(trimmed) as { choices: { delta: { content?: string }; finish_reason?: string }[] };
        const delta = parsed.choices[0]?.delta.content ?? "";
        const finished = parsed.choices[0]?.finish_reason != null;
        if (delta) yield { text: delta, done: finished };
      }
    }
  }
}
