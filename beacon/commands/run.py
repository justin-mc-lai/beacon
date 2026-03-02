"""Beacon run command"""
import typer
from typing import Optional

app = typer.Typer(name="run", help="Run Beacon workflow")


@app.command()
def workflow(
    workflow_type: str = typer.Argument(..., help="Workflow type: workflow/team/auto-test"),
    mode: str = typer.Option("normal", "--mode", "-m", help="Run mode: normal/debug/strict/dry-run/replay"),
    feature: str = typer.Option("", "--feature", "-f", help="Feature name"),
    version: str = typer.Option("v1.0.0", "--version", "-v", help="Version"),
    strict: bool = typer.Option(False, "--strict", help="Enable strict mode"),
    json_output: bool = typer.Option(False, "--json", help="JSON output"),
    project_root: str = typer.Option("", "--project-root", help="Project root path"),
):
    """Run Beacon workflow"""
    typer.echo(f"Running {workflow_type} in {mode} mode")
    typer.echo(f"Feature: {feature}, Version: {version}")
    if strict:
        typer.echo("Strict mode: enabled")


if __name__ == "__main__":
    app()
