# Agent Guidelines for n8n Workflow Builder

## Build/Test/Lint Commands
- **Install dev deps**: `make dev-install` or `pip install -e ".[dev]"`
- **Run all tests**: `make test` or `pytest tests/ -v --cov=src/n8n_builder --cov-report=html`
- **Run single test**: `pytest tests/test_specific.py::test_function_name -v`
- **Lint code**: `make lint` (runs flake8 + mypy) or `flake8 src/ tests/` + `mypy src/`
- **Format code**: `make format` or `black src/ tests/`
- **Build package**: `make build`

## Code Style Guidelines
- **Python version**: 3.8+ (configured in pyproject.toml)
- **Formatting**: Black with 88 character line length
- **Type hints**: Required for all function definitions (mypy enforced)
- **Imports**: Standard library first, then third-party, then local imports
- **Docstrings**: Google style with Args/Returns sections for public methods
- **Error handling**: Use specific exception types, wrap external API calls in try/except
- **Naming**: snake_case for functions/variables, PascalCase for classes
- **File structure**: Follow existing patterns in src/n8n_builder/

## Dependencies
- Core: click, pyyaml, python-dotenv, requests, jinja2, jsonschema
- Dev: pytest, pytest-cov, black, flake8, mypy
- Use dataclasses for models, type hints throughout