"""Planner review runtime CLI for beacon-loop delivery orchestrator."""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Optional

import typer

from beacon.utils.planner_review_runtime import build_planner_review_runtime_artifact
from beacon.utils.truth_map import resolve_truth_read_refs
from beacon.utils.versioning import resolve_target_version

app = typer.Typer(
    name="planner-review",
    help="Planner-only multi-reviewer runtime evidence for beacon-loop.",
    no_args_is_help=True,
)


@app.command("run")
def run_cmd(
    feature: str = typer.Argument(..., help="Feature slug"),
    project: Optional[str] = typer.Option(None, "--project", "-p", "--project-root", help="Project root"),
    version: str = typer.Option("auto", "--version", "-v", help="Docs version"),
    prompt: str = typer.Option("", "--prompt", help="Utterance or review prompt"),
    execution_mode: str = typer.Option("", "--execution-mode", help="parallel_subagent_review or single_process_multi_reviewer"),
    json_output: bool = typer.Option(False, "--json", help="Emit JSON payload"),
) -> None:
    """Build deterministic planner review runtime evidence without writing package truth."""
    project_root = Path(project).resolve() if project else Path.cwd()
    resolved_version = resolve_target_version(project_root, version)
    refs = resolve_truth_read_refs(project_root, version=resolved_version, feature=feature, consumer="review")
    truth_refs = [str(item) for item in (refs.get("truth_refs") or []) if str(item).strip()]
    source_refs = [str(item) for item in (refs.get("source_refs") or []) if str(item).strip()]
    evidence_refs = [str(item) for item in (refs.get("evidence_refs") or []) if str(item).strip()]
    parallel_requested = execution_mode == "parallel_subagent_review" or os.environ.get("BEACON_LOOP_REVIEW_PARALLEL") == "1"
    subagent_available = parallel_requested and os.environ.get("BEACON_LOOP_SUBAGENT_RUNTIME") == "1"
    payload = build_planner_review_runtime_artifact(
        project_root=project_root,
        feature=feature,
        version=resolved_version,
        prompt=prompt or feature,
        truth_refs=truth_refs,
        source_refs=source_refs,
        evidence_refs=evidence_refs,
        host_runtime=os.environ.get("BEACON_AGENT_RUNTIME", "codex"),
        subagent_runtime_available=subagent_available,
        write=False,
    )
    if json_output:
        typer.echo(json.dumps(payload, ensure_ascii=False, indent=2))
        return
    typer.echo(json.dumps({"review_id": payload.get("review_id"), "execution_mode": payload.get("execution_mode")}))
