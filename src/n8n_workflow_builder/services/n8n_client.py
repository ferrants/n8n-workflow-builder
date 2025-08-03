"""n8n API client for interacting with n8n instances."""

import json
import requests
import uuid
from typing import Dict, List, Any, Optional
from urllib.parse import urljoin


class N8nClient:
    """Client for interacting with n8n REST API."""

    def __init__(self, base_url: str, api_key: str) -> None:
        """Initialize the n8n client.

        Args:
            base_url: Base URL of the n8n instance
            api_key: API key for authentication
        """
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.session = requests.Session()
        self.session.headers.update(
            {"X-N8N-API-KEY": api_key, "Content-Type": "application/json"}
        )

    def get_all_workflows(self) -> List[Dict[str, Any]]:
        """Get all workflows from the n8n instance.

        Returns:
            List of workflow dictionaries
        """
        url = urljoin(self.base_url, "/api/v1/workflows")
        response = self.session.get(url)
        response.raise_for_status()

        workflows_data = response.json()
        workflows = []

        # Get detailed workflow data for each workflow
        for workflow_summary in workflows_data.get("data", []):
            workflow_id = workflow_summary["id"]
            detailed_workflow = self.get_workflow(workflow_id)
            workflows.append(detailed_workflow)

        return workflows

    def get_workflow(self, workflow_id: str) -> Dict[str, Any]:
        """Get a specific workflow by ID.

        Args:
            workflow_id: The workflow ID

        Returns:
            Workflow dictionary
        """
        url = urljoin(self.base_url, f"/api/v1/workflows/{workflow_id}")
        response = self.session.get(url)
        response.raise_for_status()

        return response.json()

    def get_workflow_by_name(self, workflow_name: str) -> Optional[Dict[str, Any]]:
        """Get a specific workflow by name.

        Args:
            workflow_name: The workflow name

        Returns:
            Workflow dictionary, or None if not found
        """
        return self._find_workflow_by_name(workflow_name)

    def upload_workflow(
        self, workflow_path: str, workflow_name: Optional[str] = None
    ) -> Dict[str, Any]:
        """Upload a workflow to the n8n instance.

        Args:
            workflow_path: Path to the workflow JSON file
            workflow_name: Optional name override for the workflow

        Returns:
            Response from the n8n API
        """
        with open(workflow_path, "r") as f:
            workflow_data = json.load(f)

        if workflow_name:
            workflow_data["name"] = workflow_name

        # Check if workflow already exists
        existing_workflow = self._find_workflow_by_name(workflow_data["name"])

        if existing_workflow:
            # Update existing workflow
            workflow_id = existing_workflow["id"]
            return self._update_workflow(workflow_id, workflow_data)
        else:
            # Create new workflow
            return self._create_workflow(workflow_data)

    def _find_workflow_by_name(self, name: str) -> Optional[Dict[str, Any]]:
        """Find a workflow by name.

        Args:
            name: Workflow name to search for

        Returns:
            Workflow dictionary if found, None otherwise
        """
        try:
            workflows = self.get_all_workflows()
            for workflow in workflows:
                if workflow.get("name") == name:
                    return workflow
            return None
        except Exception:
            return None

    def _create_workflow(self, workflow_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new workflow.

        Args:
            workflow_data: Workflow data dictionary

        Returns:
            Response from the n8n API
        """
        # Prepare workflow data for n8n API
        prepared_data = self._prepare_workflow_data(workflow_data)

        url = urljoin(self.base_url, "/api/v1/workflows")
        response = self.session.post(url, json=prepared_data)
        response.raise_for_status()

        return response.json()

    def _update_workflow(
        self, workflow_id: str, workflow_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Update an existing workflow.

        Args:
            workflow_id: ID of the workflow to update
            workflow_data: Updated workflow data

        Returns:
            Response from the n8n API
        """
        # Prepare workflow data for n8n API
        prepared_data = self._prepare_workflow_data(workflow_data)

        url = urljoin(self.base_url, f"/api/v1/workflows/{workflow_id}")
        response = self.session.put(url, json=prepared_data)
        response.raise_for_status()

        return response.json()

    def _prepare_workflow_data(self, workflow_data: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare workflow data for n8n API by adding required fields.

        Args:
            workflow_data: Raw workflow data

        Returns:
            Prepared workflow data with required n8n fields
        """
        # Only include fields that are allowed by the n8n API for creation
        # Note: 'active' and 'tags' are read-only and cannot be set during creation
        allowed_fields = ["name", "nodes", "connections", "settings"]
        prepared_data = {
            key: workflow_data[key] for key in allowed_fields if key in workflow_data
        }

        # Ensure nodes have unique IDs
        if "nodes" in prepared_data:
            for node in prepared_data["nodes"]:
                if "id" not in node:
                    node["id"] = str(uuid.uuid4())

        if "settings" not in prepared_data:
            prepared_data["settings"] = {}

        return prepared_data

    def save_workflow(self, workflow: Dict[str, Any], output_path: str) -> None:
        """Save a workflow to a JSON file.

        Args:
            workflow: Workflow dictionary
            output_path: Path to save the workflow file
        """
        with open(output_path, "w") as f:
            json.dump(workflow, f, indent=2)

    def test_connection(self) -> bool:
        """Test the connection to the n8n instance.

        Returns:
            True if connection is successful, False otherwise
        """
        try:
            url = urljoin(self.base_url, "/api/v1/workflows")
            response = self.session.get(url)
            return response.status_code == 200
        except Exception:
            return False
