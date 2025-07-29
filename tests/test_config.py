"""Tests for configuration models."""

import pytest
import tempfile
import os
from src.n8n_builder.models.config import (
    BuildConfig,
    N8nInstance,
    WorkflowReference,
    TemplateWorkflow,
)


def test_build_config_from_yaml():
    """Test loading BuildConfig from YAML."""
    yaml_content = """
n8n_instance:
  name: "Test Instance"
  url: "https://test.n8n.com"
  api_key_env: "TEST_API_KEY"

workflows:
  - name: "test-workflow"
    file: "workflows/test.json"
    description: "Test workflow"
  
  - name: "template-workflow"
    template: "templates/test.yaml"
    parameters:
      param1: "value1"
      param2: "value2"
"""

    with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
        f.write(yaml_content)
        f.flush()

        try:
            config = BuildConfig.from_yaml(f.name)

            assert config.n8n_instance.name == "Test Instance"
            assert config.n8n_instance.url == "https://test.n8n.com"
            assert config.n8n_instance.api_key_env == "TEST_API_KEY"

            assert len(config.workflows) == 2

            # Test workflow reference
            workflow_ref = config.workflows[0]
            assert isinstance(workflow_ref, WorkflowReference)
            assert workflow_ref.name == "test-workflow"
            assert workflow_ref.file == "workflows/test.json"

            # Test template workflow
            template_workflow = config.workflows[1]
            assert isinstance(template_workflow, TemplateWorkflow)
            assert template_workflow.name == "template-workflow"
            assert template_workflow.template == "templates/test.yaml"
            assert template_workflow.parameters == {
                "param1": "value1",
                "param2": "value2",
            }

        finally:
            os.unlink(f.name)
