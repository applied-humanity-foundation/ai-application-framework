<p align="center">
  <img src="https://appliedhumanityfoundation.org/favicon.svg" width="64" alt="Applied Humanity Foundation" />
</p>

<h1 align="center">AI Application Framework</h1>

<p align="center">
  <strong>Open-source tools for responsible AI integration in education and nonprofit applications</strong><br>
  Part of the <a href="https://appliedhumanityfoundation.org">Applied Humanity Foundation</a>
</p>

<p align="center">
  <a href="#features">Features</a> · <a href="#quick-start">Quick Start</a> · <a href="#api-reference">API Reference</a> · <a href="#contributing">Contributing</a>
</p>

---

## About

The AI Application Framework provides simple, safe, and well-documented tools for integrating publicly available AI systems into educational and nonprofit applications. Designed with responsible AI principles at its core, it makes advanced AI capabilities accessible to developers, educators, and researchers.

## Features

- **Unified API** — Single interface across multiple AI providers (OpenAI, Anthropic, Google, open-source models)
- **Responsible Defaults** — Built-in content safety filters, rate limiting, and usage monitoring
- **Education First** — Verbose logging mode that explains what's happening at each step
- **Type Safe** — Full Python type hints and TypeScript definitions
- **Privacy Focused** — No telemetry, no data collection, local-first when possible
- **Well Documented** — Comprehensive guides, examples, and API reference

## Quick Start

### Python

```python
from ahf_ai import TextGenerator, Summarizer, Translator

# Text generation with safety defaults
generator = TextGenerator(provider="openai")
response = generator.generate(
    prompt="Explain photosynthesis for a 10-year-old",
    max_tokens=200
)
print(response.text)

# Summarization
summarizer = Summarizer()
summary = summarizer.summarize(long_article, max_length=100)

# Translation
translator = Translator()
result = translator.translate("Hello, world!", target="zh")
```

### TypeScript

```typescript
import { TextGenerator, Summarizer } from '@ahf/ai-framework';

const generator = new TextGenerator({ provider: 'openai' });
const response = await generator.generate({
  prompt: 'Explain photosynthesis for a 10-year-old',
  maxTokens: 200,
});
console.log(response.text);
```

## API Modules

| Module | Description | Status |
|--------|-------------|--------|
| Text Generation | Generate text with configurable safety filters | Beta |
| Summarization | Condense long documents into key points | Beta |
| Translation | Translate between 20+ language pairs | Beta |
| Classification | Categorize text with confidence scores | Alpha |

## Use Cases

- **Classroom Tools** — Build AI-powered learning assistants for schools
- **Content Accessibility** — Auto-translate and summarize educational materials
- **Research** — Prototype NLP pipelines for academic research
- **Nonprofit Operations** — Automate document processing and communication

## Educational Purpose

This framework is developed as a public-interest educational resource by the Applied Humanity Foundation, a 501(c)(3) nonprofit organization. It is designed to teach responsible AI integration practices and is intended for educational, research, and nonprofit use.

This project does not provide AI models — it provides tools for responsibly using publicly available AI APIs and services.

## Contributing

We welcome contributions! Areas where help is needed:

- **New providers** — Add support for additional AI services
- **Documentation** — Improve guides and add tutorials
- **Safety filters** — Enhance content moderation capabilities
- **Testing** — Expand test coverage
- **Translation** — Localize documentation

## License

[MIT License](LICENSE) — free for everyone, forever.

## About Applied Humanity Foundation

[Applied Humanity Foundation](https://appliedhumanityfoundation.org) is a Colorado nonprofit corporation advancing human well-being through responsible AI application, open-source tools, and digital literacy education.

---

<p align="center">
  <sub>Responsible AI for everyone</sub>
</p>
