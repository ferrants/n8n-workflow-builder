# n8n Workflow Builder

A Python library for building, managing, and deploying n8n workflows with a configuration-driven approach. This package provides the core tooling while allowing you to maintain your own private repository of workflows and templates.

## Features

- **Config-driven workflow management** using YAML configuration files
- **Template system** for parameterized workflows using Jinja2
- **Secure secrets management** with .env file integration
- **CLI interface** with build, pull, push, and compare commands
- **Workflow comparison** to track differences between local and remote workflows
- **n8n API integration** for seamless workflow deployment

## Installation

### Install from PyPI (Recommended)
```bash
# Install the latest stable version
pip install n8n-workflow-builder

# Install with development dependencies (for contributing)
pip install n8n-workflow-builder[dev]
```

### Install from Source
```bash
# Clone and install in development mode
git clone https://github.com/ferrants/n8n-workflow-builder.git
cd n8n-workflow-builder
pip install -e .
```

## Setting Up Your Workflow Repository

After installing the library, you'll need to create your own repository to store workflows, templates, and configuration. This repository should be private to your organization.

### 1. Create Your Workflow Repository

```bash
# Create a new repository for your workflows
mkdir my-n8n-workflows
cd my-n8n-workflows
git init

# Create the recommended directory structure
mkdir -p templates workflows built_workflows pulled_workflows
```

### 2. Set Up Configuration Files

Create your environment file:
```
# Create .env file with your n8n credentials
N8N_API_KEY=your_n8n_api_key_here
```

Create your configuration file:
```
n8n_instance:
  name: "Production n8n"
  url: "https://your-n8n-instance.com"
  api_key_env: "N8N_API_KEY"

output_dir: "built_workflows"
pulled_dir: "pulled_workflows"

workflows:
  # Add your workflow definitions here
  # See examples below
```

### 3. Set Up Git Ignore

```
# Environment files
.env
.env.local

# Generated workflows
built_workflows/
pulled_workflows/

# Python
__pycache__/
*.pyc
*.pyo
*.pyd
.Python
*.so
.coverage
.pytest_cache/

# IDE
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db
```

### 4. Quick Start

1. **Build workflows**:
   ```bash
   n8n-workflow-builder build config.yaml
   ```

2. **Push to n8n**:
   ```bash
   n8n-workflow-builder push config.yaml
   ```

### 5. Recommended Repository Structure

```
my-n8n-workflows/
├── templates/                 # Jinja2 workflow templates
│   ├── data-sync.yaml        # Reusable templates
│   └── email-scraper.yaml    # Parameterized workflows
├── workflows/                # Static workflow files
│   └── legacy-workflow.json  # Direct workflow files
├── built_workflows/          # Generated workflows (gitignored)
├── pulled_workflows/         # Downloaded workflows (gitignored)
├── config.yaml              # Workflow definitions
├── .env                     # Environment variables (gitignored)
├── .gitignore              # Git ignore rules
└── README.md               # Your workflow documentation
```

## Configuration

### Environment Variables (.env)

```env
N8N_API_KEY=your_n8n_api_key_here
```

### Configuration File (config.yaml)

```yaml
n8n_instance:
  name: "Production n8n"
  url: "https://your-n8n-instance.com"
  api_key_env: "N8N_API_KEY"

output_dir: "built_workflows"
pulled_dir: "pulled_workflows"

workflows:
  # Direct workflow file reference
  - name: "user-onboarding"
    file: "workflows/user-onboarding.json"
    description: "Handles new user onboarding process"
  
  # Template-based workflow
  - name: "data-sync-customers"
    template: "templates/data-sync.yaml"
    description: "Syncs customer data between systems"
    parameters:
      source_system: "salesforce"
      target_system: "hubspot"
      sync_interval: "hourly"
      fields: ["name", "email", "company"]
```

## CLI Commands

### Build Workflows
Build all workflows defined in the configuration:
```bash
# Build all workflows
n8n-workflow-builder build config.yaml

# Build a specific workflow by name
n8n-workflow-builder build config.yaml --workflow user-onboarding
n8n-workflow-builder build config.yaml -w user-onboarding
```

### Pull Workflows
Download workflows from your n8n instance:
```bash
# Pull all workflows
n8n-workflow-builder pull config.yaml

# Pull a specific workflow by name
n8n-workflow-builder pull config.yaml --workflow user-onboarding
n8n-workflow-builder pull config.yaml -w user-onboarding
```

### Push Workflows
Upload built workflows to your n8n instance:
```bash
# Push all workflows
n8n-workflow-builder push config.yaml

# Push a specific workflow by name
n8n-workflow-builder push config.yaml --workflow user-onboarding
n8n-workflow-builder push config.yaml -w user-onboarding

# Dry run to see what would be uploaded
n8n-workflow-builder push config.yaml --dry-run

# Dry run for a specific workflow
n8n-workflow-builder push config.yaml --workflow my-workflow --dry-run
```

### Compare Workflows
Compare built workflows with pulled workflows:
```bash
# Compare all workflows
n8n-workflow-builder compare config.yaml

# Compare a specific workflow by name
n8n-workflow-builder compare config.yaml --workflow user-onboarding
n8n-workflow-builder compare config.yaml -w user-onboarding

# Output as JSON
n8n-workflow-builder compare config.yaml --format json

# Compare single workflow with JSON output
n8n-workflow-builder compare config.yaml --workflow my-workflow --format json
```

## Library Architecture

The n8n-workflow-builder library is structured as follows:

```
n8n_workflow_builder/        # Core library package
├── models/                  # Data models
│   └── config.py            # Configuration models
├── services/                # Business logic
│   ├── secrets.py           # Secrets management
│   ├── builder.py           # Workflow builder
│   ├── n8n_client.py        # n8n API client
│   └── comparator.py        # Workflow comparison
├── utils/                   # Utilities
│   └── validation.py        # Validation helpers
└── cli.py                   # Command line interface
```

## Publishing the Library

### For Library Maintainers

To publish this library to PyPI:

1. **Update version in pyproject.toml**
2. **Build the package**:
   ```bash
   python -m build
   ```
3. **Upload to PyPI**:
   ```bash
   python -m twine upload dist/*
   ```

### Package Configuration

The library should be configured in `pyproject.toml` with:

```toml
[project]
name = "n8n-workflow-builder"
version = "1.0.0"
description = "A Python library for building, managing, and deploying n8n workflows"
authors = [{name = "Your Name", email = "your.email@example.com"}]
license = {text = "MIT"}
readme = "README.md"
requires-python = ">=3.8"
dependencies = [
    "click>=8.0.0",
    "pyyaml>=6.0",
    "python-dotenv>=0.19.0",
    "requests>=2.25.0",
    "jinja2>=3.0.0",
    "jsonschema>=4.0.0"
]

[project.optional-dependencies]
dev = [
    "pytest>=7.0.0",
    "pytest-cov>=4.0.0",
    "black>=22.0.0",
    "flake8>=5.0.0",
    "mypy>=1.0.0"
]

[project.scripts]
n8n-workflow-builder = "n8n_workflow_builder.cli:main"

[project.urls]
Homepage = "https://github.com/ferrants/n8n-workflow-builder"
Repository = "https://github.com/ferrants/n8n-workflow-builder"
Issues = "https://github.com/ferrants/n8n-workflow-builder/issues"
```
n8n_workflows/
├── src/n8n_workflow_builder/ # Main package
│   ├── models/                # Data models
│   │   └── config.py         # Configuration models
│   ├── services/             # Business logic
│   │   ├── secrets.py        # Secrets management
│   │   ├── builder.py        # Workflow builder
│   │   ├── n8n_client.py     # n8n API client
│   │   └── comparator.py     # Workflow comparison
│   ├── utils/                # Utilities
│   │   └── validation.py     # Validation helpers
│   └── cli.py               # Command line interface
├── templates/               # Workflow templates
├── workflows/              # Static workflow files
├── built_workflows/        # Generated workflows (output)
├── pulled_workflows/       # Downloaded workflows
├── tests/                 # Test files
├── config.example.yaml    # Example configuration
├── .env.example          # Example environment file
└── pyproject.toml        # Package configuration
```

## Creating Templates

### Template System Overview

Templates use Jinja2 syntax and have access to:

- `workflow_name`: The name of the workflow being built
- `parameters`: Parameters defined in the configuration
- `secrets`: Non-sensitive configuration values

### Template Format Requirements

- **Templates must be JSON format** (despite `.yaml` extension)
- Templates are processed by Jinja2 before being parsed as JSON
- **Critical**: n8n expressions like `{{ $json.field }}` must be escaped

### Creating Templates from Existing Workflows

1. **Pull an existing workflow**:
   ```bash
   n8n-workflow-builder pull config.yaml --workflow my-workflow
   ```

2. **Copy and parameterize**:
   ```bash
   cp pulled_workflows/my-workflow.json templates/my-template.yaml
   ```

3. **Remove volatile fields** (id, createdAt, updatedAt, versionId, shared, etc.)

4. **Parameterize values**:
   ```json
   {
     "name": "{{ workflow_name }}",
     "nodes": [
       {
         "parameters": {
           "url": "https://api.example.com/{{ parameters.endpoint }}",
           "limit": {{ parameters.limit | default(10) }}
         }
       }
     ]
   }
   ```

5. **Escape n8n expressions**:
   ```json
   {
     "parameters": {
       "leftValue": "={{ '{{' }} {{ '$' }}json.website {{ '}}' }}",
       "jsCode": "const input = {{ '$' }}input.first().json.data"
     }
   }
   ```

6. **Add credential references**:
   ```json
   {
     "credentials": {
       "googleSheetsOAuth2Api": {
         "id": "{{ parameters.google_sheets_credential_id }}",
         "name": "Google Sheets account"
       }
     }
   }
   ```

### Template Testing Workflow

1. **Build and compare**:
   ```bash
   n8n-workflow-builder build config.yaml --workflow my-workflow
   n8n-workflow-builder compare config.yaml --workflow my-workflow
   ```

2. **Test deployment**:
   ```bash
   n8n-workflow-builder push config.yaml --workflow my-workflow --dry-run
   ```

### Example Template

Example template (`templates/data-sync.yaml`):
```json
{
  "name": "{{ workflow_name }}",
  "nodes": [
    {
      "name": "Get {{ parameters.source_system | title }} Data",
      "type": "n8n-nodes-base.{{ parameters.source_system }}",
      "parameters": {
        "fields": {{ parameters.fields | tojson }},
        "url": "{{ parameters.api_url | urlencode }}"
      },
      "credentials": {
        "{{ parameters.credential_type }}": {
          "id": "{{ parameters.credential_id }}",
          "name": "{{ parameters.credential_name }}"
        }
      }
    }
  ]
}
```

## Best Practices for Your Workflow Repository

### Version Control
- **Keep templates and config in git**: Track your workflow definitions and templates
- **Exclude sensitive data**: Never commit `.env` files or API keys
- **Exclude generated files**: Don't commit `built_workflows/` or `pulled_workflows/`

### Organization
- **Use descriptive names**: Name workflows and templates clearly
- **Group related workflows**: Use prefixes or directories for organization
- **Document parameters**: Add comments in config.yaml explaining parameters

### Security
- **Use environment variables**: Store API keys and secrets in `.env`
- **Separate environments**: Use different config files for dev/staging/prod
- **Credential management**: Reference credential IDs as parameters, not hardcoded

### Testing
- **Compare before deploying**: Always run compare to check differences
- **Use dry-run**: Test deployments with `--dry-run` flag
- **Single workflow testing**: Use `--workflow` flag during development

### Example Workflow Repository

See our [example workflow repository](https://github.com/ferrants/n8n-workflows-example) for a complete setup with:
- Multiple environment configurations
- Reusable templates
- CI/CD pipeline examples
- Documentation templates

## Contributing to the Library

### Development Setup
```bash
git clone https://github.com/ferrants/n8n-workflow-builder.git
cd n8n-workflow-builder
pip install -e ".[dev]"
```

### Running Tests
```bash
make test
```

### Code Formatting
```bash
make format
```

### Linting
```bash
make lint
```

## Main Components

- **Workflows**: Static JSON files or template-generated workflows
- **Templates**: Jinja2 templates for parameterized workflows  
- **Builder**: Processes configuration and builds concrete n8n workflows
- **n8n Client**: Handles API communication with n8n instances
- **Comparator**: Compares built workflows with deployed workflows
- **Secrets Service**: Secure management of API keys and sensitive data

## API Reference

The package provides several key services:

- `SecretsService`: Manages environment variables and API keys
- `WorkflowBuilder`: Builds workflows from configuration
- `N8nClient`: Communicates with n8n REST API
- `WorkflowComparator`: Compares workflow versions
