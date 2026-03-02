"""Beacon status command."""

from __future__ import annotations

import json
from pathlib import Path

import typer

from beacon.utils.runtime import newest_run_id, read_json
from beacon.utils.workflow_memory import compute_memory_metrics

app = typer.Typer(
    name="status",
    help="Show workflow status",
    invoke_without_command=True,
    no_args_is_help=False,
)


def _status_impl(board: bool, verbose: bool, project_root: str) -> int:
    root = Path(project_root) if project_root else Path.cwd()
    team_root = root / ".beacon" / "team"
    team_count = len([p for p in team_root.glob("*") if p.is_dir()]) if team_root.exists() else 0
    bridge_root = root / ".beacon" / "bridge"
    bridge_count = len([p for p in bridge_root.glob("*") if p.is_dir()]) if bridge_root.exists() else 0
    progress = read_json(root / ".beacon" / "test-progress.json", {})
    latest = newest_run_id(root)
    latest_state = read_json(root / ".beacon" / "runs" / latest / "state.json", {}) if latest else {}
    terminal_status = str(latest_state.get("status", "unknown")) if isinstance(latest_state, dict) else "unknown"
    memory_metrics = compute_memory_metrics(root, latest if latest else None)

    payload = {
        "team": {"known_teams": team_count},
        "gate": {"terminal_status": terminal_status},
        "bridge": {"known_bridges": bridge_count},
        "test": {"has_progress": bool(progress)},
        "run": {"latest_run_id": latest or ""},
        "memory": memory_metrics,
    }

    if board:
        typer.echo("Beacon Status Board")
        typer.echo(f"- team.known_teams: {team_count}")
        typer.echo(f"- gate.terminal_status: {terminal_status}")
        typer.echo(f"- bridge.known_bridges: {bridge_count}")
        typer.echo(f"- test.has_progress: {bool(progress)}")
        typer.echo(f"- memory.closure_complete: {memory_metrics.get('closure_complete')}")
        typer.echo(f"- memory.writebacks: {memory_metrics.get('writebacks')}")
        typer.echo(f"- memory.recall_injections: {memory_metrics.get('recall_injections')}")
        if verbose:
            typer.echo(f"- run.latest_run_id: {latest or 'none'}")
            typer.echo(f"- memory.missing_closure_stages: {memory_metrics.get('missing_closure_stages')}")
    else:
        typer.echo(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0


@app.callback(invoke_without_command=True)
def status_callback(
    ctx: typer.Context,
    board: bool = typer.Option(False, "--board", "-b", help="Render human board"),
    verbose: bool = typer.Option(False, "--verbose", help="Verbose output"),
    project_root: str = typer.Option("", "--project-root", help="Project root path"),
):
    """Show current status (PTK flat syntax compatibility)."""
    if ctx.invoked_subcommand is None:
        raise typer.Exit(code=_status_impl(board=board, verbose=verbose, project_root=project_root))


@app.command("show-status")
def show_status(
    board: bool = typer.Option(False, "--board", "-b", help="Render human board"),
    verbose: bool = typer.Option(False, "--verbose", help="Verbose output"),
    project_root: str = typer.Option("", "--project-root", help="Project root path"),
):
    """Show current workflow status."""
    raise typer.Exit(code=_status_impl(board=board, verbose=verbose, project_root=project_root))


if __name__ == "__main__":
    app()
