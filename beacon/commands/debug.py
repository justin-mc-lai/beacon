"""Beacon debug command."""

from __future__ import annotations

import time
from pathlib import Path

import typer

from beacon.utils.runtime import newest_run_id, run_events_path

app = typer.Typer(name="debug", help="Debug helpers")


@app.command()
def watch(
    run_id: str = typer.Argument("", help="Run ID"),
    tail: int = typer.Option(20, "--tail", "-n", help="Tail lines"),
    follow: bool = typer.Option(False, "--follow", "-f", help="Follow mode"),
    poll_interval: float = typer.Option(0.2, "--poll-interval", help="Polling interval seconds"),
    idle_exit: float = typer.Option(2.0, "--idle-exit", help="Exit after idle seconds (<=0 never exits)"),
    project_root: str = typer.Option("", "--project-root", help="Project root path"),
):
    """Watch run events."""
    root = Path(project_root) if project_root else Path.cwd()
    target_run = run_id or newest_run_id(root)
    if not target_run:
        typer.echo("No run found.", err=True)
        raise typer.Exit(code=2)

    events_file = run_events_path(root, target_run)
    if not events_file.exists():
        typer.echo(f"No events for run: {target_run}", err=True)
        raise typer.Exit(code=2)

    lines = events_file.read_text(encoding="utf-8").splitlines()
    tail_lines = lines[-tail:] if tail > 0 else lines
    for line in tail_lines:
        typer.echo(line)

    if not follow:
        return

    consumed = len(lines)
    idle_for = 0.0
    while True:
        time.sleep(max(poll_interval, 0.05))
        latest = events_file.read_text(encoding="utf-8").splitlines()
        if len(latest) > consumed:
            for line in latest[consumed:]:
                typer.echo(line)
            consumed = len(latest)
            idle_for = 0.0
            continue

        idle_for += max(poll_interval, 0.05)
        if idle_exit > 0 and idle_for >= idle_exit:
            break


if __name__ == "__main__":
    app()

