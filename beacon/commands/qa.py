"""Beacon QA command - primary surface for v1.1.9 feature-aware verification."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path
from typing import Any, Optional

import typer

from beacon.utils.exhaustiveness import build_exhaustiveness_report, write_exhaustiveness_report
from beacon.utils.qa_feature import (
    build_feature_qa_plan,
    collect_verification_writeback,
    feature_qa_matrix_path,
    materialize_feature_qa_matrix,
    writeback_feature_matrix_evidence,
    write_feature_qa_status,
)
from beacon.utils.qa_runtime import (
    list_qa_sessions,
    load_current_qa_session,
    load_qa_session,
    load_qa_status,
    qa_current_session_path,
    qa_status_path,
    set_current_qa_session,
    write_qa_session,
    write_qa_status,
)
from beacon.utils.writeback import record_verification_writeback

app = typer.Typer(name="qa", help="QA primary surface (v1.1.9)")
session_app = typer.Typer(name="session", help="QA login/session state helpers")
app.add_typer(session_app, name="session")

KNOWN_SCOPES = {
    "all",
    "full",
    "ui",
    "api-curl",
    "unit",
    "smoke",
    "visual",
    "functional",
    "interface",
    "contract",
    "integration",
    "regression",
    "exception",
    "compatibility",
    "qa9",
}
OPTION_NAMES_WITH_VALUE = {
    "--project",
    "--project-root",
    "-p",
    "--version",
    "-v",
    "--qa-matrix-path",
    "--matrix-path",
    "--qa-types",
    "--qa-profile",
    "--layer-command",
    "--ui-command",
    "--api-curl-command",
    "--unit-command",
    "--smoke-command",
    "--visual-command",
    "--interface-command",
    "--contract-command",
    "--integration-command",
    "--functional-command",
    "--regression-command",
    "--exception-command",
    "--compatibility-command",
    "--origin-url",
    "--target-url",
    "--snapshot-file",
    "--snapshot-text",
    "--required-ui-action",
    "--ui-action-evidence",
    "--compat-browsers",
    "--compat-devices",
    "--rerun-flaky",
    "--max-flaky-rate",
    "--mode",
}
FLAG_NAMES = {
    "--strict-ui-assertion",
    "--require-fresh-evidence",
    "--require-junit",
    "--require-assertion-count",
    "--require-ui-actions",
    "--verbose",
    "-v",
    "--json",
}


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def _beacon_exec(args: list[str], *, cwd: Path | None = None) -> int:
    cmd = [sys.executable, "-m", "beacon.main", *args]
    result = subprocess.run(cmd, cwd=cwd or _repo_root())
    return int(result.returncode)


def _beacon_exec_silent(args: list[str], *, cwd: Path | None = None) -> int:
    cmd = [sys.executable, "-m", "beacon.main", *args]
    result = subprocess.run(cmd, cwd=cwd or _repo_root(), capture_output=True, text=True)
    return int(result.returncode)


def _extract_option(args: list[str], *names: str) -> str:
    index = 0
    while index < len(args):
        item = str(args[index])
        for name in names:
            if item == name and index + 1 < len(args):
                return str(args[index + 1])
            if item.startswith(f"{name}="):
                return item.split("=", 1)[1]
        index += 1
    return ""


def _strip_flag(args: list[str], flag: str) -> tuple[list[str], bool]:
    out: list[str] = []
    found = False
    for item in args:
        if item == flag:
            found = True
            continue
        out.append(item)
    return out, found


def _strip_option_with_value(args: list[str], option: str) -> list[str]:
    out: list[str] = []
    skip_next = False
    for item in args:
        if skip_next:
            skip_next = False
            continue
        if item == option:
            skip_next = True
            continue
        if str(item).startswith(f"{option}="):
            continue
        out.append(item)
    return out


def _first_positional(args: list[str]) -> str:
    skip_next = False
    for index, item in enumerate(args):
        if skip_next:
            skip_next = False
            continue
        if item in OPTION_NAMES_WITH_VALUE:
            skip_next = True
            continue
        if any(item.startswith(f"{name}=") for name in OPTION_NAMES_WITH_VALUE):
            continue
        if item in FLAG_NAMES or item.startswith("-"):
            continue
        return str(item)
    return ""


def _remove_first_positional(args: list[str]) -> list[str]:
    out: list[str] = []
    removed = False
    skip_next = False
    for item in args:
        if skip_next:
            out.append(item)
            skip_next = False
            continue
        if item in OPTION_NAMES_WITH_VALUE:
            out.append(item)
            skip_next = True
            continue
        if any(str(item).startswith(f"{name}=") for name in OPTION_NAMES_WITH_VALUE):
            out.append(item)
            continue
        if not removed and not str(item).startswith("-"):
            removed = True
            continue
        out.append(item)
    return out


def _looks_like_feature_request(args: list[str]) -> bool:
    positional = _first_positional(args)
    if not positional:
        return False
    return positional.strip().lower() not in KNOWN_SCOPES


def _collect_evidence_refs(payload: dict[str, Any], *, project_root: Path, feature_matrix_rel: str) -> list[str]:
    refs: list[str] = [feature_matrix_rel, str(qa_status_path(project_root).relative_to(project_root)), str(qa_current_session_path(project_root).relative_to(project_root))]
    execution = payload.get("execution") if isinstance(payload.get("execution"), dict) else {}
    layers = execution.get("layers") if isinstance(execution.get("layers"), list) else []
    for layer in layers:
        if not isinstance(layer, dict):
            continue
        layer_refs = layer.get("evidence_ref") if isinstance(layer.get("evidence_ref"), list) else []
        refs.extend(str(item) for item in layer_refs if str(item).strip())
    artifacts = execution.get("artifacts") if isinstance(execution.get("artifacts"), list) else []
    refs.extend(str(item) for item in artifacts if str(item).strip())
    refs.extend(
        str(item.get("evidence_ref") or "")
        for item in payload.get("per_item_results", [])
        if isinstance(item, dict) and item.get("evidence_ref")
    )
    ordered: list[str] = []
    seen: set[str] = set()
    for item in refs:
        if isinstance(item, list):
            for nested in item:
                text = str(nested).strip()
                if text and text not in seen:
                    seen.add(text)
                    ordered.append(text)
            continue
        text = str(item).strip()
        if text and text not in seen:
            seen.add(text)
            ordered.append(text)
    return ordered


def _run_feature_aware_qa(raw_args: list[str]) -> tuple[int, dict[str, Any]]:
    args, json_output = _strip_flag(raw_args, "--json")
    feature = _first_positional(args)
    project_value = _extract_option(args, "--project", "--project-root", "-p")
    version = _extract_option(args, "--version", "-v") or "auto"
    mode = _extract_option(args, "--mode") or "feature-aware"
    project_root = Path(project_value).resolve() if project_value else Path.cwd()
    args = _strip_option_with_value(args, "--mode")

    plan = build_feature_qa_plan(project_root, version=version, feature=feature, execution_mode=mode)
    if not bool(plan.get("implementation_done", False)):
        if json_output:
            typer.echo(json.dumps(plan, ensure_ascii=False, indent=2))
        else:
            typer.echo(f"Beacon QA blocked: implementation not recorded for {feature}", err=True)
        return 2, plan

    if str(plan.get("status") or "") == "up_to_date":
        payload = {
            **plan,
            "feature_matrix_path": str(feature_qa_matrix_path(project_root, feature=feature).relative_to(project_root)),
            "message": "feature QA already up to date; no rerun required",
        }
        write_feature_qa_status(project_root, feature=feature, payload=payload)
        if json_output:
            typer.echo(json.dumps(payload, ensure_ascii=False, indent=2))
        else:
            typer.echo(f"✓ Feature QA up to date: {feature}")
            typer.echo(f"  Reason: {payload['message']}")
        return 0, payload

    matrix_path = materialize_feature_qa_matrix(project_root, plan=plan)
    auto_args = [
        "auto-test",
        "create",
        "qa9",
        *_remove_first_positional(args),
        "--project",
        str(project_root),
        "--version",
        version,
        "--qa-matrix-path",
        str(matrix_path),
        "--qa-types",
        ",".join(plan.get("targeted_layers") or ["contract"]),
        "--require-fresh-evidence",
    ]
    command_exit = _beacon_exec_silent(auto_args, cwd=_repo_root()) if json_output else _beacon_exec(auto_args, cwd=_repo_root())
    qa_status = load_qa_status(project_root)
    verified_ids, failed_ids, per_item_results = collect_verification_writeback(plan=plan, qa_status=qa_status)
    feature_matrix_rel = str(matrix_path.relative_to(project_root))

    record_verification_writeback(
        project_root,
        version=version,
        feature=feature,
        run_id=str(qa_status.get("run_id") or plan.get("implementation_run_id") or "feature-qa"),
        verified_item_ids=verified_ids,
        failed_item_ids=failed_ids,
        evidence_ref=_collect_evidence_refs(qa_status, project_root=project_root, feature_matrix_rel=feature_matrix_rel),
    )

    blocking_updates = plan.get("blocking_artifact_updates") if isinstance(plan.get("blocking_artifact_updates"), list) else []
    qa_status = dict(qa_status)
    qa_status["feature"] = feature
    qa_status["feature_slug"] = str(plan.get("feature_slug") or "")
    qa_status["implementation_done"] = True
    qa_status["evidence_done"] = str(qa_status.get("status") or "").strip().lower() == "passed"
    qa_status["story_sequence"] = plan.get("story_sequence", [])
    qa_status["targeted_rerun"] = {
        "required": True,
        "reason_codes": plan.get("reason_codes", []),
        "targeted_layers": plan.get("targeted_layers", []),
        "targeted_ac_ids": plan.get("targeted_ac_ids", []),
        "targeted_tc_ids": plan.get("targeted_tc_ids", []),
        "targeted_scenario_ids": plan.get("targeted_scenario_ids", []),
        "targeted_scenario_families": plan.get("targeted_scenario_families", []),
    }
    qa_status["feature_matrix_path"] = feature_matrix_rel
    qa_status["blocking_artifact_updates"] = blocking_updates
    qa_status["per_item_results"] = per_item_results
    qa_status["execution_mode"] = str(plan.get("execution_mode") or mode)
    canonical_matrix = writeback_feature_matrix_evidence(
        project_root,
        plan=plan,
        per_item_results=per_item_results,
        run_id=str(qa_status.get("run_id") or ""),
    )
    if canonical_matrix is not None:
        qa_status["canonical_matrix_path"] = str(canonical_matrix.relative_to(project_root))
    exhaustiveness = build_exhaustiveness_report(
        project_root,
        feature=feature,
        run_id=str(qa_status.get("run_id") or plan.get("implementation_run_id") or "feature-qa"),
        plan=plan,
        qa_status=qa_status,
    )
    write_exhaustiveness_report(project_root, feature=feature, payload=exhaustiveness)
    qa_status["exhaustiveness"] = exhaustiveness
    if str(exhaustiveness.get("status") or "").strip().lower() != "passed":
        qa_status["status"] = "blocked"
        qa_status["evidence_done"] = False
    write_qa_status(project_root, qa_status)

    payload = {
        **plan,
        "run_id": str(qa_status.get("run_id") or ""),
        "status": str(qa_status.get("status") or "unknown"),
        "implementation_done": True,
        "evidence_done": bool(qa_status.get("evidence_done", False)),
        "feature_matrix_path": feature_matrix_rel,
        "blocking_artifact_updates": blocking_updates,
        "per_item_results": per_item_results,
        "verified_item_ids": verified_ids,
        "failed_item_ids": failed_ids,
        "targeted_scenario_ids": list(plan.get("targeted_scenario_ids") or []),
        "targeted_scenario_families": list(plan.get("targeted_scenario_families") or []),
        "story_scenario_map_path": str(plan.get("story_scenario_map_path") or ""),
        "exhaustiveness": exhaustiveness,
    }
    write_feature_qa_status(project_root, feature=feature, payload=payload)

    exit_code = command_exit
    if exit_code == 0 and str(qa_status.get("status") or "").strip().lower() != "passed":
        exit_code = 2

    if json_output:
        typer.echo(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        typer.echo(f"Feature QA status: {payload['status']}")
        typer.echo(f"  feature: {feature}")
        typer.echo(f"  matrix: {feature_matrix_rel}")
        typer.echo(f"  evidence_done: {payload['evidence_done']}")
        if blocking_updates:
            typer.echo(f"  blocking_artifact_updates: {len(blocking_updates)}")
    return exit_code, payload


@app.command(
    "run",
    context_settings={"allow_extra_args": True, "ignore_unknown_options": True},
)
def run(ctx: typer.Context):
    """Run QA in scope mode or feature-aware mode (`beacon qa run <feature>`)."""
    if _looks_like_feature_request(list(ctx.args)):
        code, _ = _run_feature_aware_qa(list(ctx.args))
        raise typer.Exit(code=code)
    code = _beacon_exec(["auto-test", "create", *ctx.args], cwd=_repo_root())
    raise typer.Exit(code=code)


@app.command("evolve")
def evolve(
    feature: str = typer.Argument(..., help="Feature name"),
    project: Optional[str] = typer.Option(None, "--project", "--project-root", "-p", help="Project root"),
    version: str = typer.Option("auto", "--version", "-v", help="Version"),
    mode: str = typer.Option("feature-aware", "--mode", help="QA execution mode: feature-aware/story-exhaustive"),
    write_matrix: bool = typer.Option(True, "--write-matrix/--no-write-matrix", help="Write targeted matrix for rerun"),
    json_output: bool = typer.Option(False, "--json", help="JSON output"),
):
    """Compute the delta-aware rerun plan for a feature without executing QA."""
    project_root = Path(project).resolve() if project else Path.cwd()
    plan = build_feature_qa_plan(project_root, version=version, feature=feature, execution_mode=mode)
    if write_matrix and plan.get("targeted_entries"):
        matrix_path = materialize_feature_qa_matrix(project_root, plan=plan)
        plan["feature_matrix_path"] = str(matrix_path.relative_to(project_root))
    write_feature_qa_status(project_root, feature=feature, payload=plan)
    if json_output:
        typer.echo(json.dumps(plan, ensure_ascii=False, indent=2))
        return
    typer.echo(f"Beacon QA evolve: {feature}")
    typer.echo(f"- status: {plan.get('status')}")
    typer.echo(f"- mode: {plan.get('execution_mode')}")
    typer.echo(f"- targeted_layers: {', '.join(plan.get('targeted_layers', [])) or '-'}")
    typer.echo(f"- targeted_tc_ids: {', '.join(plan.get('targeted_tc_ids', [])) or '-'}")
    typer.echo(f"- targeted_scenario_ids: {', '.join(plan.get('targeted_scenario_ids', [])) or '-'}")
    typer.echo(f"- reason_codes: {', '.join(plan.get('reason_codes', [])) or '-'}")


@app.command("status")
def status(
    project: Optional[str] = typer.Option(None, "--project", "-p", help="Project root"),
    json_output: bool = typer.Option(False, "--json", help="JSON output"),
):
    """Read canonical QA status, falling back to legacy auto-test status."""
    project_root = Path(project) if project else Path.cwd()
    payload = load_qa_status(project_root)
    if not payload:
        typer.echo("No QA status found. Run `beacon qa run ...` first.")
        raise typer.Exit(1)
    if json_output:
        typer.echo(json.dumps(payload, ensure_ascii=False, indent=2))
        return
    typer.echo("Beacon QA Status")
    typer.echo("=" * 40)
    typer.echo(f"Status: {payload.get('status', 'N/A')}")
    typer.echo(f"Version: {payload.get('version', 'N/A')}")
    typer.echo(f"Run ID: {payload.get('run_id', 'N/A')}")
    typer.echo(f"Scope: {payload.get('scope', 'N/A')}")
    feature = str(payload.get("feature") or "").strip()
    if feature:
        typer.echo(f"Feature: {feature}")
        typer.echo(f"Evidence done: {payload.get('evidence_done')}")
        typer.echo(f"Execution mode: {payload.get('execution_mode', 'feature-aware')}")
    layers = payload.get("selected_layers")
    if isinstance(layers, list):
        typer.echo(f"Layers: {', '.join(str(x) for x in layers)}")
    exhaustiveness = payload.get("exhaustiveness")
    if isinstance(exhaustiveness, dict):
        typer.echo(
            f"Exhaustiveness: score={exhaustiveness.get('score', 0)} threshold={exhaustiveness.get('threshold', 0)} status={exhaustiveness.get('status', 'N/A')}"
        )


@app.command(
    "import",
    context_settings={"allow_extra_args": True, "ignore_unknown_options": True},
)
def import_results(ctx: typer.Context):
    """Primary alias of `beacon auto-test import-qa-use ...`."""
    code = _beacon_exec(["auto-test", "import-qa-use", *ctx.args], cwd=_repo_root())
    raise typer.Exit(code=code)


@session_app.command("save")
def session_save(
    session_id: str = typer.Argument(..., help="Session id"),
    project: Optional[str] = typer.Option(None, "--project", "-p", help="Project root"),
    origin: str = typer.Option("", "--origin", help="Origin or base URL"),
    runner_type: str = typer.Option("agent-browser", "--runner-type", help="Runner type"),
    profile_ref: str = typer.Option("", "--profile-ref", help="Browser profile ref"),
    cookies_ref: str = typer.Option("", "--cookies-ref", help="Cookies artifact path"),
    storage_state_ref: str = typer.Option("", "--storage-state-ref", help="Storage state artifact path"),
    expires_at: str = typer.Option("", "--expires-at", help="Expiry timestamp"),
    sensitivity: str = typer.Option("internal", "--sensitivity", help="Sensitivity label"),
    scope: Optional[list[str]] = typer.Option(None, "--scope", help="Allowed scopes/origins"),
    json_output: bool = typer.Option(False, "--json", help="JSON output"),
):
    """Save a canonical QA session manifest."""
    project_root = Path(project) if project else Path.cwd()
    payload = {
        "origin": origin,
        "runner_type": runner_type,
        "profile_ref": profile_ref,
        "cookies_ref": cookies_ref,
        "storage_state_ref": storage_state_ref,
        "expires_at": expires_at,
        "sensitivity": sensitivity,
        "scopes": list(scope or []),
    }
    refs = write_qa_session(project_root, session_id, payload)
    current_ref = set_current_qa_session(project_root, session_id)
    result = {"session_id": session_id, **refs, **current_ref}
    if json_output:
        typer.echo(json.dumps(result, ensure_ascii=False, indent=2))
        return
    typer.echo(f"✓ QA session saved: {session_id}")
    typer.echo(f"  Manifest: {project_root / refs['manifest']}")


@session_app.command("list")
def session_list(
    project: Optional[str] = typer.Option(None, "--project", "-p", help="Project root"),
    json_output: bool = typer.Option(False, "--json", help="JSON output"),
):
    """List QA sessions."""
    project_root = Path(project) if project else Path.cwd()
    rows = list_qa_sessions(project_root)
    current = load_current_qa_session(project_root)
    current_id = str(current.get("session_id", "") or "")
    payload = {"current_session_id": current_id, "sessions": rows}
    if json_output:
        typer.echo(json.dumps(payload, ensure_ascii=False, indent=2))
        return
    typer.echo(f"QA Sessions ({len(rows)} found):")
    for row in rows:
        marker = "*" if str(row.get("session_id", "")) == current_id else "-"
        typer.echo(f"{marker} {row.get('session_id')} ({row.get('runner_type', 'unknown')} @ {row.get('origin', '-')})")


@session_app.command("use")
def session_use(
    session_id: str = typer.Argument(..., help="Session id"),
    project: Optional[str] = typer.Option(None, "--project", "-p", help="Project root"),
    json_output: bool = typer.Option(False, "--json", help="JSON output"),
):
    """Set the current QA session."""
    project_root = Path(project) if project else Path.cwd()
    payload = load_qa_session(project_root, session_id)
    if not payload:
        typer.echo(f"Session not found: {session_id}", err=True)
        raise typer.Exit(2)
    refs = set_current_qa_session(project_root, session_id)
    result = {"session_id": session_id, **refs}
    if json_output:
        typer.echo(json.dumps(result, ensure_ascii=False, indent=2))
        return
    typer.echo(f"✓ Current QA session: {session_id}")


@session_app.command("show")
def session_show(
    session_id: str = typer.Argument("", help="Session id (default current)"),
    project: Optional[str] = typer.Option(None, "--project", "-p", help="Project root"),
    json_output: bool = typer.Option(False, "--json", help="JSON output"),
):
    """Show current or named QA session."""
    project_root = Path(project) if project else Path.cwd()
    target = session_id.strip() or str(load_current_qa_session(project_root).get("session_id", "") or "")
    if not target:
        typer.echo("No current QA session selected", err=True)
        raise typer.Exit(2)
    payload = load_qa_session(project_root, target)
    if not payload:
        typer.echo(f"Session not found: {target}", err=True)
        raise typer.Exit(2)
    if json_output:
        typer.echo(json.dumps(payload, ensure_ascii=False, indent=2))
        return
    typer.echo(json.dumps(payload, ensure_ascii=False, indent=2))
