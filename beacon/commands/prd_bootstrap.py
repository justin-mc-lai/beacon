"""Hidden PRD bootstrap command surface (optional skill backend)."""

from __future__ import annotations

import json
from pathlib import Path

import typer

from beacon.utils.prd_bootstrap import run_prd_bootstrap

app = typer.Typer(
    name="prd-bootstrap",
    help="Optional one-click requirement bootstrap (safe-by-default).",
    invoke_without_command=True,
    no_args_is_help=True,
)


def _print_human(payload: dict) -> None:
    typer.echo("Beacon PRD Bootstrap")
    typer.echo("=" * 21)
    typer.echo(f"run_id           : {payload.get('run_id', '')}")
    typer.echo(f"feature          : {payload.get('feature', '')}")
    typer.echo(f"version          : {payload.get('version', '')}")
    typer.echo(f"status           : {payload.get('status', '')}")
    typer.echo(f"package_state    : {payload.get('package_state', '')}")
    typer.echo(f"closure_verdict  : {payload.get('closure_verdict', '')}")
    typer.echo(f"readiness_verdict: {payload.get('readiness_verdict', '')}")
    typer.echo(f"dry_run          : {payload.get('dry_run', True)}")
    typer.echo(f"no_overwrite     : {payload.get('no_overwrite', True)}")
    typer.echo(f"state_path       : {payload.get('state_path', '')}")
    quality = payload.get("quality") if isinstance(payload.get("quality"), dict) else {}
    consistency = payload.get("consistency") if isinstance(payload.get("consistency"), dict) else {}
    closure = payload.get("closure_analysis") if isinstance(payload.get("closure_analysis"), dict) else {}
    typer.echo(f"quality_ok       : {quality.get('ok', False)}")
    typer.echo(f"consistency_ok   : {consistency.get('ok', False)}")
    typer.echo(f"closure_ok       : {closure.get('ok', False)}")
    reverse_derived = payload.get("reverse_derived_layers") if isinstance(payload.get("reverse_derived_layers"), list) else []
    drift_digest = payload.get("drift_digest") if isinstance(payload.get("drift_digest"), list) else []
    typer.echo(f"reverse_derived  : {len(reverse_derived)}")
    typer.echo(f"drift_items      : {len(drift_digest)}")
    if payload.get("reason_code"):
        typer.echo(f"reason_code      : {payload.get('reason_code')}")
    if payload.get("recommended_command"):
        typer.echo(f"next_command     : {payload.get('recommended_command')}")


@app.command("run")
def run(
    feature: str = typer.Argument(..., help="Feature name"),
    description: str = typer.Option(..., "--desc", help="Feature description"),
    project_root: str = typer.Option("", "--project-root", "-p", help="Project root path"),
    version: str = typer.Option("auto", "--version", "-v", help="Docs version (auto=project default)"),
    apply: bool = typer.Option(False, "--apply", help="Apply writes (default is dry-run)"),
    dry_run: bool = typer.Option(False, "--dry-run", help="Force dry-run preview"),
    no_overwrite: bool = typer.Option(True, "--no-overwrite/--allow-overwrite", help="Block overwriting existing docs by default"),
    legacy_split: bool = typer.Option(False, "--legacy-split", help="Generate legacy prd/user-story/test-case split docs explicitly"),
    strict_context_verify: bool = typer.Option(True, "--strict-context-verify/--skip-context-verify", help="Require doctor context verify before generating docs"),
    max_placeholders: int = typer.Option(0, "--max-placeholders", min=0, help="Allowed placeholder count threshold"),
    json_output: bool = typer.Option(False, "--json", help="Emit JSON payload"),
):
    """Generate PRD + user-story + test-case docs with safety guards."""
    root = Path(project_root).expanduser().resolve() if project_root else Path.cwd()
    try:
        payload = run_prd_bootstrap(
            root,
            feature=feature,
            description=description,
            version=version,
            apply=apply,
            dry_run=dry_run,
            no_overwrite=no_overwrite,
            legacy_split=legacy_split,
            strict_context_verify=strict_context_verify,
            max_placeholders=max_placeholders,
        )
    except ValueError as exc:
        raise typer.BadParameter(str(exc)) from exc

    if json_output:
        typer.echo(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        _print_human(payload)
    if str(payload.get("status", "")).lower() == "blocked":
        raise typer.Exit(code=2)
