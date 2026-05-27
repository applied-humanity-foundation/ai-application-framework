# API Reference

## TextGenerator

### `generate(options: GenerateOptions): Promise<GenerationResult>`

Generate text from a prompt with safety filtering.

**Parameters (`GenerateOptions`):**
| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `prompt` | `string` | *required* | The user prompt |
| `systemPrompt` | `string?` | `undefined` | Optional system instruction |
| `temperature` | `number?` | `0.7` | Sampling temperature (0.0-2.0) |
| `maxTokens` | `number?` | `2048` | Maximum tokens to generate |
| `topP` | `number?` | `1.0` | Nucleus sampling threshold |
| `stopSequences` | `string[]?` | `[]` | Stop generation at these strings |

**Returns (`GenerationResult`):**
| Field | Type | Description |
|-------|------|-------------|
| `text` | `string` | Generated text |
| `usage` | `Usage` | Token counts and cost |
| `model` | `string` | Model identifier |
| `finishReason` | `"stop" \| "length" \| "safety"` | Why generation ended |
| `safetyFiltered` | `boolean` | Whether safety filters were applied |

### `stream(options: GenerateOptions): AsyncIterableIterator<string>`

Stream generated text token-by-token. Yields individual text chunks.

---

## Summarizer

### `summarize(text: string, options?: SummaryOptions): Promise<SummaryResult>`

Condense long text into a shorter summary.

**Parameters (`SummaryOptions`):**
| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `maxLength` | `number?` | `200` | Maximum words in the summary |
| `format` | `"paragraph" \| "bullets"` | `"paragraph"` | Output format |
| `language` | `string?` | `undefined` | Output language code |

**Returns (`SummaryResult`):**
| Field | Type | Description |
|-------|------|-------------|
| `summary` | `string` | The summary text |
| `originalLength` | `number` | Character count of the input |
| `compressedLength` | `number` | Character count of the summary |
| `format` | `string` | Format used |
| `usage` | `Usage?` | Token usage if available |

---

## Translator

### `translate(text: string, options: TranslationOptions): Promise<TranslationResult>`

Translate text to a target language with optional formality control.

**Parameters (`TranslationOptions`):**
| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `targetLang` | `string` | *required* | Target language code (e.g., `"zh"`, `"fr"`) |
| `sourceLang` | `string?` | auto-detect | Source language code |
| `formality` | `"formal" \| "informal" \| "neutral"` | `"neutral"` | Register |

**Returns (`TranslationResult`):**
| Field | Type | Description |
|-------|------|-------------|
| `translatedText` | `string` | The translated output |
| `sourceLang` | `string` | Detected or specified source language |
| `targetLang` | `string` | Target language code |
| `confidence` | `number` | Translation confidence (0.0-1.0) |
| `usage` | `Usage?` | Token usage if available |

---

## Classifier

### `classify(text: string, categories: string[]): Promise<ClassificationResult>`

Classify text into user-defined categories with confidence scores.

**Parameters:**
| Field | Type | Description |
|-------|------|-------------|
| `text` | `string` | Text to classify |
| `categories` | `string[]` | List of category labels (at least one) |

**Returns (`ClassificationResult`):**
| Field | Type | Description |
|-------|------|-------------|
| `categories` | `CategoryScore[]` | All categories with scores, sorted descending |
| `topCategory` | `string` | Highest-confidence category |
| `usage` | `Usage?` | Token usage if available |

**`CategoryScore`:**
| Field | Type | Description |
|-------|------|-------------|
| `name` | `string` | Category label |
| `confidence` | `number` | Confidence score (0.0-1.0) |

---

## Usage Type

All result types may include a `Usage` object:

| Field | Type | Description |
|-------|------|-------------|
| `promptTokens` | `number` | Tokens in the prompt |
| `completionTokens` | `number` | Tokens in the completion |
| `totalTokens` | `number` | Total tokens consumed |
| `estimatedCost` | `number` | Estimated cost in USD |
