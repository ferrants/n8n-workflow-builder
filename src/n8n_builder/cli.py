"""Command line interface for n8n workflow builder."""

import click
import os
from typing import Optional

from .models.config import BuildConfig
from .services.secrets import SecretsService
from .services.builder import WorkflowBuilder
from .services.n8n_client import N8nClient
from .services.comparator import WorkflowComparator


@click.group()
@click.version_option()
def cli() -> None:
    """n8n Workflow Builder - Build, manage, and deploy n8n workflows."""
    pass


@cli.command()
@click.argument('config_file', type=click.Path(exists=True))
@click.option('--env-file', '-e', help='Path to .env file', default='.env')
def build(config_file: str, env_file: str) -> None:
    """Build all workflows defined in the config file."""
    try:
        config = BuildConfig.from_yaml(config_file)
        secrets = SecretsService(env_file)
        builder = WorkflowBuilder(config, secrets)
        
        click.echo(f"Building workflows from {config_file}...")
        results = builder.build_all()
        
        click.echo(f"Successfully built {len(results)} workflows:")
        for result in results:
            click.echo(f"  ✓ {result['name']} -> {result['output_path']}")
            
    except Exception as e:
        click.echo(f"Error building workflows: {e}", err=True)
        raise click.Abort()


@cli.command()
@click.argument('config_file', type=click.Path(exists=True))
@click.option('--env-file', '-e', help='Path to .env file', default='.env')
def pull(config_file: str, env_file: str) -> None:
    """Pull workflows from the n8n instance."""
    try:
        config = BuildConfig.from_yaml(config_file)
        secrets = SecretsService(env_file)
        
        api_key = secrets.get_required_secret(config.n8n_instance.api_key_env)
        client = N8nClient(config.n8n_instance.url, api_key)
        
        click.echo(f"Pulling workflows from {config.n8n_instance.url}...")
        
        os.makedirs(config.pulled_dir, exist_ok=True)
        workflows = client.get_all_workflows()
        
        for workflow in workflows:
            output_path = os.path.join(config.pulled_dir, f"{workflow['name']}.json")
            client.save_workflow(workflow, output_path)
            click.echo(f"  ✓ {workflow['name']} -> {output_path}")
        
        click.echo(f"Successfully pulled {len(workflows)} workflows")
        
    except Exception as e:
        click.echo(f"Error pulling workflows: {e}", err=True)
        raise click.Abort()


@cli.command()
@click.argument('config_file', type=click.Path(exists=True))
@click.option('--env-file', '-e', help='Path to .env file', default='.env')
@click.option('--dry-run', is_flag=True, help='Show what would be uploaded without actually doing it')
def push(config_file: str, env_file: str, dry_run: bool) -> None:
    """Push built workflows to the n8n instance."""
    try:
        config = BuildConfig.from_yaml(config_file)
        secrets = SecretsService(env_file)
        
        api_key = secrets.get_required_secret(config.n8n_instance.api_key_env)
        client = N8nClient(config.n8n_instance.url, api_key)
        
        if dry_run:
            click.echo("DRY RUN - No workflows will be uploaded")
        
        click.echo(f"Pushing workflows to {config.n8n_instance.url}...")
        
        if not os.path.exists(config.output_dir):
            click.echo(f"Error: Built workflows directory '{config.output_dir}' not found. Run 'build' first.", err=True)
            raise click.Abort()
        
        workflow_files = [f for f in os.listdir(config.output_dir) if f.endswith('.json')]
        
        for workflow_file in workflow_files:
            workflow_path = os.path.join(config.output_dir, workflow_file)
            workflow_name = os.path.splitext(workflow_file)[0]
            
            if dry_run:
                click.echo(f"  Would upload: {workflow_name} from {workflow_path}")
            else:
                result = client.upload_workflow(workflow_path, workflow_name)
                click.echo(f"  ✓ {workflow_name} -> {result['id']}")
        
        if not dry_run:
            click.echo(f"Successfully pushed {len(workflow_files)} workflows")
        
    except Exception as e:
        click.echo(f"Error pushing workflows: {e}", err=True)
        raise click.Abort()


@cli.command()
@click.argument('config_file', type=click.Path(exists=True))
@click.option('--format', '-f', type=click.Choice(['table', 'json']), default='table', help='Output format')
def compare(config_file: str, format: str) -> None:
    """Compare built workflows with pulled workflows."""
    try:
        config = BuildConfig.from_yaml(config_file)
        comparator = WorkflowComparator(config)
        
        click.echo("Comparing built and pulled workflows...")
        
        if not os.path.exists(config.output_dir):
            click.echo(f"Error: Built workflows directory '{config.output_dir}' not found. Run 'build' first.", err=True)
            raise click.Abort()
            
        if not os.path.exists(config.pulled_dir):
            click.echo(f"Error: Pulled workflows directory '{config.pulled_dir}' not found. Run 'pull' first.", err=True)
            raise click.Abort()
        
        comparison = comparator.compare_all()
        
        if format == 'json':
            import json
            click.echo(json.dumps(comparison, indent=2))
        else:
            comparator.print_comparison_table(comparison)
        
    except Exception as e:
        click.echo(f"Error comparing workflows: {e}", err=True)
        raise click.Abort()


def main() -> None:
    """Main entry point for the CLI."""
    cli()