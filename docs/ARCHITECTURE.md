# Architecture

## Overview

The AHF AI Application Framework provides a unified interface for text generation, summarization, translation, and classification across multiple LLM providers. All requests flow through a common safety pipeline before reaching the provider.

## System Diagram

```
                          +-------------------+
                          |   User Code       |
                          +--------+----------+
                                   |
          +------------------------+------------------------+
          |              |              |              |
   +------+------+ +-----+------+ +----+-------+ +----+------+
   | TextGenerator| | Summarizer | | Translator | | Classifier|
   +------+------+ +-----+------+ +----+-------+ +----+------+
          |              |              |              |
          +------------------------+------------------------+
                                   |
                          +--------+----------+
                          |    BaseClient     |
                          | - retry logic     |
                          | - rate limiting   |
                          | - safety filters  |
                          +--------+----------+
                                   |
                    +--------------+--------------+
                    |                             |
           +-------+--------+           +--------+-------+
           | OpenAIProvider  |           |AnthropicProvider|
           | (fetch-based)   |           | (fetch-based)  |
           +----------------+           +----------------+
```

## Component Responsibilities

### BaseClient
Shared HTTP logic used by all four high-level modules. Handles exponential-backoff retries (up to 3 attempts), token-bucket rate limiting, and pre/post safety filtering. All provider communication flows through `request()`.

### Providers
Each provider implements the abstract `BaseProvider` interface with two methods: `complete()` for synchronous responses and `stream()` for server-sent-event streaming. Providers use raw `fetch` -- no SDK dependencies required.

### Safety Pipeline
Every request passes through a two-stage safety filter:
1. **Input check** -- blocks prompt injection attempts and validates user input.
2. **Output check** -- scans for PII (emails, phone numbers, SSNs, credit cards) and optionally redacts detected patterns based on the configured safety level.

Safety levels: `none` | `low` | `medium` | `high` | `maximum`

### Rate Limiter
Token-bucket algorithm that refills at a constant rate derived from `rateLimitRpm`. Calls to `acquire()` block asynchronously when the bucket is empty.

### Logger
Structured JSON logger with automatic API key redaction. Supports `debug`, `info`, `warn`, `error` levels. Enabled at `debug` when `verbose: true`.

## Adding a New Provider

1. Create a new file in `typescript/src/providers/` (or `python/ahf_ai/providers/`).
2. Extend `BaseProvider` and implement `complete()` and `stream()`.
3. Register the provider in the `getProvider()` factory.
4. Add tests covering both success and error paths.
