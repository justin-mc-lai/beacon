"""Beacon Toolkit Lighthouse command surface."""

from __future__ import annotations

from pathlib import Path

import typer

from beacon.utils.lighthouse import (
    SUPPORTED_LIGHTHOUSE_MODES,
    generate_lighthouse_artifact,
    payload_to_json,
    render_lighthouse_human,
)

app = typer.Typer(
    name="lighthouse",
    help="Toolkit Lighthouse single-file analysis outside Beacon main workflow.",
    invoke_without_command=True,
    no_args_is_help=False,
)


def _run_lighthouse(
    *,
    project_root: str,
    version: str,
    mode: str,
    target: str,
    output: str,
    json_output: bool,
    write_versioned_output: bool | None,
) -> int:
    root = Path(project_root).expanduser().resolve() if project_root else Path.cwd()
    try:
        payload = generate_lighthouse_artifact(
            root,
            target=target or None,
            mode=mode,
            version=version,
            output_path=output or None,
            write_versioned_output=write_versioned_output,
        )
    except ValueError as exc:
        raise typer.BadParameter(str(exc)) from exc
    if json_output:
        typer.echo(payload_to_json(payload))
    else:
        typer.echo(render_lighthouse_human(payload, project_root=root))
    return 0


@app.callback(invoke_without_command=True)
def lighthouse_entry(
    ctx: typer.Context,
    project_root: str = typer.Option("", "--project-root", "-p", help="Project root path"),
    version: str = typer.Option("auto", "--version", "-v", help="Docs version (auto=project default)"),
    mode: str = typer.Option(
        "system-architecture-map",
        "--mode",
        help=f"Analysis mode: {', '.join(SUPPORTED_LIGHTHOUSE_MODES)}",
    ),
    target: str = typer.Option("", "--target", "-t", help="Target path inside project root"),
    output: str = typer.Option("", "--output", "-o", help="Optional output markdown path"),
    json_output: bool = typer.Option(False, "--json", help="Emit JSON payload"),
    write_versioned_output: bool = typer.Option(
        False,
        "--write-versioned-output",
        help="Also write docs/beacon/<version>/execution/beacon-toolkit-lighthouse-<slug>.md",
    ),
):
    """Generate a single-file Lighthouse map using the default mode."""
    if ctx.invoked_subcommand is None:
        raise typer.Exit(
            code=_run_lighthouse(
                project_root=project_root,
                version=version,
                mode=mode,
                target=target,
                output=output,
                json_output=json_output,
                write_versioned_output=True if write_versioned_output else None,
            )
        )


@app.command("run")
def run(
    project_root: str = typer.Option("", "--project-root", "-p", help="Project root path"),
    version: str = typer.Option("auto", "--version", "-v", help="Docs version (auto=project default)"),
    mode: str = typer.Option(
        "system-architecture-map",
        "--mode",
        help=f"Analysis mode: {', '.join(SUPPORTED_LIGHTHOUSE_MODES)}",
    ),
    target: str = typer.Option("", "--target", "-t", help="Target path inside project root"),
    output: str = typer.Option("", "--output", "-o", help="Optional output markdown path"),
    json_output: bool = typer.Option(False, "--json", help="Emit JSON payload"),
    write_versioned_output: bool = typer.Option(
        False,
        "--write-versioned-output",
        help="Also write docs/beacon/<version>/execution/beacon-toolkit-lighthouse-<slug>.md",
    ),
):
    """Explicit Lighthouse run command."""
    raise typer.Exit(
        code=_run_lighthouse(
            project_root=project_root,
            version=version,
            mode=mode,
            target=target,
            output=output,
            json_output=json_output,
            write_versioned_output=True if write_versioned_output else None,
        )
    )
