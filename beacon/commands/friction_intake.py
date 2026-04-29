"""Friction intake command surface."""

from __future__ import annotations

from pathlib import Path

import typer

from beacon.utils.friction_intake import (
    SUPPORTED_FRICTION_INTAKE_MODES,
    apply_friction_action,
    friction_intake_payload_json,
    load_friction_inbox,
    load_latest_friction_intake_report,
    render_friction_intake_human,
    run_friction_intake,
)

app = typer.Typer(
    name="friction-intake",
    help="Support-surface friction intake and sqlite governance queue.",
    invoke_without_command=True,
    no_args_is_help=False,
)


def _root(project_root: str) -> Path:
    return Path(project_root).expanduser().resolve() if project_root else Path.cwd()


def _run(
    *,
    project_root: str,
    version: str,
    mode: str,
    note: str,
    limit: int,
    json_output: bool,
) -> int:
    try:
        payload = run_friction_intake(
            _root(project_root),
            version=version,
            mode=mode,
            note=note,
            limit=limit,
        )
    except ValueError as exc:
        raise typer.BadParameter(str(exc)) from exc
    typer.echo(friction_intake_payload_json(payload) if json_output else render_friction_intake_human(payload))
    return 0


@app.callback(invoke_without_command=True)
def friction_intake_entry(
    ctx: typer.Context,
    project_root: str = typer.Option("", "--project-root", "-p", help="Project root path"),
    version: str = typer.Option("auto", "--version", "-v", help="Docs version (auto=project default)"),
    mode: str = typer.Option("scan", "--mode", help=f"Mode: {', '.join(SUPPORTED_FRICTION_INTAKE_MODES)}"),
    note: str = typer.Option("", "--note", help="Manual note for mode=capture"),
    limit: int = typer.Option(10, "--limit", min=1, help="Maximum items to persist"),
    json_output: bool = typer.Option(False, "--json", help="Emit JSON payload"),
):
    """Run friction intake once (default entry)."""
    if ctx.invoked_subcommand is None:
        raise typer.Exit(
            code=_run(
                project_root=project_root,
                version=version,
                mode=mode,
                note=note,
                limit=limit,
                json_output=json_output,
            )
        )


@app.command("run")
def run(
    project_root: str = typer.Option("", "--project-root", "-p", help="Project root path"),
    version: str = typer.Option("auto", "--version", "-v", help="Docs version (auto=project default)"),
    mode: str = typer.Option("scan", "--mode", help=f"Mode: {', '.join(SUPPORTED_FRICTION_INTAKE_MODES)}"),
    note: str = typer.Option("", "--note", help="Manual note for mode=capture"),
    limit: int = typer.Option(10, "--limit", min=1, help="Maximum items to persist"),
    json_output: bool = typer.Option(False, "--json", help="Emit JSON payload"),
):
    """Explicit run entry for friction intake."""
    raise typer.Exit(
        code=_run(
            project_root=project_root,
            version=version,
            mode=mode,
            note=note,
            limit=limit,
            json_output=json_output,
        )
    )


@app.command("report")
def report(
    project_root: str = typer.Option("", "--project-root", "-p", help="Project root path"),
    json_output: bool = typer.Option(False, "--json", help="Emit JSON payload"),
):
    """Show the latest friction intake report."""
    payload = load_latest_friction_intake_report(_root(project_root))
    if not payload:
        typer.echo("{}" if json_output else "No friction intake report found.")
        raise typer.Exit(code=1)
    typer.echo(friction_intake_payload_json(payload) if json_output else render_friction_intake_human(payload))


@app.command("inbox")
def inbox(
    project_root: str = typer.Option("", "--project-root", "-p", help="Project root path"),
    limit: int = typer.Option(20, "--limit", min=1, help="Maximum items to list"),
    json_output: bool = typer.Option(False, "--json", help="Emit JSON payload"),
):
    """List queued friction items from the global sqlite queue."""
    items = load_friction_inbox(_root(project_root), limit=limit)
    typer.echo(friction_intake_payload_json({"items": items}) if json_output else render_friction_intake_human({"items": items}))


def _transition(project_root: str, item_id: str, action: str, json_output: bool) -> int:
    try:
        payload = apply_friction_action(_root(project_root), item_id=item_id, action=action)
    except ValueError as exc:
        raise typer.BadParameter(str(exc)) from exc
    typer.echo(friction_intake_payload_json(payload) if json_output else friction_intake_payload_json(payload))
    return 0


@app.command("claim")
def claim(
    item_id: str = typer.Argument(..., help="Friction item id"),
    project_root: str = typer.Option("", "--project-root", "-p", help="Project root path"),
    json_output: bool = typer.Option(False, "--json", help="Emit JSON payload"),
):
    """Mark a queued friction item as claimed."""
    raise typer.Exit(code=_transition(project_root, item_id, "claim", json_output))


@app.command("resolve")
def resolve(
    item_id: str = typer.Argument(..., help="Friction item id"),
    project_root: str = typer.Option("", "--project-root", "-p", help="Project root path"),
    json_output: bool = typer.Option(False, "--json", help="Emit JSON payload"),
):
    """Mark a claimed friction item as resolved."""
    raise typer.Exit(code=_transition(project_root, item_id, "resolve", json_output))


@app.command("reopen")
def reopen(
    item_id: str = typer.Argument(..., help="Friction item id"),
    project_root: str = typer.Option("", "--project-root", "-p", help="Project root path"),
    json_output: bool = typer.Option(False, "--json", help="Emit JSON payload"),
):
    """Reopen a resolved friction item."""
    raise typer.Exit(code=_transition(project_root, item_id, "reopen", json_output))


@app.command("accept")
def accept(
    item_id: str = typer.Argument(..., help="Friction item id"),
    project_root: str = typer.Option("", "--project-root", "-p", help="Project root path"),
    json_output: bool = typer.Option(False, "--json", help="Emit JSON payload"),
):
    """Mark a friction item as accepted for requirement/change routing."""
    raise typer.Exit(code=_transition(project_root, item_id, "accept", json_output))
