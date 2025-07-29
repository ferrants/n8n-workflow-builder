.PHONY: install dev-install test lint format clean build

# Install the package
install:
	pip install -e .

# Install development dependencies
dev-install:
	pip install -e ".[dev]"

# Run tests
test:
	pytest tests/ -v --cov=src/n8n_builder --cov-report=html

# Run linting
lint:
	flake8 src/ tests/
	mypy src/

# Format code
format:
	black src/ tests/

# Clean build artifacts
clean:
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	rm -rf .pytest_cache/
	rm -rf htmlcov/
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

# Build package
build: clean
	python -m build

# Example commands
example-build:
	n8n-builder build config.example.yaml

example-pull:
	n8n-builder pull config.example.yaml

example-push:
	n8n-builder push config.example.yaml --dry-run

example-compare:
	n8n-builder compare config.example.yaml