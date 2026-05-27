/**
 * Anthropic Messages API provider implementation.
 *
 * Uses raw fetch against the /v1/messages endpoint with
 * the x-api-key header rather than Bearer auth.
 */

import type { Message } from "../types/index.js";
import { BaseProvider, type StreamChunk } from "./base.js";

export class AnthropicProvider extends BaseProvider {
  readonly modelName: string;
  readonly maxContextLength: number;
  private readonly apiKey: string;
  private readonly baseUrl: string;

  constructor(apiKey: string, model = "claude-sonnet-4-20250514", baseUrl = "https://api.anthropic.com") {
    super();
    this.apiKey = apiKey;
    this.modelName = model;
    this.baseUrl = baseUrl;
    this.maxContextLength = 200_000;
  }

  private headers(): Record<string, string> {
    return {
      "Content-Type": "application/json",
      "x-api-key": this.apiKey,
      "anthropic-version": "2023-06-01",
    };
  }

  async complete(messages: Message[]): Promise<{
    text: string;
    promptTokens: number;
    completionTokens: number;
    finishReason: string;
  }> {
    const systemMsg = messages.find((m) => m.role === "system");
    const nonSystem = messages.filter((m) => m.role !== "system");
    const body: Record<string, unknown> = {
      model: this.modelName,
      max_tokens: 4096,
      messages: nonSystem,
    };
    if (systemMsg) body["system"] = systemMsg.content;

    const res = await fetch(`${this.baseUrl}/v1/messages`, {
      method: "POST",
      headers: this.headers(),
      body: JSON.stringify(body),
    });
    if (!res.ok) throw await this.formatError(res);

    const data = await res.json() as {
      content: { text: string }[];
      stop_reason: string;
      usage: { input_tokens: number; output_tokens: number };
    };
    return {
      text: data.content.map((c) => c.text).join(""),
      promptTokens: data.usage.input_tokens,
      completionTokens: data.usage.output_tokens,
      finishReason: data.stop_reason === "end_turn" ? "stop" : data.stop_reason,
    };
  }

  async *stream(messages: Message[]): AsyncIterableIterator<StreamChunk> {
    const systemMsg = messages.find((m) => m.role === "system");
    const nonSystem = messages.filter((m) => m.role !== "system");
    const body: Record<string, unknown> = {
      model: this.modelName,
      max_tokens: 4096,
      messages: nonSystem,
      stream: true,
    };
    if (systemMsg) body["system"] = systemMsg.content;

    const res = await fetch(`${this.baseUrl}/v1/messages`, {
      method: "POST",
      headers: this.headers(),
      body: JSON.stringify(body),
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
        if (!line.startsWith("data: ")) continue;
        const parsed = JSON.parse(line.slice(6)) as { type: string; delta?: { text?: string } };
        if (parsed.type === "content_block_delta" && parsed.delta?.text) {
          yield { text: parsed.delta.text, done: false };
        }
        if (parsed.type === "message_stop") {
          yield { text: "", done: true };
        }
      }
    }
  }
}
