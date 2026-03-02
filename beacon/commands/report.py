"""Beacon report command."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import typer

from beacon.utils.runtime import load_run_state, newest_run_id, now_iso, write_json
from beacon.utils.workflow_memory import compute_memory_metrics

app = typer.Typer(
    name="report",
    help="Generate run reports",
    invoke_without_command=True,
    no_args_is_help=False,
)


def _human_summary(machine: dict[str, Any]) -> str:
    lines = [
        "# Beacon Human Summary",
        "",
        f"- Run ID: `{machine.get('run_id', 'latest')}`",
        f"- Workflow: `{machine.get('workflow', 'workflow')}`",
        f"- Mode: `{machine.get('mode', 'normal')}`",
        f"- Status: **{machine.get('status', 'unknown')}**",
        "",
        "## Artifacts",
    ]
    artifacts = machine.get("artifacts", {})
    if isinstance(artifacts, dict) and artifacts:
        for key, value in artifacts.items():
            lines.append(f"- {key}: `{value}`")
    else:
        lines.append("- (none)")
    memory_metrics = machine.get("memory_metrics")
    if isinstance(memory_metrics, dict):
        lines.extend(
            [
                "",
                "## Memory Loop",
                f"- closure_complete: `{memory_metrics.get('closure_complete')}`",
                f"- recall_injections: `{memory_metrics.get('recall_injections')}`",
                f"- writebacks: `{memory_metrics.get('writebacks')}`",
                f"- feedback_assimilations: `{memory_metrics.get('feedback_assimilations')}`",
            ]
        )
    return "\n".join(lines) + "\n"


def _build_machine_payload(project_root: Path, run_id: str) -> dict[str, Any]:
    resolved = run_id
    if not resolved or resolved == "latest":
        resolved = newest_run_id(project_root) or "latest"

    state = load_run_state(project_root, resolved) if resolved != "latest" else None
    if not state:
        return {
            "run_id": resolved,
            "workflow": "workflow",
            "mode": "normal",
            "status": "unknown",
            "reason": "no-run-state",
            "events": [],
            "llm_prompts": [],
            "token_usage": {"prompt_tokens": 0, "completion_tokens": 0},
            "tool_calls": [],
            "artifacts": {},
            "deviations": [],
            "confirmations": [],
            "memory_metrics": compute_memory_metrics(project_root, None if resolved == "latest" else resolved),
            "generated_at": now_iso(),
        }

    return {
        "run_id": resolved,
        "workflow": state.get("workflow", "workflow"),
        "mode": state.get("mode", "normal"),
        "status": state.get("status", "unknown"),
        "reason": state.get("reason", ""),
        "events": state.get("events", []),
        "llm_prompts": state.get("llm_prompts", []),
        "token_usage": state.get("token_usage", {"prompt_tokens": 0, "completion_tokens": 0}),
        "tool_calls": state.get("tool_calls", []),
        "artifacts": state.get("artifacts", {}),
        "deviations": state.get("deviations", []),
        "confirmations": state.get("confirmations", []),
        "memory_metrics": compute_memory_metrics(project_root, resolved),
        "generated_at": now_iso(),
    }


def _report_impl(project_root: str, run_id: str, human: bool, machine: bool) -> int:
    root = Path(project_root) if project_root else Path.cwd()
    payload = _build_machine_payload(root, run_id)

    exec_dir = root / "docs" / "beacon" / "v1.0.0" / "execution"
    exec_dir.mkdir(parents=True, exist_ok=True)
    summary_json = exec_dir / "summary.json"
    summary_md = exec_dir / "summary.md"
    write_json(summary_json, payload)
    summary_md.write_text(_human_summary(payload), encoding="utf-8")

    emit_human = human or not machine
    if emit_human:
        typer.echo(summary_md.read_text(encoding="utf-8"), nl=False)
    else:
        typer.echo(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0


@app.callback(invoke_without_command=True)
def report_callback(
    ctx: typer.Context,
    run_id: str = typer.Argument("latest", help="Run ID (default: latest)"),
    human: bool = typer.Option(False, "--human", help="Generate human-friendly report"),
    machine: bool = typer.Option(False, "--machine", help="Generate machine JSON report"),
    project_root: str = typer.Option("", "--project-root", help="Project root path"),
):
    """Generate report directly (PTK flat syntax compatibility)."""
    if ctx.invoked_subcommand is None:
        code = _report_impl(project_root=project_root, run_id=run_id, human=human, machine=machine)
        raise typer.Exit(code=code)


@app.command("generate")
def generate(
    run_id: str = typer.Argument("latest", help="Run ID"),
    human: bool = typer.Option(True, "--human/--machine", help="Report format"),
    project_root: str = typer.Option("", "--project-root", help="Project root path"),
):
    """Generate run report (nested compatibility)."""
    code = _report_impl(project_root=project_root, run_id=run_id, human=human, machine=not human)
    raise typer.Exit(code=code)


if __name__ == "__main__":
    app()
