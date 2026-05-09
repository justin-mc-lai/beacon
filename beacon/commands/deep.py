from __future__ import annotations

import json
from pathlib import Path

import typer

from beacon.utils.deep_loop import (
    DEEP_ARTIFACT_FAMILY,
    DEEP_LOOP_STATES,
    build_deep_release_supplement_gate,
    deep_artifact_paths,
    load_deep_artifact,
    run_deep_loop,
)

app = typer.Typer(
    name="deep",
    help="Support-surface deep analysis loop and release supplement artifacts.",
    invoke_without_command=True,
    no_args_is_help=True,
)


def _root(project_root: str) -> Path:
    return Path(project_root).expanduser().resolve() if project_root else Path.cwd()


def _echo(payload: dict, json_output: bool) -> None:
    if json_output:
        typer.echo(json.dumps(payload, ensure_ascii=False, indent=2))
        return
    typer.echo(f"status: {payload.get('status', '')}")
    typer.echo(f"feature: {payload.get('feature', '')}")
    typer.echo(f"version: {payload.get('version', '')}")
    if payload.get("deep_requirement_state"):
        typer.echo(f"deep_requirement_state: {payload.get('deep_requirement_state')}")
    if payload.get("verdict"):
        typer.echo(f"verdict: {payload.get('verdict')}")
    supplement = payload.get("release_supplement") if isinstance(payload.get("release_supplement"), dict) else payload
    if supplement.get("reason_codes"):
        typer.echo(f"reason_codes: {', '.join(supplement.get('reason_codes') or [])}")
    artifact_refs = payload.get("artifact_refs") if isinstance(payload.get("artifact_refs"), dict) else supplement.get("artifact_refs")
    if isinstance(artifact_refs, dict):
        typer.echo("artifacts:")
        for key, refs in artifact_refs.items():
            if isinstance(refs, dict):
                typer.echo(f"- {key}: {refs.get('json', '')}")


@app.command("run")
def run(
    feature: str = typer.Argument(..., help="Feature name"),
    project_root: str = typer.Option("", "--project-root", "--project", "-p", help="Project root path"),
    version: str = typer.Option("auto", "--version", "-v", help="Docs version"),
    intent: str = typer.Option("", "--intent", help="User intent snapshot for the deep trace"),
    skip_reason: str = typer.Option("", "--skip-reason", help="Explicit low-risk skip reason"),
    qa_feedback: str = typer.Option("", "--qa-feedback", help="QA feedback text that may reopen deep for structural gaps"),
    qa_severity: str = typer.Option("", "--qa-severity", help="QA severity, such as P0/P1/P2"),
    json_output: bool = typer.Option(False, "--json", help="Emit JSON payload"),
):
    """Run the full deep loop once and write auditable support artifacts."""
    try:
        payload = run_deep_loop(
            _root(project_root),
            version=version,
            feature=feature,
            intent=intent,
            skip_reason=skip_reason,
            qa_feedback=qa_feedback,
            qa_severity=qa_severity,
        )
    except ValueError as exc:
        raise typer.BadParameter(str(exc)) from exc
    _echo(payload, json_output)


@app.command("status")
def status(
    feature: str = typer.Argument(..., help="Feature name"),
    project_root: str = typer.Option("", "--project-root", "--project", "-p", help="Project root path"),
    version: str = typer.Option("auto", "--version", "-v", help="Docs version"),
    json_output: bool = typer.Option(False, "--json", help="Emit JSON payload"),
):
    """Show release-facing deep supplement status."""
    payload = build_deep_release_supplement_gate(_root(project_root), version=version, feature=feature)
    payload["feature"] = feature
    _echo(payload, json_output)
    raise typer.Exit(code=2 if payload.get("blocked") else 0)


@app.command("report")
def report(
    feature: str = typer.Argument(..., help="Feature name"),
    artifact: str = typer.Option("closure_brief", "--artifact", help=f"Artifact: {', '.join(DEEP_ARTIFACT_FAMILY)}"),
    project_root: str = typer.Option("", "--project-root", "--project", "-p", help="Project root path"),
    version: str = typer.Option("auto", "--version", "-v", help="Docs version"),
    json_output: bool = typer.Option(False, "--json", help="Emit JSON payload"),
):
    """Read a generated deep artifact."""
    root = _root(project_root)
    payload = load_deep_artifact(root, version=version, feature=feature, artifact=artifact)
    if not payload:
        refs = deep_artifact_paths(root, version, feature).get(artifact, {})
        payload = {
            "schema_version": "1.0",
            "status": "missing",
            "feature": feature,
            "artifact": artifact,
            "expected": refs,
        }
        _echo(payload, json_output)
        raise typer.Exit(code=1)
    _echo(payload, json_output)


@app.command("contract")
def contract(json_output: bool = typer.Option(False, "--json", help="Emit JSON payload")):
    """Show static deep loop states and artifact family."""
    payload = {
        "schema_version": "1.0",
        "status": "pass",
        "surface": "support",
        "not_lifecycle_stage": True,
        "preferred_entry": "beacon deep run",
        "loop_states": DEEP_LOOP_STATES,
        "artifact_family": DEEP_ARTIFACT_FAMILY,
        "qa_execution_owner": "qa",
        "truth_policy": "deep artifacts are projections/evidence and cannot rewrite frozen truth",
    }
    _echo(payload, json_output)
