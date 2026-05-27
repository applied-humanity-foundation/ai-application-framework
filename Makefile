.PHONY: install dev test lint format build clean publish-pypi publish-npm docs help

help: ## Show this help message
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | \
		awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

install: ## Install both Python and TypeScript dependencies
	pip install -e ".[dev,all]"
	npm install

dev: ## Install in development mode with all extras
	pip install -e ".[dev,all]"
	npm install
	@echo "Development environment ready."

test: test-python test-typescript ## Run all tests

test-python: ## Run Python tests with coverage
	pytest tests/python/ -v --tb=short
	@echo "Python tests complete."

test-typescript: ## Run TypeScript tests
	npm test
	@echo "TypeScript tests complete."

lint: lint-python lint-typescript ## Run all linters

lint-python: ## Lint Python code with ruff and mypy
	ruff check python/ tests/python/
	mypy python/ahf_ai/

lint-typescript: ## Lint TypeScript code with ESLint
	npm run lint

format: format-python format-typescript ## Format all code

format-python: ## Format Python code with ruff
	ruff format python/ tests/python/
	ruff check --fix python/ tests/python/

format-typescript: ## Format TypeScript code with Prettier
	npm run format

build: build-python build-typescript ## Build both packages

build-python: ## Build Python package
	python -m build
	@echo "Python package built in dist/"

build-typescript: ## Build TypeScript package
	npm run build
	@echo "TypeScript package built in dist/"

clean: ## Remove all build artifacts
	rm -rf dist/ build/ *.egg-info .pytest_cache .mypy_cache .ruff_cache
	rm -rf coverage/ htmlcov/ .coverage
	rm -rf node_modules/.cache
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	npm run clean 2>/dev/null || true
	@echo "Cleaned all build artifacts."

publish-pypi: build-python ## Publish Python package to PyPI
	twine upload dist/*.tar.gz dist/*.whl
	@echo "Published to PyPI."

publish-npm: build-typescript ## Publish TypeScript package to npm
	cd dist && npm publish --access public
	@echo "Published to npm."

docs: ## Build documentation site
	@echo "Documentation is served via index.html — open in a browser."
	@echo "API reference: docs/API_REFERENCE.md"
	@echo "Architecture: docs/ARCHITECTURE.md"
