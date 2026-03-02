"""Beacon resume command."""

from __future__ import annotations

import json
from pathlib import Path

import typer

from beacon.utils.runtime import load_run_state

app = typer.Typer(
    name="resume",
    help="Resume/inspect run state",
    invoke_without_command=True,
    no_args_is_help=False,
    context_settings={"allow_interspersed_args": True},
)


def _resume_impl(run_id: str, project_root: str) -> int:
    root = Path(project_root) if project_root else Path.cwd()
    state = load_run_state(root, run_id)
    if not state:
        typer.echo(f"Run not found: {run_id}", err=True)
        return 2
    typer.echo(json.dumps(state, ensure_ascii=False, indent=2))
    return 0


@app.callback(invoke_without_command=True)
def resume_callback(
    ctx: typer.Context,
    run_id: str = typer.Argument("", help="Run ID to resume"),
    project_root: str = typer.Option("", "--project-root", help="Project root path"),
):
    """Resume a previous run (PTK flat syntax compatibility)."""
    if ctx.invoked_subcommand is None:
        if not run_id:
            typer.echo("Missing run_id.", err=True)
            raise typer.Exit(code=2)
        raise typer.Exit(code=_resume_impl(run_id=run_id, project_root=project_root))


@app.command("restore")
def restore(
    run_id: str = typer.Argument(..., help="Run ID to resume"),
    project_root: str = typer.Option("", "--project-root", help="Project root path"),
):
    """Resume a previous run (nested compatibility)."""
    raise typer.Exit(code=_resume_impl(run_id=run_id, project_root=project_root))


if __name__ == "__main__":
    app()
