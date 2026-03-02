"""Beacon init command"""
import typer
from typing import Optional

app = typer.Typer(name="init", help="Initialize Beacon project")


@app.command()
def run(
    project_root: Optional[str] = typer.Option("", "--project", "-p", help="Project root path"),
    dry_run: bool = typer.Option(False, "--dry-run/--apply", help="Preview or apply"),
    force: bool = typer.Option(False, "--force", help="Force append managed blocks"),
    with_claude: bool = typer.Option(True, "--with-claude/--without-claude", help="Manage CLAUDE.md"),
    with_agents: bool = typer.Option(True, "--with-agents/--without-agents", help="Manage AGENTS.md"),
):
    """Initialize Beacon project structure"""
    action = "Would create" if dry_run else "Creating"
    typer.echo(f"{action} Beacon project structure at: {project_root or '.'}")


@app.command()
def init_project(
    project_root: str = typer.Option("", "--project-root", "-p", help="Project root path"),
    dry_run: bool = typer.Option(True, "--dry-run/--apply", help="Preview or apply"),
    force: bool = typer.Option(False, "--force", help="Force append managed blocks"),
    with_claude: bool = typer.Option(True, "--with-claude/--without-claude", help="Manage CLAUDE.md"),
    with_agents: bool = typer.Option(True, "--with-agents/--without-agents", help="Manage AGENTS.md"),
):
    """Initialize Beacon project structure (alias)"""
    action = "Would create" if dry_run else "Creating"
    typer.echo(f"{action} Beacon project structure at: {project_root or '.'}")


if __name__ == "__main__":
    app()
