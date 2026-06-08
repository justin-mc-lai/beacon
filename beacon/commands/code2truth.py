"""Code2Truth intake command surface."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Optional

import typer

from beacon.utils.code2truth import run_code2truth_intake
from beacon.utils.versioning import resolve_target_version

app = typer.Typer(
    name="code2truth",
    help="Build evidence-backed candidate truth from existing project source.",
    no_args_is_help=True,
)


@app.command("intake")
def intake(
    target_project_root: str = typer.Argument(..., help="Existing project root to analyze"),
    project: Optional[str] = typer.Option(None, "--project", "--project-root", "-p", help="Beacon project root"),
    version: str = typer.Option("auto", "--version", "-v", help="Beacon docs version"),
    feature: str = typer.Option("code2truth-project-intake", "--feature", "-f", help="Beacon feature or contract slug"),
    provider: str = typer.Option("auto", "--provider", help="Provider set: auto/beacon/understand-anything"),
    lighthouse: bool = typer.Option(True, "--lighthouse/--no-lighthouse", help="Generate Beacon Lighthouse source evidence"),
    write: bool = typer.Option(True, "--write/--no-write", help="Write intake artifacts under .beacon/code2truth"),
    json_output: bool = typer.Option(False, "--json", help="Emit JSON payload"),
) -> None:
    """Analyze existing implementation source and emit candidate truth evidence."""

    project_root = (Path(project) if project else Path.cwd()).expanduser().resolve()
    target = Path(target_project_root).expanduser().resolve()
    resolved_version = resolve_target_version(project_root, version)
    payload = run_code2truth_intake(
        project_root,
        target_project_root=target,
        version=resolved_version,
        feature=feature,
        provider=provider,
        use_lighthouse=lighthouse,
        write=write,
    )
    if json_output:
        typer.echo(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        typer.echo(f"Code2Truth intake: {payload.get('status')}")
        typer.echo(f"target: {payload.get('target_project_root')}")
        typer.echo(f"candidate claims: {len(payload.get('candidate_truth', {}).get('claims', []))}")
        if payload.get("output_markdown_path"):
            typer.echo(f"output: {payload['output_markdown_path']}")

