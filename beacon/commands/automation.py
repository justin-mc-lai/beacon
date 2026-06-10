"""Retired Beacon automation command surface.

The historical queue/job/launchd automation business surface is retired in
v1.6.0. The module remains importable for old internal imports, but it is not
registered by the CLI factory and it does not execute queue or scheduler logic.
"""

from __future__ import annotations

import json

import typer

app = typer.Typer(name="automation", help="Retired; use beacon-loop goal")


@app.callback(invoke_without_command=True)
def retired(
    json_output: bool = typer.Option(False, "--json", help="Emit JSON output."),
) -> None:
    payload = {
        "schema_version": "1.0",
        "surface": "automation",
        "status": "retired",
        "reason_code": "automation_retired_use_beacon_loop_goal",
        "message": "automation retired; use beacon-loop goal",
        "next_command": "beacon-loop goal",
    }
    if json_output:
        typer.echo(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        typer.echo(payload["message"], err=True)
    raise typer.Exit(2)
