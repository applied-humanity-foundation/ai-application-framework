/**
 * BaseClient -- shared HTTP logic, retry handling, and safety filtering
 * used by all high-level framework classes (TextGenerator, Summarizer, etc.).
 */

import { Config } from "./config.js";
import { SafetyFilter } from "./safety.js";
import { getProvider, type BaseProvider } from "./providers/index.js";
import { RateLimiter } from "./utils/rate-limiter.js";
import { Logger } from "./utils/logger.js";
import type { SafetyResult, Message } from "./types/index.js";

const MAX_RETRIES = 3;
const RETRY_BASE_MS = 500;

export class BaseClient {
  protected readonly config: Config;
  protected readonly provider: BaseProvider;
  protected readonly safety: SafetyFilter;
  protected readonly rateLimiter: RateLimiter;
  protected readonly logger: Logger;

  constructor(config: Config) {
    this.config = config;
    this.provider = getProvider(config.provider, config.apiKey, config.model, config.baseUrl);
    this.safety = new SafetyFilter(config.safetyLevel);
    this.rateLimiter = new RateLimiter(config.rateLimitRpm);
    this.logger = new Logger(config.verbose ? "debug" : "info");
  }

  /**
   * Send a request to the provider with automatic retry and rate limiting.
   */
  protected async request(messages: Message[]): Promise<{
    text: string;
    promptTokens: number;
    completionTokens: number;
    finishReason: string;
  }> {
    let lastError: Error | undefined;

    for (let attempt = 0; attempt < MAX_RETRIES; attempt++) {
      try {
        await this.rateLimiter.acquire();
        this.logger.debug(`Request attempt ${attempt + 1}`, { model: this.config.model });
        const result = await this.provider.complete(messages);
        this.logger.info("Request completed", { tokens: result.promptTokens + result.completionTokens });
        return result;
      } catch (err) {
        lastError = err instanceof Error ? err : new Error(String(err));
        this.logger.warn(`Attempt ${attempt + 1} failed: ${lastError.message}`);
        if (attempt < MAX_RETRIES - 1) {
          const delay = RETRY_BASE_MS * Math.pow(2, attempt);
          await new Promise<void>((r) => setTimeout(r, delay));
        }
      }
    }
    throw lastError ?? new Error("Request failed after retries");
  }

  protected validateResponse(text: string): void {
    if (typeof text !== "string") {
      throw new Error("Invalid response: expected string");
    }
  }

  protected applySafetyFilters(text: string): { text: string; safetyResult: SafetyResult } {
    const result = this.safety.checkOutput(text);
    return {
      text: result.filteredText ?? text,
      safetyResult: result,
    };
  }
}
