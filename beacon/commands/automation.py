"""Beacon automation support surface."""

from __future__ import annotations

import json
from pathlib import Path

import typer

from beacon.utils.automation_capabilities import (
    build_automation_capabilities_payload,
    render_automation_capabilities_markdown,
)

app = typer.Typer(
    name="automation",
    help="Host-scheduled automation support surfaces",
    invoke_without_command=True,
    no_args_is_help=True,
)


@app.command("capabilities")
def capabilities(
    project_root: str = typer.Option("", "--project-root", help="Project root path."),
    json_output: bool = typer.Option(False, "--json", help="Emit JSON output."),
):
    """Explain Beacon's supported host-scheduled automation capability plane."""
    root = Path(project_root) if project_root else Path.cwd()
    payload = build_automation_capabilities_payload(root)
    if json_output:
        typer.echo(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        typer.echo(render_automation_capabilities_markdown(payload), nl=False)
