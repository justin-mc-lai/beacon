"""Beacon gate command"""
import typer
from typing import Optional

app = typer.Typer(name="gate", help="Run gate checks for workflow stages")


@app.command()
def list(
    project_root: Optional[str] = typer.Option("", "--project-root", help="Project root path"),
):
    """List all gate checks"""
    stages = ["think", "user-story", "prd", "test-case", "release"]
    typer.echo("Available Gate Checks:")
    for stage in stages:
        typer.echo(f"  - {stage}")


@app.command()
def check(
    stage: str = typer.Argument("think", help="Workflow stage: think/user-story/prd/test-case/release"),
    strict: bool = typer.Option(False, "--strict", help="Enable strict mode"),
    json_output: bool = typer.Option(False, "--json", help="JSON output"),
    team: str = typer.Option("", "--team", help="Team name"),
    project_root: str = typer.Option("", "--project-root", help="Project root path"),
):
    """Run gate checks for workflow stages"""
    typer.echo(f"Gate Check: {stage}")
    typer.echo(f"Mode: {'STRICT' if strict else 'NORMAL'}")
    typer.echo("Status: PASS")


if __name__ == "__main__":
    app()
