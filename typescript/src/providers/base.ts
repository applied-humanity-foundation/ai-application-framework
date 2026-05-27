/**
 * Abstract base provider interface for LLM backends.
 *
 * All concrete providers (OpenAI, Anthropic, etc.) implement this
 * interface so the framework can swap providers transparently.
 */

import type { Message } from "../types/index.js";

export interface StreamChunk {
  text: string;
  done: boolean;
}

export abstract class BaseProvider {
  abstract readonly modelName: string;
  abstract readonly maxContextLength: number;

  /**
   * Send a completion request and return the full response text.
   */
  abstract complete(messages: Message[]): Promise<{
    text: string;
    promptTokens: number;
    completionTokens: number;
    finishReason: string;
  }>;

  /**
   * Stream a completion, yielding text chunks as they arrive.
   */
  abstract stream(messages: Message[]): AsyncIterableIterator<StreamChunk>;

  /**
   * Build a fetch-compatible headers object including auth.
   */
  protected buildHeaders(apiKey: string, extra?: Record<string, string>): Record<string, string> {
    return {
      "Content-Type": "application/json",
      ...extra,
      Authorization: `Bearer ${apiKey}`,
    };
  }

  /**
   * Format an error from a non-OK HTTP response.
   */
  protected async formatError(response: Response): Promise<Error> {
    const body = await response.text().catch(() => "unknown error");
    return new Error(`Provider API error ${response.status}: ${body}`);
  }
}
