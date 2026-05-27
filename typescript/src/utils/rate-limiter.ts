/**
 * Token-bucket rate limiter for controlling API request throughput.
 *
 * Tokens refill at a constant rate. If the bucket is empty,
 * acquire() waits until a token is available.
 */

export class RateLimiter {
  private tokens: number;
  private readonly maxTokens: number;
  private readonly refillIntervalMs: number;
  private lastRefill: number;

  constructor(requestsPerMinute: number) {
    this.maxTokens = requestsPerMinute;
    this.tokens = requestsPerMinute;
    this.refillIntervalMs = 60_000 / requestsPerMinute;
    this.lastRefill = Date.now();
  }

  private refill(): void {
    const now = Date.now();
    const elapsed = now - this.lastRefill;
    const newTokens = Math.floor(elapsed / this.refillIntervalMs);
    if (newTokens > 0) {
      this.tokens = Math.min(this.maxTokens, this.tokens + newTokens);
      this.lastRefill = now;
    }
  }

  async acquire(): Promise<void> {
    this.refill();
    if (this.tokens > 0) {
      this.tokens--;
      return;
    }
    // Wait for the next token to become available
    const waitMs = this.refillIntervalMs - (Date.now() - this.lastRefill);
    await new Promise<void>((resolve) => setTimeout(resolve, Math.max(0, waitMs)));
    this.refill();
    this.tokens--;
  }

  get availableTokens(): number {
    this.refill();
    return this.tokens;
  }
}
