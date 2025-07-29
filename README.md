# n8n Workflow Builder

A Python application for building, managing, and deploying n8n workflows with configuration-driven approach.

## Features

- **Config-driven workflow management** using YAML configuration files
- **Template system** for parameterized workflows using Jinja2
- **Secure secrets management** with .env file integration
- **CLI interface** with build, pull, push, and compare commands
- **Workflow comparison** to track differences between local and remote workflows
- **n8n API integration** for seamless workflow deployment

## Installation

```bash
# Install the package
pip install -e .

# Install with development dependencies
pip install -e ".[dev]"
```

## Quick Start

1. **Set up environment variables**:
   ```bash
   cp .env.example .env
   # Edit .env with your n8n API key and instance URL
   ```

2. **Create a configuration file**:
   ```bash
   cp config.example.yaml config.yaml
   # Edit config.yaml with your workflow definitions
   ```

3. **Build workflows**:
   ```bash
   n8n-builder build config.yaml
   ```

4. **Push to n8n**:
   ```bash
   n8n-builder push config.yaml
   ```

## Configuration

### Environment Variables (.env)

```env
N8N_API_KEY=your_n8n_api_key_here
N8N_WEBHOOK_URL=your_n8n_webhook_url_here
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
n8n-builder build config.yaml
```

### Pull Workflows
Download workflows from your n8n instance:
```bash
n8n-builder pull config.yaml
```

### Push Workflows
Upload built workflows to your n8n instance:
```bash
n8n-builder push config.yaml

# Dry run to see what would be uploaded
n8n-builder push config.yaml --dry-run
```

### Compare Workflows
Compare built workflows with pulled workflows:
```bash
n8n-builder compare config.yaml

# Output as JSON
n8n-builder compare config.yaml --format json
```

## Project Structure

```
n8n_workflows/
├── src/n8n_builder/           # Main package
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

## Template System

Templates use Jinja2 syntax and have access to:

- `workflow_name`: The name of the workflow being built
- `parameters`: Parameters defined in the configuration
- `secrets`: Non-sensitive configuration values

Example template (`templates/data-sync.yaml`):
```json
{
  "name": "{{ workflow_name }}",
  "nodes": [
    {
      "name": "Get {{ parameters.source_system | title }} Data",
      "type": "n8n-nodes-base.{{ parameters.source_system }}",
      "parameters": {
        "fields": {{ parameters.fields | tojson }}
      }
    }
  ]
}
```

## Development

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

### Building Package
```bash
make build
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
