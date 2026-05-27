# Providers

## Supported Providers

| Provider | Module | Auth Header | Default Model | Max Context |
|----------|--------|-------------|---------------|-------------|
| OpenAI | `providers/openai` | `Authorization: Bearer` | `gpt-4o` | 128k tokens |
| Anthropic | `providers/anthropic` | `x-api-key` | `claude-sonnet-4-20250514` | 200k tokens |

Both providers use raw `fetch` -- no SDK dependency required. This keeps the framework lightweight and avoids version conflicts.

## Provider Comparison

| Feature | OpenAI | Anthropic |
|---------|--------|-----------|
| Streaming | SSE (`data:` lines) | SSE (`data:` lines) |
| System prompt | `messages[0].role = "system"` | Top-level `system` field |
| Stop reason | `finish_reason: "stop"` | `stop_reason: "end_turn"` |
| Token counting | `usage.prompt_tokens` | `usage.input_tokens` |

## Configuration

### TypeScript

```typescript
import { Config, TextGenerator } from "@ahf/ai-framework";

// OpenAI
const openai = new Config({ provider: "openai", apiKey: "sk-..." });

// Anthropic
const anthropic = new Config({ provider: "anthropic", apiKey: "sk-ant-..." });

// Custom base URL (e.g., Azure OpenAI or local proxy)
const custom = new Config({
  provider: "openai",
  apiKey: "sk-...",
  baseUrl: "https://my-proxy.example.com/v1",
});
```

## Adding a Custom Provider

1. **Create the provider file** in `typescript/src/providers/` or `python/ahf_ai/providers/`.

2. **Extend `BaseProvider`** and implement the required methods:

```typescript
import { BaseProvider, StreamChunk } from "./base.js";
import { Message } from "../types/index.js";

export class MyProvider extends BaseProvider {
  readonly modelName = "my-model";
  readonly maxContextLength = 32_000;

  async complete(messages: Message[]) {
    // Make HTTP request to your API
    // Return { text, promptTokens, completionTokens, finishReason }
  }

  async *stream(messages: Message[]): AsyncIterableIterator<StreamChunk> {
    // Yield { text, done } chunks from your streaming API
  }
}
```

3. **Register in the factory** (`providers/index.ts`):

```typescript
case "my-provider":
  return new MyProvider(apiKey, model, baseUrl);
```

4. **Add tests** covering both `complete()` and `stream()` paths, including error responses (4xx, 5xx, timeouts).
