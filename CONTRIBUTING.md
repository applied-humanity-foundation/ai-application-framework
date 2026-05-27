# Contributing to AHF AI Application Framework

Thank you for your interest in contributing! This project is maintained by the
Applied Humanity Foundation, a 501(c)(3) nonprofit. Contributions of all kinds
are welcome -- code, documentation, bug reports, and feature requests.

## Getting Started

1. Fork the repository and clone your fork.
2. Install dependencies for both packages:

```bash
make dev
```

This installs the Python package in editable mode with all optional
dependencies and sets up the TypeScript toolchain via npm.

## Project Structure

The library ships in two languages with a shared design:

- `python/ahf_ai/` -- Python package (published to PyPI as `ahf-ai`)
- `typescript/src/` -- TypeScript package (published to npm as `@ahf/ai-framework`)
- `tests/python/` and `tests/typescript/` -- test suites for each
- `examples/` -- runnable example scripts
- `docs/` -- architecture and API documentation

## Development Workflow

### Making Changes

1. Create a feature branch from `main`:
   ```bash
   git checkout -b feature/your-feature-name
   ```
2. Write your code. Follow the existing patterns in whichever package you are
   modifying.
3. Add or update tests to cover your changes.
4. Run the full check suite before committing:
   ```bash
   make lint
   make test
   ```

### Python Guidelines

- Target Python 3.9+ and use type hints on all public APIs.
- Use `ruff` for linting and formatting.
- Use `mypy` in strict mode -- the CI enforces this.
- Write async code where IO is involved; use `httpx.AsyncClient`.
- Pydantic v2 models go in `python/ahf_ai/types/models.py`.

### TypeScript Guidelines

- Target ES2022 with strict TypeScript settings.
- Use `vitest` for tests.
- Run `npm run lint` (ESLint) and `npm run format` (Prettier) before pushing.
- All public functions must have explicit return types.

### Testing Requirements

- Every new feature or bug fix must include tests.
- Python tests live in `tests/python/` and use pytest with `pytest-asyncio`.
- TypeScript tests live in `tests/typescript/` and use vitest.
- Aim for meaningful assertions, not just "it doesn't crash" checks.

## Pull Request Process

1. Fill out the PR template completely.
2. Ensure all CI checks pass (linting, type checking, tests).
3. Keep PRs focused -- one logical change per PR.
4. Update documentation if you change any public API.
5. A maintainer will review your PR. Please be patient and responsive to
   feedback.

## Reporting Bugs

Use the GitHub issue template for bug reports. Include:

- Your Python/Node version and OS
- A minimal reproduction case
- The expected vs. actual behavior

## Suggesting Features

Open a feature request issue. Describe the use case, not just the solution you
have in mind. We prioritize features that align with the Foundation's mission of
making AI accessible and safe.

## Code of Conduct

All participants are expected to follow the
[Code of Conduct](CODE_OF_CONDUCT.md). Be respectful, constructive, and
inclusive.

## License

By contributing, you agree that your contributions will be licensed under the
MIT License that covers this project.
