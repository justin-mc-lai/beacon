"""Beacon automation support surface."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Optional

import typer

from beacon.utils.automation_capabilities import (
    build_automation_capabilities_payload,
    render_automation_capabilities_markdown,
)
from beacon.utils.automation_feedback import (
    refresh_qa_feedback_ledger,
    update_automation_queue_from_feedback,
)
from beacon.utils.automation_summary import build_automation_summary_payload
from beacon.utils.automation_queue import (
    build_automation_queue_validation_payload,
    default_queue_path,
)
from beacon.utils.automation_scaffold import (
    init_automation_scaffold,
    render_automation_init_markdown,
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


@app.command("validate-queue")
def validate_queue(
    project_root: str = typer.Option("", "--project-root", help="Project root path."),
    queue: str = typer.Option("", "--queue", help="Queue file path."),
    json_output: bool = typer.Option(False, "--json", help="Emit JSON output."),
):
    """Validate the host-scheduled automation queue contract."""
    root = Path(project_root) if project_root else Path.cwd()
    queue_path = Path(queue) if queue else default_queue_path(root)
    payload = build_automation_queue_validation_payload(root, queue_path)
    if json_output:
        typer.echo(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        typer.echo(json.dumps(payload, ensure_ascii=False, indent=2))
    if payload["status"] != "valid":
        raise typer.Exit(2)


@app.command("summarize-qa")
def summarize_qa(
    project_root: str = typer.Option("", "--project-root", help="Project root path."),
    feature: list[str] = typer.Option([], "--feature", help="Feature name to include (repeatable)."),
    json_output: bool = typer.Option(False, "--json", help="Emit JSON output."),
):
    """Build or refresh the QA feedback ledger used by automation jobs."""
    root = Path(project_root) if project_root else Path.cwd()
    payload = refresh_qa_feedback_ledger(root, features=feature or None)
    typer.echo(json.dumps(payload, ensure_ascii=False, indent=2))


@app.command("build-summary")
def build_summary(
    project_root: str = typer.Option("", "--project-root", help="Project root path."),
    summary_kind: str = typer.Option("qa", "--summary-kind", help="Summary kind: qa|functional|exception|regression|nightly."),
    job: str = typer.Option(..., "--job", help="Automation job id."),
    layer: str = typer.Option("qa", "--layer", help="Automation layer name."),
    status: str = typer.Option("", "--status", help="Explicit overall status."),
    ledger_path: str = typer.Option("", "--ledger-path", help="QA ledger JSON path."),
    queue_update_path: str = typer.Option("", "--queue-update-path", help="Queue update JSON path."),
    tests: Optional[int] = typer.Option(None, "--tests", help="Executed test count."),
    failures: Optional[int] = typer.Option(None, "--failures", help="Failure count."),
    skipped: Optional[int] = typer.Option(None, "--skipped", help="Skipped count."),
    feature: list[str] = typer.Option([], "--feature", help="Feature name to include (repeatable)."),
    release_ready_feature: list[str] = typer.Option([], "--release-ready-feature", help="Release-ready feature name (repeatable)."),
    repair_feature: list[str] = typer.Option([], "--repair-feature", help="Repair-needed feature name (repeatable)."),
    artifact: list[str] = typer.Option([], "--artifact", help="Artifact key=value pair (repeatable)."),
):
    """Build the shared automation summary payload used by notifications and operator summaries."""
    root = Path(project_root) if project_root else Path.cwd()
    artifact_payload: dict[str, str] = {}
    for item in artifact:
        text = str(item or "").strip()
        if not text or "=" not in text:
            continue
        key, value = text.split("=", 1)
        key = key.strip()
        value = value.strip()
        if key and value:
            artifact_payload[key] = value
    payload = build_automation_summary_payload(
        project_root=root,
        summary_kind=summary_kind,
        job=job,
        layer=layer,
        status=status,
        ledger_path=Path(ledger_path) if ledger_path else None,
        queue_update_path=Path(queue_update_path) if queue_update_path else None,
        tests=tests,
        failures=failures,
        skipped=skipped,
        artifacts=artifact_payload,
        features=feature or None,
        release_ready_features=release_ready_feature or None,
        repair_features=repair_feature or None,
    )
    typer.echo(json.dumps(payload, ensure_ascii=False, indent=2))


@app.command("update-queue")
def update_queue(
    project_root: str = typer.Option("", "--project-root", help="Project root path."),
    queue: str = typer.Option("", "--queue", help="Queue file path."),
    json_output: bool = typer.Option(False, "--json", help="Emit JSON output."),
):
    """Update the automation queue from the QA feedback ledger."""
    root = Path(project_root) if project_root else Path.cwd()
    queue_path = Path(queue) if queue else default_queue_path(root)
    payload = update_automation_queue_from_feedback(root, queue_path=queue_path)
    typer.echo(json.dumps(payload, ensure_ascii=False, indent=2))


@app.command("init")
def init(
    project_root: str = typer.Option("", "--project-root", help="Project root path."),
    executor: str = typer.Option("codex", "--executor", help="Executor profile: codex|claude|cursor|windsurf|trae."),
    force: bool = typer.Option(False, "--force", help="Refresh existing automation scaffold files."),
    json_output: bool = typer.Option(False, "--json", help="Emit JSON output."),
):
    """Generate project-local automation scaffold assets."""
    root = Path(project_root) if project_root else Path.cwd()
    payload = init_automation_scaffold(root, force=force, executor=executor)
    if json_output:
        typer.echo(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        typer.echo(render_automation_init_markdown(payload), nl=False)
    if payload.get("status") != "completed":
        raise typer.Exit(2)
