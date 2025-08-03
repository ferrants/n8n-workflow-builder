"""Validation utilities for n8n workflows and configurations."""

import json
from typing import Dict, Any, List
from jsonschema import validate, ValidationError


def validate_workflow(workflow_data: Dict[str, Any]) -> List[str]:
    """Validate an n8n workflow structure.

    Args:
        workflow_data: Workflow data dictionary

    Returns:
        List of validation errors (empty if valid)
    """
    errors = []

    # Check required fields
    required_fields = ["name", "nodes", "connections"]
    for field in required_fields:
        if field not in workflow_data:
            errors.append(f"Missing required field: {field}")

    # Validate nodes
    if "nodes" in workflow_data:
        if not isinstance(workflow_data["nodes"], list):
            errors.append("'nodes' must be a list")
        else:
            for i, node in enumerate(workflow_data["nodes"]):
                node_errors = validate_node(node, i)
                errors.extend(node_errors)

    # Validate connections
    if "connections" in workflow_data:
        if not isinstance(workflow_data["connections"], dict):
            errors.append("'connections' must be a dictionary")

    return errors


def validate_node(node: Dict[str, Any], index: int) -> List[str]:
    """Validate a single workflow node.

    Args:
        node: Node data dictionary
        index: Node index for error reporting

    Returns:
        List of validation errors
    """
    errors = []

    required_fields = ["name", "type", "typeVersion", "position"]
    for field in required_fields:
        if field not in node:
            errors.append(f"Node {index}: Missing required field '{field}'")

    # Validate position
    if "position" in node:
        if not isinstance(node["position"], list) or len(node["position"]) != 2:
            errors.append(f"Node {index}: 'position' must be a list of two numbers")

    return errors


def validate_config_file(config_path: str) -> List[str]:
    """Validate a configuration file.

    Args:
        config_path: Path to the configuration file

    Returns:
        List of validation errors
    """
    errors = []

    try:
        from ..models.config import BuildConfig

        BuildConfig.from_yaml(config_path)
    except FileNotFoundError:
        errors.append(f"Configuration file not found: {config_path}")
    except Exception as e:
        errors.append(f"Invalid configuration: {str(e)}")

    return errors
