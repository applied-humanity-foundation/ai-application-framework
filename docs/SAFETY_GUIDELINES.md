# Safety Guidelines

## Overview

The AHF AI Application Framework includes a built-in safety pipeline that runs on every request. It covers two stages: **input validation** (before the prompt reaches the provider) and **output filtering** (before the response reaches the caller).

## Safety Levels

| Level | Input Checks | Output Checks | PII Redaction |
|-------|-------------|---------------|---------------|
| `none` | Disabled | Disabled | No |
| `low` | Disabled | PII detection only | No |
| `medium` | Prompt injection detection | PII detection | No |
| `high` | Prompt injection detection | PII detection | Yes -- automatic |
| `maximum` | Prompt injection + content moderation | PII detection + content filtering | Yes -- automatic |

The default level is `medium`.

## Input Safety

### Prompt Injection Detection

The input filter scans for known prompt injection phrases such as:
- "ignore previous instructions"
- "ignore all previous"
- "disregard your instructions"
- "override safety"

When detected at `medium` or above, the request is blocked and a `GenerationResult` with `finishReason: "safety"` is returned immediately. No API call is made.

## Output Safety

### PII Detection

The output filter uses regex patterns to detect personally identifiable information:

| Pattern | Example Match |
|---------|--------------|
| Email | `user@example.com` |
| Phone (US) | `555-123-4567`, `(555) 123-4567` |
| SSN | `123-45-6789` |
| Credit card | `4111 1111 1111 1111` |
| IP address | `192.168.1.1` |

At `high` and `maximum` levels, detected PII is automatically replaced with `[REDACTED_TYPE]` (e.g., `[REDACTED_EMAIL]`). At `low` and `medium` levels, PII is flagged but not redacted.

## Configuration

### TypeScript

```typescript
import { Config, TextGenerator } from "@ahf/ai-framework";

const config = new Config({
  provider: "openai",
  apiKey: "sk-...",
  safetyLevel: "high",  // Enable automatic PII redaction
});

const generator = new TextGenerator(config);
```

### Python

```python
from ahf_ai import Config, TextGenerator

config = Config(
    provider="openai",
    api_key="sk-...",
    safety_level="high",
)
generator = TextGenerator(config)
```

## Custom Safety Rules

To extend the safety filter with custom patterns or rules:

1. Subclass `SafetyFilter` (TypeScript) or the safety module (Python).
2. Override `checkInput()` or `checkOutput()` to add domain-specific logic.
3. Return a `SafetyResult` with appropriate flags and details.

## Recommendations

- Use `medium` for general-purpose applications.
- Use `high` or `maximum` when handling user-submitted content that may contain PII.
- Use `none` only in controlled testing environments with synthetic data.
- Always log safety events for audit purposes using the built-in `Logger`.
