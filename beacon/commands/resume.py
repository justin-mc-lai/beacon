"""Beacon resume command entrypoints."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Optional

import typer

from beacon.commands.workflow import continue_workflow
from beacon.utils.material_audit import build_material_audit
from beacon.utils.runtime import load_run_state
from beacon.utils.workflow_memory import compute_memory_metrics


def _resume_impl(run_id: str, project_root: str) -> int:
    root = Path(project_root) if project_root else Path.cwd()
    state = load_run_state(root, run_id)
    if not state:
        typer.echo(f"Run not found: {run_id}", err=True)
        return 2
    payload = dict(state)
    payload["memory_metrics"] = compute_memory_metrics(root, run_id)
    version = str(payload.get("version", "") or "").strip()
    if version:
        payload["source_of_truth"] = {
            "root": f"docs/beacon/{version}",
            "runtime_state_root": ".beacon",
            "formal_package_closure": build_material_audit(root, version=version, strict=False).get("status", "unknown"),
        }
    typer.echo(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0


def _resolve_run_id(action: str, target: Optional[str], run_id_opt: Optional[str]) -> str:
    resolved = str(run_id_opt or target or "").strip()
    if resolved:
        return resolved
    typer.echo(f"Missing run_id for resume {action}.", err=True)
    raise typer.Exit(code=2)


def resume_entry(  # noqa: PLR0913
    action_or_run_id: Optional[str] = typer.Argument(
        None,
        metavar="[RUN_ID|ACTION]",
        help="Run ID, or action: restore|continue",
    ),
    target_run_id: Optional[str] = typer.Argument(
        None,
        metavar="[RUN_ID]",
        help="Run ID when action is restore/continue",
    ),
    project_root: str = typer.Option("", "--project-root", help="Project root path"),
    run_id: Optional[str] = typer.Option(None, "--run-id", help="Explicit run id for resume continue/restore"),
    version: str = typer.Option("auto", "--version", "-v", help="Version filter"),
    feature: Optional[str] = typer.Option(None, "--feature", "-f", help="Feature filter"),
    auto: bool = typer.Option(False, "--auto", "-a", help="Continue until gate"),
    interactive: Optional[bool] = typer.Option(
        None,
        "--interactive/--no-interactive",
        help="Interactive mode (default: auto detect TTY)",
    ),
    hud: bool = typer.Option(True, "--hud/--no-hud", help="Render workflow HUD before execution"),
    confirm_execute: bool = typer.Option(
        False,
        "--confirm-execute",
        help="Non-interactive first confirmation for workflow execution (v1.1.0+).",
    ),
    confirm_execute_second: bool = typer.Option(
        False,
        "--confirm-execute-second",
        help="Non-interactive second confirmation for workflow execution (v1.1.0+).",
    ),
    confirm_timeout: int = typer.Option(60, "--confirm-timeout", min=1, help="Confirm timeout seconds"),
    on_timeout: str = typer.Option("pause", "--on-timeout", help="Timeout behavior: pause|continue|abort"),
):
    """Inspect run state or continue workflow using flat-compatible syntax.

    Supported contracts:
      - beacon resume <run_id> [--project-root ...]
      - beacon resume restore <run_id>|--run-id <run_id> [...]
      - beacon resume continue <run_id>|--run-id <run_id> [...]
    """
    token = str(action_or_run_id or "").strip()
    if not token:
        typer.echo("Missing run_id.", err=True)
        raise typer.Exit(code=2)

    lowered = token.lower()
    if lowered in {"continue", "cont"}:
        resolved = _resolve_run_id("continue", target_run_id, run_id)
        continue_workflow(
            project=project_root or None,
            version=version,
            feature=feature,
            run_id=resolved,
            auto=auto,
            interactive=interactive,
            hud=hud,
            confirm_execute=confirm_execute,
            confirm_execute_second=confirm_execute_second,
            confirm_timeout=confirm_timeout,
            on_timeout=on_timeout,
            implementation_command=None,
            verify_scope="all",
            verify_config=None,
            verify_ui_command=None,
            verify_api_curl_command=None,
            verify_unit_command=None,
            verify_smoke_command=None,
            verify_require_ui_actions=False,
            verify_qa_profile="web-full",
            verify_qa_types=None,
            verify_qa_matrix_path=None,
            verify_ui_runner="playwright",
            verify_compat_browsers=None,
            verify_compat_devices=None,
            verify_require_fresh_evidence=False,
        )
        return

    if lowered in {"restore", "show"}:
        resolved = _resolve_run_id("restore", target_run_id, run_id)
        raise typer.Exit(code=_resume_impl(run_id=resolved, project_root=project_root))

    if target_run_id:
        typer.echo(f"Unexpected extra argument: {target_run_id}", err=True)
        raise typer.Exit(code=2)

    resolved = str(run_id or token).strip()
    if not resolved:
        typer.echo("Missing run_id.", err=True)
        raise typer.Exit(code=2)
    raise typer.Exit(code=_resume_impl(run_id=resolved, project_root=project_root))


app = typer.Typer(name="resume", help="Resume/inspect run state", invoke_without_command=True, no_args_is_help=False)


@app.callback(invoke_without_command=True)
def _compat_resume_callback(
    action_or_run_id: Optional[str] = typer.Argument(None),
    target_run_id: Optional[str] = typer.Argument(None),
    project_root: str = typer.Option("", "--project-root", help="Project root path"),
    run_id: Optional[str] = typer.Option(None, "--run-id", help="Explicit run id for resume continue/restore"),
    version: str = typer.Option("auto", "--version", "-v", help="Version filter"),
    feature: Optional[str] = typer.Option(None, "--feature", "-f", help="Feature filter"),
    auto: bool = typer.Option(False, "--auto", "-a", help="Continue until gate"),
    interactive: Optional[bool] = typer.Option(
        None,
        "--interactive/--no-interactive",
        help="Interactive mode (default: auto detect TTY)",
    ),
    hud: bool = typer.Option(True, "--hud/--no-hud", help="Render workflow HUD before execution"),
    confirm_execute: bool = typer.Option(
        False,
        "--confirm-execute",
        help="Non-interactive first confirmation for workflow execution (v1.1.0+).",
    ),
    confirm_execute_second: bool = typer.Option(
        False,
        "--confirm-execute-second",
        help="Non-interactive second confirmation for workflow execution (v1.1.0+).",
    ),
    confirm_timeout: int = typer.Option(60, "--confirm-timeout", min=1, help="Confirm timeout seconds"),
    on_timeout: str = typer.Option("pause", "--on-timeout", help="Timeout behavior: pause|continue|abort"),
):
    """Compatibility callback when module app is invoked standalone."""
    resume_entry(
        action_or_run_id=action_or_run_id,
        target_run_id=target_run_id,
        project_root=project_root,
        run_id=run_id,
        version=version,
        feature=feature,
        auto=auto,
        interactive=interactive,
        hud=hud,
        confirm_execute=confirm_execute,
        confirm_execute_second=confirm_execute_second,
        confirm_timeout=confirm_timeout,
        on_timeout=on_timeout,
    )


if __name__ == "__main__":
    app()
