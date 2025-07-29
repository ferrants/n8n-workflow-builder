"""Workflow builder service for processing and building n8n workflows."""

import json
import os
from typing import Dict, List, Any, Optional
from jinja2 import Environment, FileSystemLoader, Template

from ..models.config import BuildConfig, WorkflowReference, TemplateWorkflow
from .secrets import SecretsService


class WorkflowBuilder:
    """Service for building n8n workflows from configuration."""

    def __init__(self, config: BuildConfig, secrets: SecretsService) -> None:
        """Initialize the workflow builder.

        Args:
            config: Build configuration
            secrets: Secrets service for accessing environment variables
        """
        self.config = config
        self.secrets = secrets
        self.jinja_env = Environment(loader=FileSystemLoader("."))

    def build_all(self) -> List[Dict[str, Any]]:
        """Build all workflows defined in the configuration.

        Returns:
            List of build results with workflow names and output paths
        """
        os.makedirs(self.config.output_dir, exist_ok=True)
        results = []

        for workflow in self.config.workflows:
            if isinstance(workflow, WorkflowReference):
                result = self._build_workflow_reference(workflow)
            elif isinstance(workflow, TemplateWorkflow):
                result = self._build_template_workflow(workflow)
            else:
                raise ValueError(f"Unknown workflow type: {type(workflow)}")

            results.append(result)

        return results

    def build_single(self, workflow_name: str) -> Optional[Dict[str, Any]]:
        """Build a single workflow by name.

        Args:
            workflow_name: Name of the workflow to build

        Returns:
            Build result dictionary, or None if workflow not found
        """
        os.makedirs(self.config.output_dir, exist_ok=True)
        
        # Find the workflow in the configuration
        target_workflow = None
        for workflow in self.config.workflows:
            if workflow.name == workflow_name:
                target_workflow = workflow
                break
        
        if target_workflow is None:
            return None
        
        # Build the specific workflow
        if isinstance(target_workflow, WorkflowReference):
            return self._build_workflow_reference(target_workflow)
        elif isinstance(target_workflow, TemplateWorkflow):
            return self._build_template_workflow(target_workflow)
        else:
            raise ValueError(f"Unknown workflow type: {type(target_workflow)}")

    def _build_workflow_reference(self, workflow: WorkflowReference) -> Dict[str, Any]:
        """Build a workflow from a direct file reference.

        Args:
            workflow: Workflow reference configuration

        Returns:
            Build result dictionary
        """
        if not os.path.exists(workflow.file):
            raise FileNotFoundError(f"Workflow file not found: {workflow.file}")

        with open(workflow.file, "r") as f:
            workflow_data = json.load(f)

        # Update workflow name if different
        if "name" in workflow_data:
            workflow_data["name"] = workflow.name

        output_path = os.path.join(self.config.output_dir, f"{workflow.name}.json")

        with open(output_path, "w") as f:
            json.dump(workflow_data, f, indent=2)

        return {
            "name": workflow.name,
            "type": "reference",
            "source": workflow.file,
            "output_path": output_path,
        }

    def _build_template_workflow(self, workflow: TemplateWorkflow) -> Dict[str, Any]:
        """Build a workflow from a template with parameters.

        Args:
            workflow: Template workflow configuration

        Returns:
            Build result dictionary
        """
        if not os.path.exists(workflow.template):
            raise FileNotFoundError(f"Template file not found: {workflow.template}")

        # Load template
        template = self.jinja_env.get_template(workflow.template)

        # Prepare template context
        context = {
            "workflow_name": workflow.name,
            "parameters": workflow.parameters,
            "secrets": self._get_secrets_context(),
        }

        # Render template
        rendered_content = template.render(**context)

        # Parse as JSON if template produces JSON, otherwise assume it's already structured
        try:
            workflow_data = json.loads(rendered_content)
        except json.JSONDecodeError:
            # If not JSON, assume it's YAML and convert
            import yaml

            workflow_data = yaml.safe_load(rendered_content)

        # Ensure workflow has the correct name
        if isinstance(workflow_data, dict) and "name" not in workflow_data:
            workflow_data["name"] = workflow.name

        output_path = os.path.join(self.config.output_dir, f"{workflow.name}.json")

        with open(output_path, "w") as f:
            json.dump(workflow_data, f, indent=2)

        return {
            "name": workflow.name,
            "type": "template",
            "source": workflow.template,
            "output_path": output_path,
            "parameters": workflow.parameters,
        }

    def _get_secrets_context(self) -> Dict[str, Any]:
        """Get secrets context for template rendering.

        Returns:
            Dictionary of available secrets (non-sensitive ones only)
        """
        # Only expose non-sensitive configuration, not actual secret values
        return {
            "n8n_url": self.config.n8n_instance.url,
            "n8n_name": self.config.n8n_instance.name or "default",
        }
