"""Beacon implement command - execution adapter for implementation stage."""

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Any, Optional

import typer

from beacon.utils.artifact_paths import execution_file_candidates, execution_file_output, human_execution_file, qa_matrix_candidates
from beacon.utils.artifact_update_obligations import write_artifact_update_obligations
from beacon.utils.git_alignment import (
    build_implement_branch_guard_payload,
    switch_to_expected_branch,
)
from beacon.utils.governance import evaluate_takeover_baseline_gate
from beacon.utils.implementation_plan import (
    build_implementation_plan_gate_payload,
    compile_implementation_plan,
    implementation_plan_json_path,
    implementation_plan_markdown_path,
    implementation_plan_progress_path,
    implementation_plan_supported,
    load_implementation_plan_progress,
    mark_implementation_plan_failed,
    mark_implementation_plan_started,
)
from beacon.utils.implement_native import run_native_implementation
from beacon.utils.implement_adapters import (
    build_default_task_prompt,
    detect_adapter,
    discover_skill_adapters,
    format_template,
    load_beacon_config,
    resolve_adapter,
    resolve_default_runner,
)
from beacon.utils.learning_loop import write_requirement_rewrite_input
from beacon.utils.runtime import generate_run_id, now_iso, write_json
from beacon.utils.story_state import load_story_state
from beacon.utils.team_surface import write_implement_to_qa_handoff
from beacon.utils.v115_delivery import refresh_evidence_manifest
from beacon.utils.versioning import normalize_version, resolve_target_version
from beacon.utils.writeback import record_implementation_writeback

app = typer.Typer(name="implement", help="Run implementation via configured skill adapters")


def _slug(text: str) -> str:
    return "-".join(str(text or "").strip().lower().split())


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def _impl_root(project_root: Path, run_id: str) -> Path:
    return project_root / ".beacon" / "implement" / run_id


def _artifacts(project_root: Path, version: str, feature: str) -> dict[str, str]:
    slug = _slug(feature)
    base = project_root / "docs" / "beacon" / version
    return {
        "source_of_truth_root": f"docs/beacon/{version}",
        "user_story": str((base / "user-story" / f"{slug}.md").relative_to(project_root)),
        "prd": str((base / "prd" / f"{slug}.md").relative_to(project_root)),
        "test_case": str((base / "qa" / "test-cases" / f"{slug}.md").relative_to(project_root)),
        "ac_matrix": str(qa_matrix_candidates(project_root, version, slug, "ac-test-matrix")[0].relative_to(project_root)),
        "prototype_dir": str((base / "prototype" / slug).relative_to(project_root)),
        "execution_dir": str((base / "execution").relative_to(project_root)),
    }


def _summary_paths(project_root: Path, version: str, feature: str) -> dict[str, Path]:
    slug = _slug(feature)
    return {
        "json": execution_file_output(project_root, version, f"implementation-summary-{slug}.json"),
        "md": human_execution_file(project_root, version, f"implementation-summary-{slug}.md"),
    }


def _technical_archive_paths(project_root: Path, version: str, feature: str) -> dict[str, Path]:
    slug = _slug(feature)
    return {
        "md": human_execution_file(project_root, version, f"technical-implementation-{slug}.md"),
        "json": execution_file_output(project_root, version, f"technical-implementation-{slug}.json"),
    }


def _branch_preflight_path(run_id: str) -> Path:
    return Path(f".beacon/implement/{run_id}/branch-preflight.json")


def _git_commit(project_root: Path) -> str:
    try:
        result = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=project_root,
            capture_output=True,
            text=True,
            check=False,
        )
    except Exception:  # noqa: BLE001
        return ""
    return result.stdout.strip() if result.returncode == 0 else ""


def _write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def _semver_tuple(version: str | None) -> tuple[int, int, int]:
    text = str(normalize_version(version) or version or "").strip().lstrip("v")
    try:
        major, minor, patch = text.split(".")
        return (int(major), int(minor), int(patch))
    except Exception:  # noqa: BLE001
        return (0, 0, 0)


def _default_runner_for_version(project_root: Path, version: str) -> str:
    if _semver_tuple(version) >= (1, 3, 0):
        return "codex-subagents"
    configured = resolve_default_runner(project_root)
    if configured:
        return configured
    return "native-single"


def _normalize_string_list(value: Any) -> list[str]:
    if isinstance(value, list):
        return [str(item) for item in value if str(item).strip()]
    if isinstance(value, str) and str(value).strip():
        return [str(value).strip()]
    return []


def _run_auto_qa(project_root: Path, *, feature: str, version: str, extra_args: list[str]) -> tuple[int, dict[str, Any] | None]:
    cmd = [
        sys.executable,
        "-m",
        "beacon.main",
        "qa",
        "run",
        feature,
        "--project",
        str(project_root),
        "--version",
        version,
        "--json",
        *extra_args,
    ]
    result = subprocess.run(cmd, cwd=_repo_root(), capture_output=True, text=True)
    payload = None
    if result.stdout.strip():
        try:
            payload = json.loads(result.stdout)
        except Exception:  # noqa: BLE001
            payload = None
    return result.returncode, payload


def _run_beacon_json_command(project_root: Path, command: str) -> tuple[int, dict[str, Any] | None]:
    rendered = str(command or "").strip()
    if not rendered:
        return 2, None
    if "--json" not in rendered:
        rendered = f"{rendered} --json"
    result = subprocess.run(rendered, cwd=_repo_root(), shell=True, capture_output=True, text=True)
    payload = None
    if result.stdout.strip():
        try:
            payload = json.loads(result.stdout)
        except Exception:  # noqa: BLE001
            payload = None
    return result.returncode, payload


def _run_auto_qa_sequence(
    project_root: Path,
    *,
    feature: str,
    version: str,
    extra_args: list[str],
    follow_handoff: bool,
    max_rounds: int,
) -> tuple[int, dict[str, Any]]:
    history: list[dict[str, Any]] = []
    qa_exit, qa_payload = _run_auto_qa(project_root, feature=feature, version=version, extra_args=extra_args)
    history.append(
        {
            "step": "qa-run",
            "round": 1,
            "exit_code": qa_exit,
            "payload": qa_payload,
        }
    )
    final_exit = qa_exit
    final_payload = qa_payload
    previous_signature = ""
    rounds_completed = 1

    while follow_handoff and rounds_completed < max(1, int(max_rounds or 1)):
        feature_scorecard = final_payload.get("feature_scorecard") if isinstance(final_payload, dict) else {}
        if not isinstance(feature_scorecard, dict) or not feature_scorecard:
            break
        continue_decision = str(feature_scorecard.get("continue_decision") or "").strip()
        if continue_decision == "ready_for_release":
            break
        repair_handoff = feature_scorecard.get("repair_handoff") if isinstance(feature_scorecard.get("repair_handoff"), dict) else {}
        action = str(repair_handoff.get("action") or "").strip()
        command = str(repair_handoff.get("command") or "").strip()
        signature = json.dumps(
            {
                "continue_decision": continue_decision,
                "action": action,
                "command": command,
                "stop_reasons": feature_scorecard.get("stop_reasons", []),
                "missing_test_case_ids": (feature_scorecard.get("coverage_gap") or {}).get("missing_test_case_ids", []),
            },
            ensure_ascii=False,
            sort_keys=True,
        )
        if not action or not command or signature == previous_signature:
            break
        previous_signature = signature
        if action not in {"test-case-create", "verify-run", "qa-run"}:
            break
        handoff_exit, handoff_payload = _run_beacon_json_command(project_root, command)
        history.append(
            {
                "step": action,
                "round": rounds_completed,
                "exit_code": handoff_exit,
                "payload": handoff_payload,
                "command": command,
            }
        )
        if handoff_exit != 0:
            final_exit = handoff_exit
            break
        if action == "qa-run":
            final_exit = handoff_exit
            final_payload = handoff_payload
            break
        rounds_completed += 1
        qa_exit, qa_payload = _run_auto_qa(project_root, feature=feature, version=version, extra_args=extra_args)
        history.append(
            {
                "step": "qa-run",
                "round": rounds_completed,
                "exit_code": qa_exit,
                "payload": qa_payload,
            }
        )
        final_exit = qa_exit
        final_payload = qa_payload

    return final_exit, {
        "enabled": True,
        "triggered": True,
        "args": extra_args,
        "follow_handoff": bool(follow_handoff),
        "max_rounds": int(max_rounds or 1),
        "exit_code": final_exit,
        "payload": final_payload,
        "history": history,
    }


def _render_summary_markdown(payload: dict[str, Any]) -> str:
    lines = [
        "# Beacon Implementation Summary",
        "",
        f"- feature: `{payload.get('feature')}`",
        f"- version: `{payload.get('version')}`",
        f"- run_id: `{payload.get('run_id')}`",
        f"- status: `{payload.get('status')}`",
        f"- runner: `{payload.get('runner')}`",
        f"- adapter_type: `{payload.get('adapter_type')}`",
    ]
    skill = str(payload.get("skill", "") or "").strip()
    if skill:
        lines.append(f"- skill: `{skill}`")
    lines.extend(["", "## Changed Files"])
    changed = payload.get("changed_files") if isinstance(payload.get("changed_files"), list) else []
    if changed:
        for item in changed:
            lines.append(f"- `{item}`")
    else:
        lines.append("- none")
    verification = payload.get("verification") if isinstance(payload.get("verification"), list) else []
    lines.extend(["", "## Verification"])
    if verification:
        for item in verification:
            if isinstance(item, dict):
                lines.append(f"- `{item.get('status', 'unknown')}`: {item.get('command', '')}")
    else:
        lines.append("- none")
    updates = payload.get("artifact_updates") if isinstance(payload.get("artifact_updates"), dict) else {}
    lines.extend(["", "## Artifact Updates"])
    if updates:
        for key, value in updates.items():
            if isinstance(value, dict):
                lines.append(f"- `{key}`: required={value.get('required')} reason={value.get('reason', '')}")
            else:
                lines.append(f"- `{key}`: {value}")
    else:
        lines.append("- none")
    return "\n".join(lines) + "\n"


def _normalize_list(value: Any) -> list[Any]:
    return list(value) if isinstance(value, list) else []


def _story_item_ids(story: dict[str, Any], *, kinds: set[str]) -> list[str]:
    out: list[str] = []
    for item in story.get("items", []):
        if not isinstance(item, dict):
            continue
        if str(item.get("kind", "") or "") not in kinds:
            continue
        if not bool(item.get("required", True)):
            continue
        item_id = str(item.get("id", "") or "").strip().upper()
        if item_id:
            out.append(item_id)
    return out


def _modules_from_changed_files(changed_files: list[str]) -> list[str]:
    modules: set[str] = set()
    for item in changed_files:
        text = str(item).strip()
        if not text:
            continue
        parts = text.split("/")
        if len(parts) >= 2:
            modules.add("/".join(parts[:2]))
        elif parts:
            modules.add(parts[0])
    return sorted(modules)


def _technical_archive_payload(
    *,
    project_root: Path,
    version: str,
    feature: str,
    run_id: str,
    runner: str,
    skill: str,
    request_path: str,
    result_path: str,
    stdout_path: str,
    stderr_path: str,
    result_payload: dict[str, Any],
) -> dict[str, Any]:
    slug = _slug(feature)
    changed_files = [str(x) for x in _normalize_list(result_payload.get("changed_files")) if str(x).strip()]
    additions = [str(x) for x in _normalize_list(result_payload.get("additions")) if str(x).strip()]
    modifications = [str(x) for x in _normalize_list(result_payload.get("modifications")) if str(x).strip()]
    deletions = [str(x) for x in _normalize_list(result_payload.get("deletions")) if str(x).strip()]
    refactors = [str(x) for x in _normalize_list(result_payload.get("refactors")) if str(x).strip()]
    services = _normalize_list(result_payload.get("services"))
    payload = {
        "schema_version": "1.0",
        "feature": feature,
        "feature_slug": slug,
        "version": version,
        "revision_id": "",
        "run_id": run_id,
        "implemented_at": now_iso(),
        "runner": runner,
        "skill": skill,
        "profile_id": str(result_payload.get("profile_id", "") or ""),
        "git_commit": _git_commit(project_root),
        "services": services,
        "implementation_scope_summary": str(result_payload.get("summary", "") or ""),
        "business_goal_summary": str(result_payload.get("business_goal_summary", "") or str(result_payload.get("summary", "") or "")),
        "acceptance_scope": _normalize_list(result_payload.get("acceptance_scope")),
        "changed_files": changed_files,
        "modules_touched": _modules_from_changed_files(changed_files),
        "additions": additions,
        "modifications": modifications,
        "deletions": deletions,
        "refactors": refactors,
        "data_operations": _normalize_list(result_payload.get("data_operations")),
        "db_changes": result_payload.get("db_changes") if isinstance(result_payload.get("db_changes"), dict) else {"none": True, "new_tables": [], "altered_tables": [], "indexes": [], "migrations": []},
        "cache_changes": _normalize_list(result_payload.get("cache_changes")),
        "event_contract_changes": _normalize_list(result_payload.get("event_contract_changes")),
        "api_changes": result_payload.get("api_changes") if isinstance(result_payload.get("api_changes"), dict) else {"none": True, "new_endpoints": [], "changed_endpoints": [], "removed_endpoints": []},
        "external_integrations": _normalize_list(result_payload.get("external_integrations")),
        "queue_or_job_changes": _normalize_list(result_payload.get("queue_or_job_changes")),
        "cron_changes": _normalize_list(result_payload.get("cron_changes")),
        "config_changes": _normalize_list(result_payload.get("config_changes")),
        "env_changes": _normalize_list(result_payload.get("env_changes")),
        "feature_flags": _normalize_list(result_payload.get("feature_flags")),
        "deployment_notes": _normalize_list(result_payload.get("deployment_notes")),
        "verification": _normalize_list(result_payload.get("verification")),
        "known_risks": _normalize_list(result_payload.get("known_risks")),
        "rollback_notes": _normalize_list(result_payload.get("rollback_notes")),
        "compatibility_notes": _normalize_list(result_payload.get("compatibility_notes")),
        "artifact_updates": result_payload.get("artifact_updates") if isinstance(result_payload.get("artifact_updates"), dict) else {},
        "traceability": {
            "request_path": request_path,
            "result_path": result_path,
            "stdout_path": stdout_path,
            "stderr_path": stderr_path,
        },
    }
    return payload


def _render_technical_archive_markdown(payload: dict[str, Any]) -> str:
    def _render_section(title: str, items: list[Any]) -> list[str]:
        lines = ["", f"## {title}"]
        if not items:
            lines.append("- none")
            return lines
        for item in items:
            lines.append(f"- {item}")
        return lines

    lines = [
        "# Beacon Technical Implementation Archive",
        "",
        f"- feature: `{payload.get('feature')}`",
        f"- feature_slug: `{payload.get('feature_slug')}`",
        f"- version: `{payload.get('version')}`",
        f"- run_id: `{payload.get('run_id')}`",
        f"- runner: `{payload.get('runner')}`",
        f"- profile_id: `{payload.get('profile_id')}`",
        f"- git_commit: `{payload.get('git_commit')}`",
        "",
        "## Traceability",
        f"- request_path: `{payload.get('traceability', {}).get('request_path', '')}`",
        f"- result_path: `{payload.get('traceability', {}).get('result_path', '')}`",
        f"- stdout_path: `{payload.get('traceability', {}).get('stdout_path', '')}`",
        f"- stderr_path: `{payload.get('traceability', {}).get('stderr_path', '')}`",
    ]
    lines.extend(_render_section("Services", [str(x) for x in payload.get("services", [])]))
    lines.extend(_render_section("Changed Files", [f"`{x}`" for x in payload.get("changed_files", [])]))
    lines.extend(_render_section("Modules Touched", [f"`{x}`" for x in payload.get("modules_touched", [])]))
    lines.extend(_render_section("Additions", payload.get("additions", [])))
    lines.extend(_render_section("Modifications", payload.get("modifications", [])))
    lines.extend(_render_section("Deletions", payload.get("deletions", [])))
    lines.extend(_render_section("Refactors", payload.get("refactors", [])))
    lines.extend(_render_section("Data Operations", payload.get("data_operations", [])))
    lines.extend(_render_section("Config Changes", payload.get("config_changes", [])))
    lines.extend(_render_section("Env Changes", payload.get("env_changes", [])))
    lines.extend(_render_section("Feature Flags", payload.get("feature_flags", [])))
    lines.extend(_render_section("Queue / Job Changes", payload.get("queue_or_job_changes", [])))
    lines.extend(_render_section("Known Risks", payload.get("known_risks", [])))
    lines.extend(_render_section("Rollback Notes", payload.get("rollback_notes", [])))
    lines.extend(_render_section("Verification", [str(item) for item in payload.get("verification", [])]))
    lines.extend(["", "## DB Changes", json.dumps(payload.get("db_changes", {}), ensure_ascii=False, indent=2)])
    lines.extend(["", "## API Changes", json.dumps(payload.get("api_changes", {}), ensure_ascii=False, indent=2)])
    return "\n".join(lines) + "\n"


def _validate_result(payload: dict[str, Any]) -> list[str]:
    problems: list[str] = []
    if not isinstance(payload, dict):
        return ["result payload is not an object"]
    for key in ("status", "summary"):
        if not str(payload.get(key, "")).strip():
            problems.append(f"{key} missing")
    changed = payload.get("changed_files")
    if changed is not None and not isinstance(changed, list):
        problems.append("changed_files must be a list")
    verification = payload.get("verification")
    if verification is not None and not isinstance(verification, list):
        problems.append("verification must be a list")
    updates = payload.get("artifact_updates")
    if updates is not None and not isinstance(updates, dict):
        problems.append("artifact_updates must be an object")
    for key in ("implemented_task_ids", "verified_task_ids", "blocked_task_ids", "failed_task_ids"):
        value = payload.get(key)
        if value is not None and not isinstance(value, list):
            problems.append(f"{key} must be a list")
    return problems


def _run_review_command(project_root: Path, version: str, feature: str, mode: str) -> tuple[int, dict[str, Any] | None]:
    cmd = [
        sys.executable,
        "-m",
        "beacon.main",
        "review",
        mode,
        feature,
        "--project",
        str(project_root),
        "--version",
        version,
        "--json",
    ]
    result = subprocess.run(cmd, cwd=_repo_root(), capture_output=True, text=True)
    payload = None
    if result.stdout.strip():
        try:
            payload = json.loads(result.stdout)
        except Exception:  # noqa: BLE001
            payload = None
    return result.returncode, payload


def _run_branch_preflight(
    *,
    project_root: Path,
    version: str,
    run_id: str,
    feature: str,
    auto_switch_branch: bool,
    require_clean_worktree_for_switch: bool,
) -> dict[str, Any]:
    feature_slug = _slug(feature)
    branch_preflight = build_implement_branch_guard_payload(
        project_root,
        version,
        require_clean_worktree_for_switch=require_clean_worktree_for_switch,
    )
    branch_preflight.update(
        {
            "run_id": run_id,
            "feature": feature,
            "feature_slug": feature_slug,
            "generated_at": now_iso(),
        }
    )
    if branch_preflight.get("blocked") and auto_switch_branch:
        dirty_worktree = bool(branch_preflight.get("dirty_worktree"))
        if not (dirty_worktree and require_clean_worktree_for_switch):
            switch_payload = switch_to_expected_branch(
                project_root,
                str(branch_preflight.get("expected_branch", "") or ""),
                create_if_missing=True,
            )
            branch_preflight["switch_attempt"] = switch_payload
            refreshed = build_implement_branch_guard_payload(
                project_root,
                version,
                require_clean_worktree_for_switch=require_clean_worktree_for_switch,
            )
            refreshed.update(
                {
                    "run_id": run_id,
                    "feature": feature,
                    "feature_slug": feature_slug,
                    "generated_at": now_iso(),
                    "switch_attempt": switch_payload,
                    "auto_switch_branch": True,
                }
            )
            if switch_payload.get("status") == "failed" and refreshed.get("blocked"):
                refreshed["reason_codes"] = list(
                    dict.fromkeys([*list(refreshed.get("reason_codes", [])), "implement_branch_switch_failed"])
                )
            branch_preflight = refreshed
    return branch_preflight


def run_implement_stage(  # noqa: PLR0913
    *,
    feature: str,
    project_root: Path,
    version: str,
    run_id_override: str | None = None,
    runner: str | None = None,
    skill: str | None = None,
    task_template: str | None = None,
    dry_run: bool = False,
    timeout_sec: int | None = None,
    auto_review_spec: bool | None = None,
    auto_review_quality: bool | None = None,
    auto_qa: bool | None = None,
    auto_qa_args: list[str] | None = None,
    auto_qa_follow_handoff: bool | None = None,
    auto_qa_max_rounds: int | None = None,
    auto_switch_branch: bool | None = None,
) -> tuple[int, dict[str, Any]]:
    resolved_version = resolve_target_version(project_root, version)
    config = load_beacon_config(project_root)
    implementation_cfg = config.get("implementation") if isinstance(config.get("implementation"), dict) else {}
    branch_guard_cfg = implementation_cfg.get("branch_guard") if isinstance(implementation_cfg.get("branch_guard"), dict) else {}
    auto_review_spec = bool(implementation_cfg.get("auto_review_spec", True)) if auto_review_spec is None else auto_review_spec
    auto_review_quality = bool(implementation_cfg.get("auto_review_quality", False)) if auto_review_quality is None else auto_review_quality
    auto_qa = bool(implementation_cfg.get("auto_qa", False)) if auto_qa is None else auto_qa
    auto_qa_follow_handoff = (
        bool(implementation_cfg.get("auto_qa_follow_handoff", False))
        if auto_qa_follow_handoff is None
        else auto_qa_follow_handoff
    )
    auto_qa_max_rounds = int(implementation_cfg.get("auto_qa_max_rounds", 2) or 2) if auto_qa_max_rounds is None else int(auto_qa_max_rounds or 1)
    resolved_auto_qa_args = (
        _normalize_string_list(implementation_cfg.get("auto_qa_args"))
        if auto_qa_args is None
        else [str(item) for item in auto_qa_args if str(item).strip()]
    )
    auto_switch_branch = (
        bool(branch_guard_cfg.get("auto_switch", False))
        if auto_switch_branch is None
        else auto_switch_branch
    )
    require_clean_worktree_for_switch = bool(branch_guard_cfg.get("require_clean_worktree_for_switch", True))

    run_id = str(run_id_override or "").strip() or generate_run_id(project_root)
    feature_slug = _slug(feature)
    impl_dir = _impl_root(project_root, run_id)
    impl_dir.mkdir(parents=True, exist_ok=True)
    state_path = impl_dir / "state.json"
    takeover_gate = evaluate_takeover_baseline_gate(project_root, version=resolved_version)
    if str(takeover_gate.get("status", "") or "") == "blocked":
        payload = {
            "schema_version": "1.0",
            "run_id": run_id,
            "feature": feature,
            "feature_slug": feature_slug,
            "version": resolved_version,
            "status": "blocked",
            "reason_code": "takeover_baseline_required",
            "takeover_gate": takeover_gate,
            "generated_at": now_iso(),
        }
        write_json(state_path, payload)
        return 2, payload
    branch_preflight_path = _branch_preflight_path(run_id)
    branch_preflight = _run_branch_preflight(
        project_root=project_root,
        version=resolved_version,
        run_id=run_id,
        feature=feature,
        auto_switch_branch=bool(auto_switch_branch),
        require_clean_worktree_for_switch=require_clean_worktree_for_switch,
    )
    write_json(project_root / branch_preflight_path, branch_preflight)
    if branch_preflight.get("blocked"):
        payload = {
            "schema_version": "1.0",
            "run_id": run_id,
            "feature": feature,
            "feature_slug": feature_slug,
            "version": resolved_version,
            "status": "blocked",
            "reason_code": "implement_branch_guard_blocked",
            "branch_preflight_path": str(branch_preflight_path),
            "branch_preflight": branch_preflight,
            "expected_branch": branch_preflight.get("expected_branch", ""),
            "current_branch": branch_preflight.get("current_branch", ""),
            "recommended_command": branch_preflight.get("recommended_command", ""),
            "generated_at": now_iso(),
        }
        write_json(state_path, payload)
        return 2, payload

    plan_preflight_path = Path(f".beacon/implement/{run_id}/plan-preflight.json")
    implementation_plan_gate: dict[str, Any] = {}
    if implementation_plan_supported(resolved_version):
        implementation_plan_gate = build_implementation_plan_gate_payload(
            project_root,
            version=resolved_version,
            feature=feature,
            run_id=run_id,
        )
        write_json(project_root / plan_preflight_path, implementation_plan_gate)
        if implementation_plan_gate.get("blocked"):
            payload = {
                "schema_version": "1.0",
                "run_id": run_id,
                "feature": feature,
                "feature_slug": feature_slug,
                "version": resolved_version,
                "status": "blocked",
                "reason_code": str(implementation_plan_gate.get("reason_code", "implementation_plan_missing") or "implementation_plan_missing"),
                "plan_preflight_path": str(plan_preflight_path),
                "plan_preflight": implementation_plan_gate,
                "branch_preflight_path": str(branch_preflight_path),
                "branch_preflight": branch_preflight,
                "recommended_command": str(implementation_plan_gate.get("recommended_command", "") or ""),
                "generated_at": now_iso(),
            }
            write_json(state_path, payload)
            return 2, payload

    requested_runner = None if str(runner or "").strip().lower() == "auto" else runner
    if requested_runner is None:
        requested_runner = _default_runner_for_version(project_root, resolved_version)
    adapter_id, adapter = resolve_adapter(project_root, requested_runner)
    if not adapter_id or not adapter:
        payload = {
            "schema_version": "1.0",
            "status": "blocked",
            "reason_code": "runner_not_configured",
            "feature": feature,
            "version": resolved_version,
            "run_id": run_id,
            "feature_slug": feature_slug,
            "branch_preflight_path": str(branch_preflight_path),
            "branch_preflight": branch_preflight,
        }
        write_json(state_path, payload)
        return 2, payload

    artifacts = _artifacts(project_root, resolved_version, feature)
    request_path = Path(f".beacon/implement/{run_id}/request.json")
    request_md_path = Path(
        format_template(
            str(adapter.get("request_file") or f".beacon/implement/{run_id}/request.md"),
            {"run_id": run_id},
        )
    ) if str(adapter.get("adapter_type", "")).strip() in {"handoff", "claude-skill"} else None
    result_path = Path(
        format_template(
            str(adapter.get("result_file") or f".beacon/implement/{run_id}/result.json"),
            {"run_id": run_id},
        )
    )
    stdout_path = Path(
        format_template(str(adapter.get("stdout_file") or f".beacon/implement/{run_id}/stdout.log"), {"run_id": run_id})
    )
    stderr_path = Path(
        format_template(str(adapter.get("stderr_file") or f".beacon/implement/{run_id}/stderr.log"), {"run_id": run_id})
    )
    command_path = Path(
        format_template(str(adapter.get("command_file") or f".beacon/implement/{run_id}/command.txt"), {"run_id": run_id})
    )

    context = {
        "project_root": str(project_root),
        "workspace_root": str(project_root.parent),
        "feature": feature,
        "feature_slug": feature_slug,
        "version": resolved_version,
        "run_id": run_id,
        "request_file": str(request_path),
        "result_file": str(result_path),
        "source_of_truth_root": artifacts["source_of_truth_root"],
    }
    implementation_plan_file = (
        str(implementation_plan_json_path(project_root, resolved_version, feature).relative_to(project_root))
        if implementation_plan_supported(resolved_version)
        else ""
    )
    rendered_skill = str(skill or adapter.get("skill_prefix", "") or "").strip()
    default_prompt = build_default_task_prompt(
        feature=feature,
        version=resolved_version,
        source_of_truth_root=artifacts["source_of_truth_root"],
        feature_slug=feature_slug,
        result_file=str(result_path),
        implementation_plan_file=implementation_plan_file,
    )
    rendered_task_template = str(task_template or adapter.get("task_template") or "").strip()
    task_prompt = format_template(rendered_task_template, {**context, "task_prompt": default_prompt}) if rendered_task_template else default_prompt
    if rendered_skill:
        task_prompt = f"{rendered_skill}\n{task_prompt}"
    context["task_prompt"] = task_prompt

    request_payload = {
        "schema_version": "1.0",
        "run_id": run_id,
        "feature": feature,
        "feature_slug": feature_slug,
        "version": resolved_version,
        "source_of_truth_root": artifacts["source_of_truth_root"],
        "artifacts": artifacts,
        "runner": {
            "id": adapter_id,
            "adapter_type": str(adapter.get("adapter_type", "")),
            "runtime_family": str(adapter.get("runtime_family", "")),
            "skill": rendered_skill,
        },
        "branch_preflight_path": str(branch_preflight_path),
        "branch_preflight": branch_preflight,
        "task_prompt": task_prompt,
        "result_file": str(result_path),
        "implementation_plan": implementation_plan_file,
        "generated_at": now_iso(),
    }
    write_json(project_root / request_path, request_payload)

    state_path = impl_dir / "state.json"
    base_state = {
        "schema_version": "1.0",
        "run_id": run_id,
        "feature": feature,
        "feature_slug": feature_slug,
        "version": resolved_version,
        "runner": adapter_id,
        "adapter_type": str(adapter.get("adapter_type", "")),
        "request_path": str(request_path),
        "result_path": str(result_path),
        "branch_preflight_path": str(branch_preflight_path),
        "plan_preflight_path": str(plan_preflight_path),
        "generated_at": now_iso(),
        "status": "planned",
    }

    adapter_type = str(adapter.get("adapter_type", "")).strip()
    if adapter_type == "native":
        mark_implementation_plan_started(
            project_root,
            version=resolved_version,
            feature=feature,
            run_id=run_id,
        )
        native_mode = str(adapter.get("mode", "single") or "single")
        result_payload = run_native_implementation(
            project_root,
            version=resolved_version,
            feature=feature,
            run_id=run_id,
            mode=native_mode,
        )
        if str(result_payload.get("status", "")).strip().lower() != "completed":
            mark_implementation_plan_failed(
                project_root,
                version=resolved_version,
                feature=feature,
                run_id=run_id,
                reason_code=str(result_payload.get("reason_code", "native_runner_failed") or "native_runner_failed"),
            )
            payload = {
                **base_state,
                "status": "failed",
                "reason_code": str(result_payload.get("reason_code", "native_runner_failed") or "native_runner_failed"),
                "result": result_payload,
            }
            write_json(state_path, payload)
            return 2, payload
        summary_paths = _summary_paths(project_root, resolved_version, feature)
        archive_paths = _technical_archive_paths(project_root, resolved_version, feature)
        story_state = load_story_state(project_root, version=resolved_version, feature=feature, create_if_missing=True) or {}
        marker = project_root / ".beacon" / "state" / f"implementation-{feature_slug}.json"
        write_json(marker, {
            "schema_version": "1.0",
            "run_id": run_id,
            "feature": feature,
            "feature_slug": feature_slug,
            "version": resolved_version,
            "runner": adapter_id,
            "skill": rendered_skill,
            "status": "completed",
            "generated_at": now_iso(),
        })
        summary_payload = {
            **base_state,
            "run_id": run_id,
            "feature": feature,
            "feature_slug": feature_slug,
            "version": resolved_version,
            "runner": adapter_id,
            "adapter_type": adapter_type,
            "skill": rendered_skill,
            "status": "completed",
            "summary": str(result_payload.get("summary", "")),
            "changed_files": result_payload.get("changed_files", []),
            "verification": result_payload.get("verification", []),
            "implemented_task_ids": result_payload.get("implemented_task_ids", []),
            "verified_task_ids": result_payload.get("verified_task_ids", []),
            "blocked_task_ids": result_payload.get("blocked_task_ids", []),
            "failed_task_ids": result_payload.get("failed_task_ids", []),
            "artifact_updates": result_payload.get("artifact_updates", {}),
            "branch_preflight": branch_preflight,
            "plan_preflight_path": str(plan_preflight_path),
            "plan_preflight": implementation_plan_gate,
            "implementation_marker": str(marker.relative_to(project_root)),
            "technical_archive": {
                "json": str(archive_paths["json"].relative_to(project_root)),
                "md": str(archive_paths["md"].relative_to(project_root)),
            },
            "implementation_plan": implementation_plan_file,
            "implementation_plan_progress": load_implementation_plan_progress(project_root, version=resolved_version, feature=feature),
            "generated_at": now_iso(),
        }
        for key, value in result_payload.items():
            if key in summary_payload:
                continue
            summary_payload[key] = value
        technical_payload = _technical_archive_payload(
            project_root=project_root,
            version=resolved_version,
            feature=feature,
            run_id=run_id,
            runner=adapter_id,
            skill=rendered_skill,
            request_path=str(request_path),
            result_path=str(result_path),
            stdout_path="",
            stderr_path="",
            result_payload=result_payload,
        )
        current_revision_id = str(story_state.get("current_revision_id", "") or "")
        technical_payload["revision_id"] = current_revision_id
        write_json(archive_paths["json"], technical_payload)
        _write_text(archive_paths["md"], _render_technical_archive_markdown(technical_payload))
        refresh_evidence_manifest(
            project_root,
            refs=[
                str(archive_paths["json"].relative_to(project_root)),
                str(archive_paths["md"].relative_to(project_root)),
            ],
            version=resolved_version,
        )
        learning_payload = write_requirement_rewrite_input(
            project_root,
            version=resolved_version,
            feature=feature,
            archive_payload=technical_payload,
            archive_path=str(archive_paths["json"].relative_to(project_root)),
        )
        obligations = write_artifact_update_obligations(
            project_root,
            version=resolved_version,
            feature=feature,
            run_id=run_id,
            updates=result_payload.get("artifact_updates") if isinstance(result_payload.get("artifact_updates"), dict) else {},
            technical_archive_path=str(archive_paths["json"].relative_to(project_root)),
        )
        summary_payload["artifact_writeback_obligations"] = str(
            (
                project_root
                / ".beacon"
                / "state"
                / "artifact-update-obligations"
                / f"{feature_slug}.json"
            ).relative_to(project_root)
        )
        summary_payload["artifact_writeback_open_count"] = int(obligations.get("open_count", 0) or 0)
        summary_payload["requirement_rewrite_input"] = str(learning_payload.get("path", "") or "")
        handoff_path = write_implement_to_qa_handoff(
            project_root,
            version=resolved_version,
            feature=feature,
            run_id=run_id,
            summary_ref=str(summary_paths["json"].relative_to(project_root)),
            technical_archive_ref=str(archive_paths["json"].relative_to(project_root)),
            evidence_refs=[str(summary_paths["json"].relative_to(project_root)), str(archive_paths["json"].relative_to(project_root))],
            changed_files=result_payload.get("changed_files", []),
            implementation_plan_ref=implementation_plan_file,
        )
        summary_payload["implement_to_qa_handoff"] = str(handoff_path.relative_to(project_root))
        summary_payload["auto_qa"] = {
            "enabled": bool(auto_qa),
            "triggered": False,
            "args": resolved_auto_qa_args,
            "follow_handoff": bool(auto_qa_follow_handoff),
            "max_rounds": int(auto_qa_max_rounds or 1),
        }
        auto_qa_exit = 0
        if auto_qa:
            auto_qa_exit, auto_qa_payload = _run_auto_qa_sequence(
                project_root,
                feature=feature,
                version=resolved_version,
                extra_args=resolved_auto_qa_args,
                follow_handoff=bool(auto_qa_follow_handoff),
                max_rounds=int(auto_qa_max_rounds or 1),
            )
            summary_payload["auto_qa"] = auto_qa_payload
        write_json(summary_paths["json"], summary_payload)
        _write_text(summary_paths["md"], _render_summary_markdown(summary_payload))
        refresh_evidence_manifest(
            project_root,
            refs=[
                str(summary_paths["json"].relative_to(project_root)),
                str(summary_paths["md"].relative_to(project_root)),
            ],
            version=resolved_version,
        )
        write_json(state_path, summary_payload)
        return auto_qa_exit, summary_payload
    if adapter_type in {"handoff", "claude-skill"}:
        request_md = project_root / (request_md_path or Path(f".beacon/implement/{run_id}/request.md"))
        _write_text(request_md, task_prompt + "\n")
        payload = {
            **base_state,
            "status": "handoff_required",
            "request_path": str(request_path),
            "request_markdown": str(request_md.relative_to(project_root)),
            "recommended_flows": adapter.get("recommended_flows", []),
            "plan_preflight_path": str(plan_preflight_path),
            "plan_preflight": implementation_plan_gate,
            "implementation_plan": implementation_plan_file,
        }
        write_json(state_path, payload)
        return 0, payload

    rendered_args = [format_template(str(arg), context) for arg in adapter.get("args", [])]
    command = [str(adapter.get("command", "")).strip(), *rendered_args]
    _write_text(project_root / command_path, " ".join(command) + "\n")

    if dry_run:
        payload = {
            **base_state,
            "status": "dry_run",
            "command": command,
            "command_path": str(command_path),
            "task_prompt": task_prompt,
            "plan_preflight_path": str(plan_preflight_path),
            "plan_preflight": implementation_plan_gate,
            "implementation_plan": implementation_plan_file,
        }
        write_json(state_path, payload)
        return 0, payload

    env = {}
    for key in adapter.get("env_passthrough", []) if isinstance(adapter.get("env_passthrough"), list) else []:
        if key in os.environ:
            env[key] = os.environ[key]
    if isinstance(adapter.get("env_overrides"), dict):
        env.update({str(k): str(v) for k, v in adapter.get("env_overrides", {}).items()})

    timeout = int(timeout_sec or adapter.get("timeout_sec") or 3600)
    mark_implementation_plan_started(
        project_root,
        version=resolved_version,
        feature=feature,
        run_id=run_id,
    )
    try:
        result = subprocess.run(
            command,
            cwd=project_root,
            capture_output=True,
            text=True,
            timeout=timeout,
            env={**os.environ, **env},
        )
    except subprocess.TimeoutExpired:
        mark_implementation_plan_failed(
            project_root,
            version=resolved_version,
            feature=feature,
            run_id=run_id,
            reason_code="runner_execution_timeout",
        )
        payload = {
            **base_state,
            "status": "failed",
            "reason_code": "runner_execution_timeout",
            "command": command,
            "timeout_sec": timeout,
        }
        write_json(state_path, payload)
        return 2, payload
    except FileNotFoundError:
        mark_implementation_plan_failed(
            project_root,
            version=resolved_version,
            feature=feature,
            run_id=run_id,
            reason_code="runner_command_not_found",
        )
        payload = {
            **base_state,
            "status": "failed",
            "reason_code": "runner_command_not_found",
            "command": command,
        }
        write_json(state_path, payload)
        return 2, payload
    _write_text(project_root / stdout_path, result.stdout or "")
    _write_text(project_root / stderr_path, result.stderr or "")

    if result.returncode != 0:
        mark_implementation_plan_failed(
            project_root,
            version=resolved_version,
            feature=feature,
            run_id=run_id,
            reason_code="runner_execution_failed",
        )
        payload = {
            **base_state,
            "status": "failed",
            "reason_code": "runner_execution_failed",
            "command": command,
            "stdout_path": str(stdout_path),
            "stderr_path": str(stderr_path),
            "exit_code": result.returncode,
        }
        write_json(state_path, payload)
        return 2, payload

    full_result_path = project_root / result_path
    if not full_result_path.exists():
        mark_implementation_plan_failed(
            project_root,
            version=resolved_version,
            feature=feature,
            run_id=run_id,
            reason_code="runner_result_missing",
        )
        payload = {
            **base_state,
            "status": "failed",
            "reason_code": "runner_result_missing",
            "command": command,
            "stdout_path": str(stdout_path),
            "stderr_path": str(stderr_path),
        }
        write_json(state_path, payload)
        return 2, payload

    try:
        result_payload = json.loads(full_result_path.read_text(encoding="utf-8"))
    except Exception as exc:  # noqa: BLE001
        mark_implementation_plan_failed(
            project_root,
            version=resolved_version,
            feature=feature,
            run_id=run_id,
            reason_code="runner_result_invalid",
        )
        payload = {
            **base_state,
            "status": "failed",
            "reason_code": "runner_result_invalid",
            "problems": [f"result json parse failed: {exc}"],
        }
        write_json(state_path, payload)
        return 2, payload
    problems = _validate_result(result_payload)
    if problems:
        mark_implementation_plan_failed(
            project_root,
            version=resolved_version,
            feature=feature,
            run_id=run_id,
            reason_code="runner_result_invalid",
        )
        payload = {
            **base_state,
            "status": "failed",
            "reason_code": "runner_result_invalid",
            "problems": problems,
        }
        write_json(state_path, payload)
        return 2, payload

    if str(result_payload.get("status", "")).strip().lower() != "completed":
        mark_implementation_plan_failed(
            project_root,
            version=resolved_version,
            feature=feature,
            run_id=run_id,
            reason_code="implement_execution_failed",
        )
        payload = {
            **base_state,
            "status": "failed",
            "reason_code": "implement_execution_failed",
            "result": result_payload,
        }
        write_json(state_path, payload)
        return 2, payload

    marker = project_root / ".beacon" / "state" / f"implementation-{feature_slug}.json"
    write_json(
        marker,
        {
            "schema_version": "1.0",
            "run_id": run_id,
            "feature": feature,
            "feature_slug": feature_slug,
            "version": resolved_version,
            "runner": adapter_id,
            "skill": rendered_skill,
            "status": "completed",
            "generated_at": now_iso(),
        },
    )

    review_spec_info: dict[str, Any] | None = None
    review_quality_info: dict[str, Any] | None = None
    if auto_review_spec:
        rc, payload = _run_review_command(project_root, resolved_version, feature, "spec")
        review_spec_info = {"exit_code": rc, "payload": payload}
    if auto_review_quality:
        rc, payload = _run_review_command(project_root, resolved_version, feature, "quality")
        review_quality_info = {"exit_code": rc, "payload": payload}

    summary_paths = _summary_paths(project_root, resolved_version, feature)
    archive_paths = _technical_archive_paths(project_root, resolved_version, feature)
    story_state = load_story_state(project_root, version=resolved_version, feature=feature, create_if_missing=True) or {}
    implemented_item_ids = [str(item) for item in _normalize_string_list(result_payload.get("implemented_items"))]
    if not implemented_item_ids:
        implemented_item_ids = _story_item_ids(story_state, kinds={"ac", "task"})
    implemented_task_ids = [str(item) for item in _normalize_string_list(result_payload.get("implemented_task_ids"))]
    writeback_payload = record_implementation_writeback(
        project_root,
        version=resolved_version,
        feature=feature,
        run_id=run_id,
        implemented_item_ids=implemented_item_ids,
        task_ids=implemented_task_ids,
        changed_files=result_payload.get("changed_files", []),
    )
    summary_payload = {
        "schema_version": "1.0",
        "run_id": run_id,
        "feature": feature,
        "feature_slug": feature_slug,
        "version": resolved_version,
        "runner": adapter_id,
        "adapter_type": adapter_type,
        "skill": rendered_skill,
        "status": "completed",
        "summary": str(result_payload.get("summary", "")),
        "changed_files": result_payload.get("changed_files", []),
        "verification": result_payload.get("verification", []),
        "implemented_task_ids": implemented_task_ids,
        "verified_task_ids": result_payload.get("verified_task_ids", []),
        "blocked_task_ids": result_payload.get("blocked_task_ids", []),
        "failed_task_ids": result_payload.get("failed_task_ids", []),
        "artifact_updates": result_payload.get("artifact_updates", {}),
        "request_path": str(request_path),
        "result_path": str(result_path),
        "stdout_path": str(stdout_path),
        "stderr_path": str(stderr_path),
        "branch_preflight_path": str(branch_preflight_path),
        "branch_preflight": branch_preflight,
        "plan_preflight_path": str(plan_preflight_path),
        "plan_preflight": implementation_plan_gate,
        "implementation_plan": implementation_plan_file,
        "implementation_plan_progress": load_implementation_plan_progress(project_root, version=resolved_version, feature=feature),
        "implementation_marker": str(marker.relative_to(project_root)),
        "technical_archive": {
            "json": str(archive_paths["json"].relative_to(project_root)),
            "md": str(archive_paths["md"].relative_to(project_root)),
        },
        "review_spec": review_spec_info,
        "review_quality": review_quality_info,
        "generated_at": now_iso(),
        "writeback": writeback_payload,
    }
    technical_payload = _technical_archive_payload(
        project_root=project_root,
        version=resolved_version,
        feature=feature,
        run_id=run_id,
        runner=adapter_id,
        skill=rendered_skill,
        request_path=str(request_path),
        result_path=str(result_path),
        stdout_path=str(stdout_path),
        stderr_path=str(stderr_path),
        result_payload=result_payload,
    )
    technical_payload["revision_id"] = str(story_state.get("current_revision_id", "") or "")
    write_json(archive_paths["json"], technical_payload)
    _write_text(archive_paths["md"], _render_technical_archive_markdown(technical_payload))
    refresh_evidence_manifest(
        project_root,
        refs=[
            str(archive_paths["json"].relative_to(project_root)),
            str(archive_paths["md"].relative_to(project_root)),
        ],
        version=resolved_version,
    )
    learning_payload = write_requirement_rewrite_input(
        project_root,
        version=resolved_version,
        feature=feature,
        archive_payload=technical_payload,
        archive_path=str(archive_paths["json"].relative_to(project_root)),
    )
    obligations = write_artifact_update_obligations(
        project_root,
        version=resolved_version,
        feature=feature,
        run_id=run_id,
        updates=result_payload.get("artifact_updates") if isinstance(result_payload.get("artifact_updates"), dict) else {},
        technical_archive_path=str(archive_paths["json"].relative_to(project_root)),
    )
    summary_payload["artifact_writeback_obligations"] = str(
        (
            project_root
            / ".beacon"
            / "state"
            / "artifact-update-obligations"
            / f"{feature_slug}.json"
        ).relative_to(project_root)
    )
    summary_payload["artifact_writeback_open_count"] = int(obligations.get("open_count", 0) or 0)
    summary_payload["requirement_rewrite_input"] = str(learning_payload.get("path", "") or "")
    handoff_path = write_implement_to_qa_handoff(
        project_root,
        version=resolved_version,
        feature=feature,
        run_id=run_id,
        summary_ref=str(summary_paths["json"].relative_to(project_root)),
        technical_archive_ref=str(archive_paths["json"].relative_to(project_root)),
        evidence_refs=[str(summary_paths["json"].relative_to(project_root)), str(archive_paths["json"].relative_to(project_root))],
        changed_files=result_payload.get("changed_files", []),
        implementation_plan_ref=implementation_plan_file,
    )
    summary_payload["implement_to_qa_handoff"] = str(handoff_path.relative_to(project_root))
    summary_payload["auto_qa"] = {
        "enabled": bool(auto_qa),
        "triggered": False,
        "args": resolved_auto_qa_args,
        "follow_handoff": bool(auto_qa_follow_handoff),
        "max_rounds": int(auto_qa_max_rounds or 1),
    }
    auto_qa_exit = 0
    if auto_qa:
        auto_qa_exit, auto_qa_payload = _run_auto_qa_sequence(
            project_root,
            feature=feature,
            version=resolved_version,
            extra_args=resolved_auto_qa_args,
            follow_handoff=bool(auto_qa_follow_handoff),
            max_rounds=int(auto_qa_max_rounds or 1),
        )
        summary_payload["auto_qa"] = auto_qa_payload
    write_json(summary_paths["json"], summary_payload)
    _write_text(summary_paths["md"], _render_summary_markdown(summary_payload))
    refresh_evidence_manifest(
        project_root,
        refs=[
            str(summary_paths["json"].relative_to(project_root)),
            str(summary_paths["md"].relative_to(project_root)),
        ],
        version=resolved_version,
    )

    payload = {**base_state, **summary_payload}
    write_json(state_path, payload)
    return auto_qa_exit, payload


@app.command("list-runners")
def list_runners(
    project_root: str = typer.Option("", "--project-root", "--project", "-p", help="Project root path"),
    json_output: bool = typer.Option(False, "--json", help="Emit JSON output"),
):
    """List implementation runners available to Beacon."""
    root = Path(project_root) if project_root else Path.cwd()
    adapters = discover_skill_adapters(root)
    preferred = resolve_default_runner(root) or _default_runner_for_version(root, "v1.3.0")
    rows = []
    for adapter_id, adapter in sorted(adapters.items()):
        detected, evidence = detect_adapter(adapter_id, root)
        rows.append(
            {
                "id": adapter_id,
                "adapter_type": str(adapter.get("adapter_type", "")),
                "runtime_family": str(adapter.get("runtime_family", "")),
                "preferred": adapter_id == preferred,
                "detected": detected,
                "evidence": evidence,
            }
        )
    if json_output:
        typer.echo(json.dumps({"preferred": preferred or "", "runners": rows}, ensure_ascii=False, indent=2))
        return
    typer.echo("Beacon Implement Runners")
    typer.echo("=" * 25)
    for row in rows:
        marker = "*" if row["preferred"] else "-"
        typer.echo(f"{marker} {row['id']} ({row['adapter_type']}) detected={row['detected']}")


@app.command("run")
def run(
    feature: str = typer.Argument(..., help="Feature name"),
    project: Optional[str] = typer.Option(None, "--project", "--project-root", "-p", help="Project root"),
    version: str = typer.Option("auto", "--version", "-v", help="Version (auto=largest docs semver)"),
    runner: str = typer.Option("auto", "--runner", help="Runner id or auto"),
    skill: str = typer.Option("", "--skill", help="Override adapter skill"),
    task_template: str = typer.Option("", "--task-template", help="Override task template"),
    dry_run: bool = typer.Option(False, "--dry-run", help="Write request only"),
    timeout_sec: int = typer.Option(0, "--timeout-sec", help="Override timeout seconds"),
    auto_review_spec: bool = typer.Option(True, "--auto-review-spec/--no-auto-review-spec", help="Auto trigger review spec"),
    auto_review_quality: bool = typer.Option(False, "--auto-review-quality/--no-auto-review-quality", help="Auto trigger review quality"),
    auto_qa: Optional[bool] = typer.Option(None, "--auto-qa/--no-auto-qa", help="Auto trigger qa run after successful implementation"),
    auto_qa_arg: Optional[list[str]] = typer.Option(None, "--auto-qa-arg", help="Extra argument passed to auto-triggered qa run (repeatable)"),
    auto_qa_follow_handoff: Optional[bool] = typer.Option(None, "--auto-qa-follow-handoff/--no-auto-qa-follow-handoff", help="When auto-qa is blocked, follow supported repair handoff actions and retry QA"),
    auto_qa_max_rounds: int = typer.Option(0, "--auto-qa-max-rounds", help="Maximum QA rounds in the auto-qa follow-handoff loop"),
    auto_switch_branch: bool = typer.Option(False, "--auto-switch-branch", help="Explicitly switch/create the expected Beacon version branch before implementation"),
    json_output: bool = typer.Option(False, "--json", help="Emit JSON output"),
):
    """Run implementation using the resolved skill adapter."""
    project_root = Path(project) if project else Path.cwd()
    code, payload = run_implement_stage(
        feature=feature,
        project_root=project_root,
        version=version,
        runner=runner,
        skill=skill or None,
        task_template=task_template or None,
        dry_run=dry_run,
        timeout_sec=timeout_sec or None,
        auto_review_spec=auto_review_spec,
        auto_review_quality=auto_review_quality,
        auto_qa=auto_qa,
        auto_qa_args=list(auto_qa_arg or []),
        auto_qa_follow_handoff=auto_qa_follow_handoff,
        auto_qa_max_rounds=auto_qa_max_rounds or None,
        auto_switch_branch=auto_switch_branch,
    )
    if json_output:
        typer.echo(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        typer.echo(f"Beacon implement status: {payload.get('status')}")
        typer.echo(f"run_id: {payload.get('run_id', '')}")
        if payload.get("reason_code"):
            typer.echo(f"reason_code: {payload.get('reason_code')}")
    raise typer.Exit(code=code)


@app.command("check-branch")
def check_branch(
    project: Optional[str] = typer.Option(None, "--project", "--project-root", "-p", help="Project root"),
    version: str = typer.Option("auto", "--version", "-v", help="Version (auto=largest docs semver)"),
    feature: str = typer.Option("implement-branch-preflight", "--feature", help="Feature label for traceability"),
    auto_switch_branch: bool = typer.Option(False, "--auto-switch-branch", help="Explicitly switch/create the expected Beacon version branch"),
    json_output: bool = typer.Option(False, "--json", help="Emit JSON output"),
):
    """Check or repair the required Beacon implementation branch before coding."""
    project_root = Path(project) if project else Path.cwd()
    resolved_version = resolve_target_version(project_root, version)
    run_id = generate_run_id(project_root)
    payload = _run_branch_preflight(
        project_root=project_root,
        version=resolved_version,
        run_id=run_id,
        feature=feature,
        auto_switch_branch=auto_switch_branch,
        require_clean_worktree_for_switch=True,
    )
    payload["branch_preflight_path"] = str(_branch_preflight_path(run_id))
    write_json(project_root / _branch_preflight_path(run_id), payload)
    if json_output:
        typer.echo(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        typer.echo(f"Beacon implement branch check: {payload.get('status')}")
        typer.echo(f"expected_branch: {payload.get('expected_branch', '')}")
        typer.echo(f"current_branch: {payload.get('current_branch', '')}")
        if payload.get("recommended_command"):
            typer.echo(f"recommended_command: {payload.get('recommended_command')}")
    raise typer.Exit(code=2 if payload.get("blocked") else 0)


def _plan_impl(feature: str, project: Optional[str], version: str, json_output: bool) -> int:
    project_root = Path(project) if project else Path.cwd()
    code, payload = compile_implementation_plan(project_root, version=version, feature=feature)
    if json_output:
        typer.echo(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        typer.echo(f"Beacon implementation plan status: {payload.get('status')}")
        if payload.get("plan_id"):
            typer.echo(f"plan_id: {payload.get('plan_id')}")
        if payload.get("plan_path"):
            typer.echo(f"plan_path: {payload.get('plan_path')}")
        if payload.get("reason_code"):
            typer.echo(f"reason_code: {payload.get('reason_code')}")
    return code


def _team_plan_impl(feature: str, project: Optional[str], version: str, json_output: bool) -> int:
    project_root = Path(project) if project else Path.cwd()
    code, payload = compile_implementation_plan(project_root, version=version, feature=feature)
    resolved_version = resolve_target_version(project_root, version)
    team_mode = {
        "preferred_surface": "implement-team",
        "preferred_runner": "codex-subagents" if _semver_tuple(resolved_version) >= (1, 3, 0) else "native-team",
        "plan_command": f'beacon implement team-plan "{feature}" --project-root {project_root} --version {resolved_version}',
        "run_command": f'beacon implement team-run "{feature}" --project {project_root} --version {resolved_version}',
    }
    payload = {
        **payload,
        "team_surface": "implement-team",
        "team_mode": payload.get("team_mode", {}) or team_mode,
        "recommended_command": str((payload.get("team_mode", {}) or team_mode).get("run_command") or ""),
    }
    if json_output:
        typer.echo(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        typer.echo(f"Beacon implement team-plan status: {payload.get('status')}")
        typer.echo(f"team_surface: implement-team")
        if payload.get("recommended_command"):
            typer.echo(f"recommended_command: {payload.get('recommended_command')}")
    return code


@app.command("plan")
def plan(
    feature: str = typer.Argument(..., help="Feature name"),
    project: Optional[str] = typer.Option(None, "--project", "--project-root", "-p", help="Project root"),
    version: str = typer.Option("auto", "--version", "-v", help="Version (auto=largest docs semver)"),
    json_output: bool = typer.Option(False, "--json", help="Emit JSON output"),
):
    """Compile PRD/user-story/test-case into an implementation plan."""
    raise typer.Exit(code=_plan_impl(feature, project, version, json_output))


@app.command("team-plan")
def team_plan(
    feature: str = typer.Argument(..., help="Feature name"),
    project: Optional[str] = typer.Option(None, "--project", "--project-root", "-p", help="Project root"),
    version: str = typer.Option("auto", "--version", "-v", help="Version (auto=largest docs semver)"),
    json_output: bool = typer.Option(False, "--json", help="Emit JSON output"),
):
    """Compile an implementation plan with explicit implement-team guidance."""
    raise typer.Exit(code=_team_plan_impl(feature, project, version, json_output))


@app.command("compile-plan")
def compile_plan(
    feature: str = typer.Argument(..., help="Feature name"),
    project: Optional[str] = typer.Option(None, "--project", "--project-root", "-p", help="Project root"),
    version: str = typer.Option("auto", "--version", "-v", help="Version (auto=largest docs semver)"),
    json_output: bool = typer.Option(False, "--json", help="Emit JSON output"),
):
    """Alias of `implement plan`."""
    raise typer.Exit(code=_plan_impl(feature, project, version, json_output))


@app.command("team-run")
def team_run(
    feature: str = typer.Argument(..., help="Feature name"),
    project: Optional[str] = typer.Option(None, "--project", "--project-root", "-p", help="Project root"),
    version: str = typer.Option("auto", "--version", "-v", help="Version (auto=largest docs semver)"),
    auto_review_spec: bool = typer.Option(True, "--auto-review-spec/--no-auto-review-spec", help="Auto trigger review spec"),
    auto_review_quality: bool = typer.Option(False, "--auto-review-quality/--no-auto-review-quality", help="Auto trigger review quality"),
    json_output: bool = typer.Option(False, "--json", help="Emit JSON output"),
):
    """Run implementation through the explicit implement-team surface."""
    project_root = Path(project) if project else Path.cwd()
    code, payload = run_implement_stage(
        feature=feature,
        project_root=project_root,
        version=version,
        runner="codex-subagents",
        auto_review_spec=auto_review_spec,
        auto_review_quality=auto_review_quality,
    )
    if json_output:
        typer.echo(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        typer.echo(f"Beacon implement team-run status: {payload.get('status')}")
        typer.echo(f"team_surface: {payload.get('team_surface', '')}")
        typer.echo(f"run_id: {payload.get('run_id', '')}")
    raise typer.Exit(code=code)


@app.command("status")
def status(
    feature_or_run_id: str = typer.Argument(..., help="Feature name or run id"),
    project: Optional[str] = typer.Option(None, "--project", "--project-root", "-p", help="Project root"),
    version: str = typer.Option("auto", "--version", "-v", help="Version (auto=largest docs semver)"),
    run_id: str = typer.Option("", "--run-id", help="Explicit run id"),
    json_output: bool = typer.Option(False, "--json", help="Emit JSON output"),
):
    """Show implementation run status."""
    project_root = Path(project) if project else Path.cwd()
    resolved_version = resolve_target_version(project_root, version)
    target_run = run_id.strip()
    feature_slug = _slug(feature_or_run_id)
    implement_root = project_root / ".beacon" / "implement"
    state_payload: dict[str, Any] | None = None
    if target_run:
        state_path = implement_root / target_run / "state.json"
        if state_path.exists():
            state_payload = json.loads(state_path.read_text(encoding="utf-8"))
    else:
        candidate_states = sorted(implement_root.glob("*/state.json")) if implement_root.exists() else []
        for state_path in reversed(candidate_states):
            payload = json.loads(state_path.read_text(encoding="utf-8"))
            if str(payload.get("feature_slug", "")) == feature_slug or str(payload.get("feature", "")) == feature_or_run_id:
                state_payload = payload
                break
        if state_payload is None and feature_or_run_id.startswith("run-"):
            state_path = implement_root / feature_or_run_id / "state.json"
            if state_path.exists():
                state_payload = json.loads(state_path.read_text(encoding="utf-8"))
    if state_payload is None:
        typer.echo("Implementation run not found", err=True)
        raise typer.Exit(2)

    slug = str(state_payload.get("feature_slug", feature_slug))
    summary = _summary_paths(project_root, resolved_version, slug).get("json")
    review_spec = execution_file_candidates(project_root, resolved_version, f"review-spec-{slug}.json")
    review_quality = execution_file_candidates(project_root, resolved_version, f"review-quality-{slug}.json")
    output = dict(state_payload)
    output["summary_exists"] = bool(summary and summary.exists())
    output["review_spec_exists"] = any(path.exists() for path in review_spec)
    output["review_quality_exists"] = any(path.exists() for path in review_quality)
    output["implementation_marker_exists"] = (project_root / ".beacon" / "state" / f"implementation-{slug}.json").exists()
    output["implementation_plan_exists"] = implementation_plan_json_path(project_root, resolved_version, slug).exists()
    output["implementation_plan_markdown_exists"] = implementation_plan_markdown_path(project_root, resolved_version, slug).exists()
    output["implementation_plan_progress_exists"] = implementation_plan_progress_path(project_root, resolved_version, slug).exists()
    output["implementation_plan_progress"] = load_implementation_plan_progress(project_root, version=resolved_version, feature=slug)
    if json_output:
        typer.echo(json.dumps(output, ensure_ascii=False, indent=2))
        return
    typer.echo(json.dumps(output, ensure_ascii=False, indent=2))
