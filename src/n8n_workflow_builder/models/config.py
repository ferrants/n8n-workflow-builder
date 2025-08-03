"""Configuration models for n8n workflow builder."""

from dataclasses import dataclass
from typing import Dict, List, Optional, Any, Union
import yaml


@dataclass
class N8nInstance:
    """Configuration for an n8n instance."""

    url: str
    api_key_env: str
    name: Optional[str] = None


@dataclass
class WorkflowReference:
    """Reference to a workflow file."""

    name: str
    file: str
    description: Optional[str] = None


@dataclass
class TemplateWorkflow:
    """Template workflow with parameters."""

    name: str
    template: str
    parameters: Dict[str, Any]
    description: Optional[str] = None


@dataclass
class BuildConfig:
    """Main configuration for the n8n workflow builder."""

    n8n_instance: N8nInstance
    workflows: List[Union[WorkflowReference, TemplateWorkflow]]
    output_dir: str = "built_workflows"
    pulled_dir: str = "pulled_workflows"

    @classmethod
    def from_yaml(cls, yaml_path: str) -> "BuildConfig":
        """Load configuration from a YAML file.

        Args:
            yaml_path: Path to the YAML configuration file

        Returns:
            BuildConfig instance
        """
        with open(yaml_path, "r") as f:
            data = yaml.safe_load(f)

        # Parse n8n instance
        n8n_data = data["n8n_instance"]
        n8n_instance = N8nInstance(
            url=n8n_data["url"],
            api_key_env=n8n_data["api_key_env"],
            name=n8n_data.get("name"),
        )

        # Parse workflows
        workflows = []
        for workflow_data in data["workflows"]:
            if "file" in workflow_data:
                workflows.append(
                    WorkflowReference(
                        name=workflow_data["name"],
                        file=workflow_data["file"],
                        description=workflow_data.get("description"),
                    )
                )
            elif "template" in workflow_data:
                workflows.append(
                    TemplateWorkflow(
                        name=workflow_data["name"],
                        template=workflow_data["template"],
                        parameters=workflow_data.get("parameters", {}),
                        description=workflow_data.get("description"),
                    )
                )

        return cls(
            n8n_instance=n8n_instance,
            workflows=workflows,
            output_dir=data.get("output_dir", "built_workflows"),
            pulled_dir=data.get("pulled_dir", "pulled_workflows"),
        )
