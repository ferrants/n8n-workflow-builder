# n8n Workflow Repository Template

This is a template for setting up your own n8n workflow repository using the n8n-workflow-builder library.

## Quick Setup

```bash
# 1. Install the library
pip install n8n-workflow-builder

# 2. Create your workflow repository
mkdir my-n8n-workflows
cd my-n8n-workflows
git init

# 3. Create directory structure
mkdir -p templates workflows built_workflows pulled_workflows

# 4. Copy this template structure
curl -o setup.sh https://raw.githubusercontent.com/ferrants/n8n-workflow-builder/main/setup-repo.sh
chmod +x setup.sh
./setup.sh
```

## Directory Structure

```
my-n8n-workflows/
├── templates/                 # Jinja2 workflow templates
│   ├── data-sync.yaml        # Example: Data synchronization template
│   ├── email-scraper.yaml    # Example: Email scraping template
│   └── api-monitor.yaml      # Example: API monitoring template
├── workflows/                # Static workflow files
│   └── legacy-import.json    # Example: Direct workflow import
├── environments/             # Environment-specific configs
│   ├── dev.yaml             # Development environment
│   ├── staging.yaml         # Staging environment
│   └── prod.yaml            # Production environment
├── built_workflows/          # Generated workflows (gitignored)
├── pulled_workflows/         # Downloaded workflows (gitignored)
├── config.yaml              # Main workflow definitions
├── .env                     # Environment variables (gitignored)
├── .env.example            # Environment template
├── .gitignore              # Git ignore rules
├── Makefile                # Common commands
└── README.md               # Your workflow documentation
```

## Example Files

### .env.example
```env
# n8n Instance Configuration
N8N_API_KEY=your_api_key_here
N8N_INSTANCE_URL=https://your-n8n-instance.com

# Google Sheets Credentials (example)
GOOGLE_SHEETS_CREDENTIAL_ID=your_credential_id_here

# Other service credentials
SLACK_CREDENTIAL_ID=your_slack_credential_id
WEBHOOK_URL=https://your-webhook-url.com
```

### config.yaml
```yaml
n8n_instance:
  name: "Production n8n"
  url: "${N8N_INSTANCE_URL}"
  api_key_env: "N8N_API_KEY"

output_dir: "built_workflows"
pulled_dir: "pulled_workflows"

workflows:
  # Data synchronization workflows
  - name: "sync-customers-salesforce-hubspot"
    template: "templates/data-sync.yaml"
    description: "Syncs customer data from Salesforce to HubSpot"
    parameters:
      source_system: "salesforce"
      target_system: "hubspot"
      sync_interval: "hourly"
      fields: ["name", "email", "company", "phone"]
      source_credential_id: "${SALESFORCE_CREDENTIAL_ID}"
      target_credential_id: "${HUBSPOT_CREDENTIAL_ID}"

  # Email scraping workflows  
  - name: "scrape-competitor-emails"
    template: "templates/email-scraper.yaml"
    description: "Scrapes competitor websites for contact emails"
    parameters:
      search_terms: ["competitor1", "competitor2"]
      google_sheet_url: "https://docs.google.com/spreadsheets/d/your-sheet-id"
      google_sheet_tab: "Contacts"
      limit: 50
      google_sheets_credential_id: "${GOOGLE_SHEETS_CREDENTIAL_ID}"

  # Direct workflow import
  - name: "legacy-notification-system"
    file: "workflows/legacy-import.json"
    description: "Legacy notification system imported directly"
```

### Makefile
```makefile
.PHONY: help build push pull compare clean

help:
	@echo "Available commands:"
	@echo "  build     - Build all workflows"
	@echo "  push      - Deploy workflows to n8n"
	@echo "  pull      - Download workflows from n8n"
	@echo "  compare   - Compare built vs deployed workflows"
	@echo "  clean     - Clean generated files"

build:
	n8n-builder build config.yaml

push:
	n8n-builder push config.yaml

pull:
	n8n-builder pull config.yaml

compare:
	n8n-builder compare config.yaml

clean:
	rm -rf built_workflows/* pulled_workflows/*

# Environment-specific commands
build-dev:
	n8n-builder build environments/dev.yaml

push-dev:
	n8n-builder push environments/dev.yaml

build-prod:
	n8n-builder build environments/prod.yaml

push-prod:
	n8n-builder push environments/prod.yaml --dry-run
	@echo "Remove --dry-run to actually deploy to production"
```

### .gitignore
```gitignore
# Environment files
.env
.env.local
.env.*.local

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
venv/
env/

# IDE
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db

# Logs
*.log
logs/

# Temporary files
*.tmp
*.temp
```

## Best Practices

1. **Environment Management**: Use separate config files for different environments
2. **Secret Management**: Store all credentials in environment variables
3. **Version Control**: Track templates and configs, exclude generated files
4. **Testing**: Always use `--dry-run` before production deployments
5. **Documentation**: Document your workflows and parameters clearly
6. **Backup**: Regularly pull workflows to backup your n8n instance

## Getting Started

1. Copy this template structure to your repository
2. Update the configuration files with your specific workflows
3. Create templates based on your existing n8n workflows
4. Set up your environment variables
5. Test with `n8n-builder build config.yaml`
6. Deploy with `n8n-builder push config.yaml --dry-run` first

For more information, see the [n8n-workflow-builder documentation](https://github.com/ferrants/n8n-workflow-builder).
