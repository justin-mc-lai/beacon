"""Memory/Friction evolution command surface."""

from __future__ import annotations

from pathlib import Path

import typer

from beacon.utils.memory_friction_evolution import (
    SUPPORTED_MFE_MODES,
    load_latest_memory_friction_report,
    memory_friction_payload_json,
    render_memory_friction_human,
    run_memory_friction_evolution,
)

app = typer.Typer(
    name="memory-friction-evolution",
    help="Optional toolkit for memory/friction evolution candidates (labs/hidden).",
    invoke_without_command=True,
    no_args_is_help=False,
)


def _run(
    *,
    project_root: str,
    version: str,
    mode: str,
    top_n: int,
    max_turns: int,
    with_lighthouse: bool,
    lighthouse_target: str,
    writeback: bool,
    json_output: bool,
) -> int:
    root = Path(project_root).expanduser().resolve() if project_root else Path.cwd()
    try:
        payload = run_memory_friction_evolution(
            root,
            version=version,
            mode=mode,
            top_n=top_n,
            max_turns=max_turns,
            with_lighthouse=with_lighthouse,
            lighthouse_target=lighthouse_target,
            writeback=writeback,
        )
    except ValueError as exc:
        raise typer.BadParameter(str(exc)) from exc

    if json_output:
        typer.echo(memory_friction_payload_json(payload))
    else:
        typer.echo(render_memory_friction_human(payload))
    return 0


@app.callback(invoke_without_command=True)
def mfe_entry(
    ctx: typer.Context,
    project_root: str = typer.Option("", "--project-root", "-p", help="Project root path"),
    version: str = typer.Option("auto", "--version", "-v", help="Docs version (auto=project default)"),
    mode: str = typer.Option("both", "--mode", help=f"Mode: {', '.join(SUPPORTED_MFE_MODES)}"),
    top_n: int = typer.Option(5, "--top-n", min=1, help="Maximum candidate rows to keep"),
    max_turns: int = typer.Option(3, "--max-turns", min=1, help="Maximum decision turns"),
    with_lighthouse: bool = typer.Option(False, "--with-lighthouse", help="Run toolkit in parallel with Lighthouse"),
    lighthouse_target: str = typer.Option("", "--target", "-t", help="Optional Lighthouse target path"),
    writeback: bool = typer.Option(False, "--writeback", help="Write keep/review candidates back into memory via upsert"),
    json_output: bool = typer.Option(False, "--json", help="Emit JSON payload"),
):
    """Run memory/friction evolution once (default entry)."""
    if ctx.invoked_subcommand is None:
        raise typer.Exit(
            code=_run(
                project_root=project_root,
                version=version,
                mode=mode,
                top_n=top_n,
                max_turns=max_turns,
                with_lighthouse=with_lighthouse,
                lighthouse_target=lighthouse_target,
                writeback=writeback,
                json_output=json_output,
            )
        )


@app.command("run")
def run(
    project_root: str = typer.Option("", "--project-root", "-p", help="Project root path"),
    version: str = typer.Option("auto", "--version", "-v", help="Docs version (auto=project default)"),
    mode: str = typer.Option("both", "--mode", help=f"Mode: {', '.join(SUPPORTED_MFE_MODES)}"),
    top_n: int = typer.Option(5, "--top-n", min=1, help="Maximum candidate rows to keep"),
    max_turns: int = typer.Option(3, "--max-turns", min=1, help="Maximum decision turns"),
    with_lighthouse: bool = typer.Option(False, "--with-lighthouse", help="Run toolkit in parallel with Lighthouse"),
    lighthouse_target: str = typer.Option("", "--target", "-t", help="Optional Lighthouse target path"),
    writeback: bool = typer.Option(False, "--writeback", help="Write keep/review candidates back into memory via upsert"),
    json_output: bool = typer.Option(False, "--json", help="Emit JSON payload"),
):
    """Explicit run entry for memory/friction evolution."""
    raise typer.Exit(
        code=_run(
            project_root=project_root,
            version=version,
            mode=mode,
            top_n=top_n,
            max_turns=max_turns,
            with_lighthouse=with_lighthouse,
            lighthouse_target=lighthouse_target,
            writeback=writeback,
            json_output=json_output,
        )
    )


@app.command("report")
def report(
    project_root: str = typer.Option("", "--project-root", "-p", help="Project root path"),
    json_output: bool = typer.Option(False, "--json", help="Emit JSON payload"),
):
    """Show latest memory/friction evolution report."""
    root = Path(project_root).expanduser().resolve() if project_root else Path.cwd()
    payload = load_latest_memory_friction_report(root)
    if not payload:
        typer.echo("{}" if json_output else "No memory/friction evolution report found.")
        raise typer.Exit(code=1)
    if json_output:
        typer.echo(memory_friction_payload_json(payload))
    else:
        typer.echo(render_memory_friction_human(payload))
