"""Workflow comparison service for comparing built and pulled workflows."""

import json
import os
from typing import Dict, List, Any, Optional, Set
from difflib import unified_diff

from ..models.config import BuildConfig


class WorkflowComparator:
    """Service for comparing built and pulled workflows."""

    def __init__(self, config: BuildConfig) -> None:
        """Initialize the workflow comparator.

        Args:
            config: Build configuration
        """
        self.config = config

    def compare_all(self) -> Dict[str, Any]:
        """Compare all built workflows with pulled workflows.

        Returns:
            Comparison results dictionary
        """
        built_workflows = self._load_workflows(self.config.output_dir)
        pulled_workflows = self._load_workflows(self.config.pulled_dir)

        built_names = set(built_workflows.keys())
        pulled_names = set(pulled_workflows.keys())

        comparison = {
            "summary": {
                "built_count": len(built_names),
                "pulled_count": len(pulled_names),
                "common_count": len(built_names & pulled_names),
                "only_built": list(built_names - pulled_names),
                "only_pulled": list(pulled_names - built_names),
            },
            "workflows": {},
        }

        # Compare common workflows
        for name in built_names & pulled_names:
            comparison["workflows"][name] = self._compare_workflows(
                built_workflows[name], pulled_workflows[name], name
            )

        # Mark workflows that exist only in one set
        for name in built_names - pulled_names:
            comparison["workflows"][name] = {
                "status": "only_built",
                "differences": [],
                "identical": False,
            }

        for name in pulled_names - built_names:
            comparison["workflows"][name] = {
                "status": "only_pulled",
                "differences": [],
                "identical": False,
            }

        return comparison

    def compare_single(self, workflow_name: str) -> Optional[Dict[str, Any]]:
        """Compare a single workflow by name.

        Args:
            workflow_name: Name of the workflow to compare

        Returns:
            Comparison result dictionary, or None if workflow not found
        """
        built_workflows = self._load_workflows(self.config.output_dir)
        pulled_workflows = self._load_workflows(self.config.pulled_dir)

        # Check if workflow exists in either built or pulled
        if workflow_name not in built_workflows and workflow_name not in pulled_workflows:
            return None

        if workflow_name in built_workflows and workflow_name in pulled_workflows:
            # Both exist - compare them
            result = self._compare_workflows(
                built_workflows[workflow_name], 
                pulled_workflows[workflow_name], 
                workflow_name
            )
        elif workflow_name in built_workflows:
            # Only in built
            result = {
                "status": "only_built",
                "differences": [],
                "identical": False,
            }
        else:
            # Only in pulled
            result = {
                "status": "only_pulled", 
                "differences": [],
                "identical": False,
            }

        return {
            "workflow_name": workflow_name,
            "result": result
        }

    def _load_workflows(self, directory: str) -> Dict[str, Dict[str, Any]]:
        """Load all workflow files from a directory.

        Args:
            directory: Directory containing workflow JSON files

        Returns:
            Dictionary mapping workflow names to workflow data
        """
        workflows = {}

        if not os.path.exists(directory):
            return workflows

        for filename in os.listdir(directory):
            if filename.endswith(".json"):
                workflow_name = os.path.splitext(filename)[0]
                filepath = os.path.join(directory, filename)

                try:
                    with open(filepath, "r") as f:
                        workflows[workflow_name] = json.load(f)
                except (json.JSONDecodeError, IOError) as e:
                    print(f"Warning: Could not load workflow {filepath}: {e}")

        return workflows

    def _compare_workflows(
        self, built: Dict[str, Any], pulled: Dict[str, Any], name: str
    ) -> Dict[str, Any]:
        """Compare two workflow dictionaries.

        Args:
            built: Built workflow data
            pulled: Pulled workflow data
            name: Workflow name

        Returns:
            Comparison result dictionary
        """
        # Normalize workflows for comparison (remove timestamps, IDs, etc.)
        built_normalized = self._normalize_workflow(built)
        pulled_normalized = self._normalize_workflow(pulled)

        differences = []
        identical = built_normalized == pulled_normalized

        if not identical:
            differences = self._find_differences(built_normalized, pulled_normalized)

        return {
            "status": "identical" if identical else "different",
            "differences": differences,
            "identical": identical,
        }

    def _normalize_workflow(self, workflow: Dict[str, Any]) -> Dict[str, Any]:
        """Normalize a workflow for comparison by removing volatile fields.

        Args:
            workflow: Original workflow data

        Returns:
            Normalized workflow data
        """
        normalized = workflow.copy()

        # Remove fields that change between builds/pulls
        fields_to_remove = ["id", "createdAt", "updatedAt", "versionId"]

        for field in fields_to_remove:
            normalized.pop(field, None)

        # Normalize nodes if present
        if "nodes" in normalized:
            for node in normalized["nodes"]:
                for field in ["id"]:
                    node.pop(field, None)

        # Normalize connections if present
        if "connections" in normalized:
            # Sort connections for consistent comparison
            normalized["connections"] = self._sort_connections(
                normalized["connections"]
            )

        return normalized

    def _sort_connections(self, connections: Dict[str, Any]) -> Dict[str, Any]:
        """Sort connections for consistent comparison.

        Args:
            connections: Original connections data

        Returns:
            Sorted connections data
        """
        sorted_connections = {}
        for node_name in sorted(connections.keys()):
            sorted_connections[node_name] = connections[node_name]
        return sorted_connections

    def _find_differences(
        self, built: Dict[str, Any], pulled: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Find specific differences between two workflows.

        Args:
            built: Built workflow data
            pulled: Pulled workflow data

        Returns:
            List of difference descriptions
        """
        differences = []

        # Convert to JSON strings for diff comparison
        built_json = json.dumps(built, indent=2, sort_keys=True)
        pulled_json = json.dumps(pulled, indent=2, sort_keys=True)

        # Generate unified diff
        diff_lines = list(
            unified_diff(
                built_json.splitlines(keepends=True),
                pulled_json.splitlines(keepends=True),
                fromfile="built",
                tofile="pulled",
                lineterm="",
            )
        )

        if diff_lines:
            differences.append(
                {
                    "type": "content_diff",
                    "description": "Workflow content differs",
                    "diff": "".join(diff_lines),
                }
            )

        return differences

    def print_comparison_table(self, comparison: Dict[str, Any]) -> None:
        """Print a formatted comparison table.

        Args:
            comparison: Comparison results from compare_all()
        """
        summary = comparison["summary"]

        print("\n=== Workflow Comparison Summary ===")
        print(f"Built workflows: {summary['built_count']}")
        print(f"Pulled workflows: {summary['pulled_count']}")
        print(f"Common workflows: {summary['common_count']}")

        if summary["only_built"]:
            print(f"Only in built: {', '.join(summary['only_built'])}")

        if summary["only_pulled"]:
            print(f"Only in pulled: {', '.join(summary['only_pulled'])}")

        print("\n=== Individual Workflow Status ===")
        print(f"{'Workflow Name':<30} {'Status':<15} {'Differences'}")
        print("-" * 60)

        for name, result in comparison["workflows"].items():
            status = result["status"]
            diff_count = len(result["differences"])
            diff_text = f"{diff_count} differences" if diff_count > 0 else "None"

            status_symbol = {
                "identical": "✓",
                "different": "✗",
                "only_built": "→",
                "only_pulled": "←",
            }.get(status, "?")

            print(f"{name:<30} {status_symbol} {status:<14} {diff_text}")

        # Show detailed differences for non-identical workflows
        for name, result in comparison["workflows"].items():
            if result["status"] == "different" and result["differences"]:
                print(f"\n--- Differences in {name} ---")
                for diff in result["differences"]:
                    if diff["type"] == "content_diff":
                        print(diff["diff"])

    def print_single_comparison(self, comparison: Dict[str, Any]) -> None:
        """Print a formatted comparison for a single workflow.

        Args:
            comparison: Comparison result from compare_single()
        """
        workflow_name = comparison["workflow_name"]
        result = comparison["result"]
        status = result["status"]
        
        print(f"\n=== Workflow Comparison: {workflow_name} ===")
        
        status_messages = {
            "identical": "✓ Workflows are identical",
            "different": "✗ Workflows differ",
            "only_built": "→ Workflow exists only in built directory",
            "only_pulled": "← Workflow exists only in pulled directory",
        }
        
        print(status_messages.get(status, f"? Unknown status: {status}"))
        
        if result["differences"]:
            print(f"\nFound {len(result['differences'])} differences:")
            for diff in result["differences"]:
                if diff["type"] == "content_diff":
                    print("\n--- Content Differences ---")
                    print(diff["diff"])
        elif status == "different":
            print("\nWorkflows differ but no detailed differences available.")
        elif status == "identical":
            print("\nNo differences found.")
