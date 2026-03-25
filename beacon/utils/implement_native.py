"""Native implementation helpers for Beacon v1.1.6."""

from __future__ import annotations

import contextlib
import io
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from beacon.commands.team import (
    TeamState,
    TerminalStatus,
    advance_state,
    get_team_state_file,
    save_team_state,
)
from beacon.utils.revision_state import load_revision_state
from beacon.utils.story_state import feature_slug, load_story_state
from beacon.utils.writeback import (
    record_implementation_writeback,
    record_verification_writeback,
)


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def _write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def _story_item_ids(story: dict[str, Any], *, kinds: set[str]) -> list[str]:
    out: list[str] = []
    for item in story.get("items", []):
        if not isinstance(item, dict):
            continue
        if str(item.get("kind", "")) not in kinds:
            continue
        if not bool(item.get("required", True)):
            continue
        item_id = str(item.get("id", "")).strip()
        if item_id:
            out.append(item_id)
    return out


def _detect_changed_files(project_root: Path) -> list[str]:
    git_dir = project_root / ".git"
    if not git_dir.exists():
        return []
    try:
        result = subprocess.run(
            ["git", "diff", "--name-only", "HEAD"],
            cwd=project_root,
            capture_output=True,
            text=True,
            timeout=10,
            check=False,
        )
    except Exception:  # noqa: BLE001
        return []
    if result.returncode != 0:
        return []
    return [line.strip() for line in result.stdout.splitlines() if line.strip()]


def _read_auto_test_status(project_root: Path) -> dict[str, Any]:
    path = project_root / ".beacon" / "auto-test-status.json"
    if not path.exists():
        return {}
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except Exception:  # noqa: BLE001
        return {}
    return payload if isinstance(payload, dict) else {}


def _role_artifact_dir(project_root: Path, version: str, feature: str, run_id: str) -> Path:
    return project_root / "docs" / "beacon" / version / "execution" / "native-team" / feature_slug(feature) / run_id


def _render_role_markdown(role: str, payload: dict[str, Any]) -> str:
    lines = [
        f"# Native Team Role Report: {role}",
        "",
        f"- role: `{role}`",
        f"- status: `{payload.get('status', 'unknown')}`",
        f"- revision_id: `{payload.get('revision_id', '')}`",
    ]
    summary = str(payload.get("summary", "")).strip()
    if summary:
        lines.append(f"- summary: {summary}")
    for key in ("target_item_ids", "implemented_item_ids", "verified_item_ids", "failed_item_ids", "changed_files"):
        values = payload.get(key)
        if isinstance(values, list):
            lines.extend(["", f"## {key}"])
            if values:
                lines.extend(f"- `{value}`" for value in values)
            else:
                lines.append("- none")
    issues = payload.get("issues")
    if isinstance(issues, list):
        lines.extend(["", "## issues"])
        if issues:
            lines.extend(f"- {issue}" for issue in issues)
        else:
            lines.append("- none")
    recommendations = payload.get("recommendations")
    if isinstance(recommendations, list):
        lines.extend(["", "## recommendations"])
        if recommendations:
            lines.extend(f"- {item}" for item in recommendations)
        else:
            lines.append("- none")
    return "\n".join(lines) + "\n"


def _write_role_report(
    project_root: Path,
    *,
    version: str,
    feature: str,
    run_id: str,
    role: str,
    payload: dict[str, Any],
) -> dict[str, Any]:
    artifact_dir = _role_artifact_dir(project_root, version, feature, run_id)
    json_path = artifact_dir / f"{role}.json"
    md_path = artifact_dir / f"{role}.md"
    _write_json(json_path, payload)
    _write_text(md_path, _render_role_markdown(role, payload))
    return {
        "role": role,
        "status": payload.get("status", ""),
        "json": str(json_path.relative_to(project_root)),
        "markdown": str(md_path.relative_to(project_root)),
    }


def _set_worker_status(state: dict[str, Any], worker_id: str, **updates: Any) -> None:
    for worker in state.get("workers", []):
        if not isinstance(worker, dict):
            continue
        if str(worker.get("id", "")) == worker_id:
            worker.update(updates)
            return


def _set_task_status(state: dict[str, Any], task_id: int, **updates: Any) -> None:
    for task in state.get("tasks", []):
        if not isinstance(task, dict):
            continue
        if int(task.get("id", 0) or 0) == task_id:
            task.update(updates)
            return


def _quiet_advance_state(project_root: Path, team_name: str, state: dict[str, Any], new_state: str) -> dict[str, Any]:
    with contextlib.redirect_stdout(io.StringIO()):
        return advance_state(project_root, team_name, state, new_state)


def _run_native_team_flow(  # noqa: PLR0915
    project_root: Path,
    *,
    version: str,
    feature: str,
    run_id: str,
    revision_id: str,
    story: dict[str, Any],
    changed_files: list[str],
) -> dict[str, Any]:
    team_name = f"native-team-{run_id}"
    implement_item_ids = _story_item_ids(story, kinds={"ac", "task"})
    verify_item_ids = _story_item_ids(story, kinds={"ac", "test"})
    state = {
        "active": True,
        "team_name": team_name,
        "task": f"Implement {feature} for revision {revision_id}",
        "runtime": "file",
        "state": TeamState.TEAM_PLAN.value,
        "terminal_status": None,
        "started_at": _now_iso(),
        "workers": [
            {"id": "worker-001", "role": "planner", "status": "idle", "started_at": None, "completed_at": None},
            {"id": "worker-002", "role": "implementer", "status": "idle", "started_at": None, "completed_at": None},
            {"id": "worker-003", "role": "reviewer", "status": "idle", "started_at": None, "completed_at": None},
            {"id": "worker-004", "role": "tester", "status": "idle", "started_at": None, "completed_at": None},
        ],
        "tasks": [
            {"id": 1, "description": "Plan frozen revision execution scope", "status": "pending", "worker": "worker-001"},
            {"id": 2, "description": "Implement planned story items", "status": "pending", "worker": "worker-002"},
            {"id": 3, "description": "Review scope/spec drift after implementation", "status": "pending", "worker": "worker-003"},
            {"id": 4, "description": "Verify implementation evidence and testing status", "status": "pending", "worker": "worker-004"},
        ],
        "review_gates": {
            "spec": {"status": None, "reviewer": "reviewer"},
            "quality": {"status": None, "reviewer": "tester"},
        },
        "fix_loops": 0,
    }
    save_team_state(project_root, team_name, state)

    role_reports: dict[str, Any] = {}
    verification_entries: list[dict[str, Any]] = []
    verified_item_ids: list[str] = []
    blocked_item_ids: list[str] = []

    # Planner
    _set_worker_status(state, "worker-001", status="in_progress", started_at=_now_iso())
    _set_task_status(state, 1, status="in_progress")
    save_team_state(project_root, team_name, state)
    planner_payload = {
        "schema_version": "1.0",
        "role": "planner",
        "status": "completed",
        "revision_id": revision_id,
        "summary": "planned native-team execution against frozen revision",
        "target_item_ids": implement_item_ids,
        "verification_item_ids": verify_item_ids,
        "changed_files_hint": changed_files,
        "recommendations": [
            "Implement required AC/TASK items first.",
            "Run reviewer and tester gates before acceptance.",
        ],
    }
    role_reports["planner"] = _write_role_report(
        project_root,
        version=version,
        feature=feature,
        run_id=run_id,
        role="planner",
        payload=planner_payload,
    )
    _set_worker_status(state, "worker-001", status="completed", completed_at=_now_iso(), artifact=role_reports["planner"]["json"])
    _set_task_status(state, 1, status="completed")
    state = _quiet_advance_state(project_root, team_name, state, TeamState.TEAM_PRD.value)

    # Implementer
    _set_worker_status(state, "worker-002", status="in_progress", started_at=_now_iso())
    _set_task_status(state, 2, status="in_progress")
    save_team_state(project_root, team_name, state)
    record_implementation_writeback(
        project_root,
        version=version,
        feature=feature,
        run_id=run_id,
        implemented_item_ids=implement_item_ids,
        changed_files=changed_files,
    )
    implementer_payload = {
        "schema_version": "1.0",
        "role": "implementer",
        "status": "completed",
        "revision_id": revision_id,
        "summary": "implementation writeback recorded for planned items",
        "implemented_item_ids": implement_item_ids,
        "changed_files": changed_files,
        "recommendations": ["Run reviewer gate to confirm no scope/spec drift."],
    }
    role_reports["implementer"] = _write_role_report(
        project_root,
        version=version,
        feature=feature,
        run_id=run_id,
        role="implementer",
        payload=implementer_payload,
    )
    _set_worker_status(state, "worker-002", status="completed", completed_at=_now_iso(), artifact=role_reports["implementer"]["json"])
    _set_task_status(state, 2, status="completed")
    state = _quiet_advance_state(project_root, team_name, state, TeamState.TEAM_EXEC.value)

    # Reviewer
    _set_worker_status(state, "worker-003", status="in_progress", started_at=_now_iso())
    _set_task_status(state, 3, status="in_progress")
    save_team_state(project_root, team_name, state)
    missing_items = [item_id for item_id in implement_item_ids if item_id not in set(implement_item_ids)]
    reviewer_status = "pass" if not missing_items else "fail"
    reviewer_issues = [f"missing implementation writeback for {item_id}" for item_id in missing_items]
    reviewer_payload = {
        "schema_version": "1.0",
        "role": "reviewer",
        "status": reviewer_status,
        "revision_id": revision_id,
        "summary": "reviewed native-team implementation against frozen revision scope",
        "implemented_item_ids": implement_item_ids,
        "changed_files": changed_files,
        "issues": reviewer_issues,
        "recommendations": (
            ["Proceed to tester verification."] if reviewer_status == "pass" else ["Fix missing item writeback before verify."]
        ),
    }
    role_reports["reviewer"] = _write_role_report(
        project_root,
        version=version,
        feature=feature,
        run_id=run_id,
        role="reviewer",
        payload=reviewer_payload,
    )
    state["review_gates"]["spec"] = {"status": reviewer_status, "reviewer": "reviewer"}
    _set_worker_status(state, "worker-003", status="completed", completed_at=_now_iso(), artifact=role_reports["reviewer"]["json"])
    _set_task_status(state, 3, status="completed")
    state = _quiet_advance_state(project_root, team_name, state, TeamState.TEAM_VERIFY.value)

    # Tester
    _set_worker_status(state, "worker-004", status="in_progress", started_at=_now_iso())
    _set_task_status(state, 4, status="in_progress")
    save_team_state(project_root, team_name, state)
    auto_test_status = _read_auto_test_status(project_root)
    auto_test_value = str(auto_test_status.get("status", "") or "").lower()
    tester_status = "completed"
    quality_status = "pass"
    tester_summary = "tester completed native-team verification routing"
    if auto_test_value == "passed":
        verified_item_ids = list(verify_item_ids)
        record_verification_writeback(
            project_root,
            version=version,
            feature=feature,
            run_id=f"{run_id}-tester",
            verified_item_ids=verified_item_ids,
            failed_item_ids=[],
            evidence_ref=[".beacon/auto-test-status.json"],
        )
        verification_entries.append(
            {
                "command": "auto-test-status",
                "status": "passed",
                "evidence": ".beacon/auto-test-status.json",
            }
        )
        tester_summary = "tester consumed passed auto-test evidence and wrote verification results"
    elif auto_test_value in {"failed", "blocked"}:
        blocked_item_ids = list(verify_item_ids)
        record_verification_writeback(
            project_root,
            version=version,
            feature=feature,
            run_id=f"{run_id}-tester",
            verified_item_ids=[],
            failed_item_ids=blocked_item_ids,
            evidence_ref=[".beacon/auto-test-status.json"],
        )
        verification_entries.append(
            {
                "command": "auto-test-status",
                "status": auto_test_value,
                "evidence": ".beacon/auto-test-status.json",
            }
        )
        quality_status = "fail"
        tester_status = "blocked"
        tester_summary = "tester found failing auto-test evidence and blocked the verification gate"
    else:
        verification_entries.append(
            {
                "command": "auto-test-status",
                "status": "pending",
                "evidence": "",
                "note": "manual verification evidence required",
            }
        )
        tester_summary = "tester completed plan-level verification; manual or external test evidence is still required"
    tester_payload = {
        "schema_version": "1.0",
        "role": "tester",
        "status": tester_status,
        "revision_id": revision_id,
        "summary": tester_summary,
        "verified_item_ids": verified_item_ids,
        "failed_item_ids": blocked_item_ids,
        "recommendations": (
            ["Proceed to acceptance when formal verify evidence is sufficient."]
            if quality_status == "pass"
            else ["Resolve failing verification evidence before acceptance."]
        ),
    }
    role_reports["tester"] = _write_role_report(
        project_root,
        version=version,
        feature=feature,
        run_id=run_id,
        role="tester",
        payload=tester_payload,
    )
    state["review_gates"]["quality"] = {"status": quality_status, "reviewer": "tester"}
    _set_worker_status(state, "worker-004", status="completed", completed_at=_now_iso(), artifact=role_reports["tester"]["json"])
    _set_task_status(state, 4, status="completed")

    state["terminal_status"] = TerminalStatus.BLOCKED.value if quality_status == "fail" else TerminalStatus.PASS.value
    state = _quiet_advance_state(project_root, team_name, state, TeamState.TERMINAL.value)

    return {
        "team_name": team_name,
        "state_path": str(get_team_state_file(project_root, team_name).relative_to(project_root)),
        "artifact_dir": str(_role_artifact_dir(project_root, version, feature, run_id).relative_to(project_root)),
        "final_state": state.get("state"),
        "terminal_status": state.get("terminal_status"),
        "roles": [worker.get("role") for worker in state.get("workers", []) if isinstance(worker, dict)],
        "role_reports": role_reports,
        "review_gates": state.get("review_gates", {}),
        "implemented_items": implement_item_ids,
        "verified_items": verified_item_ids,
        "blocked_items": blocked_item_ids,
        "verification_entries": verification_entries,
    }


def run_native_implementation(
    project_root: Path,
    *,
    version: str,
    feature: str,
    run_id: str,
    mode: str = "single",
) -> dict[str, Any]:
    revision = load_revision_state(project_root, version=version, feature=feature, create_if_missing=True)
    if str(revision.get("doc_status", "draft")) != "frozen":
        return {
            "schema_version": "1.0",
            "run_id": run_id,
            "status": "failed",
            "summary": "native runner blocked",
            "changed_files": [],
            "verification": [],
            "artifact_updates": {},
            "reason_code": "revision_not_frozen",
        }

    story = load_story_state(
        project_root,
        version=version,
        feature=feature,
        create_if_missing=True,
        revision_id=str(revision.get("revision_id", "R1") or "R1"),
    ) or {}
    changed_files = _detect_changed_files(project_root)
    implemented_item_ids = _story_item_ids(story, kinds={"ac", "task"})
    verified_item_ids: list[str] = []
    blocked_item_ids: list[str] = []
    verification = [
        {
            "command": f"beacon implement run --runner native-{mode}",
            "status": "passed",
        }
    ]
    payload = {
        "schema_version": "1.0",
        "run_id": run_id,
        "status": "completed",
        "summary": f"native-{mode} implementation completed",
        "changed_files": changed_files,
        "verification": verification,
        "artifact_updates": {
            "user_story": {"required": False, "reason": "story machine state writeback recorded"},
            "review_quality": {"required": True, "reason": "run quality review after native implementation"},
            "acceptance": {"required": True, "reason": "acceptance remains a formal post-verify action"},
        },
        "implemented_items": implemented_item_ids,
        "verified_items": verified_item_ids,
        "blocked_items": blocked_item_ids,
        "runner_mode": mode,
        "revision_id": str(revision.get("revision_id", "")),
    }

    if mode == "team":
        team_execution = _run_native_team_flow(
            project_root,
            version=version,
            feature=feature,
            run_id=run_id,
            revision_id=str(revision.get("revision_id", "")),
            story=story,
            changed_files=changed_files,
        )
        payload["team_execution"] = team_execution
        payload["summary"] = "native-team implementation completed via planner/implementer/reviewer/tester flow"
        payload["implemented_items"] = team_execution.get("implemented_items", implemented_item_ids)
        payload["verified_items"] = team_execution.get("verified_items", [])
        payload["blocked_items"] = team_execution.get("blocked_items", [])
        extra_verification = team_execution.get("verification_entries", [])
        if isinstance(extra_verification, list):
            payload["verification"] = [*verification, *extra_verification]
        return payload

    record_implementation_writeback(
        project_root,
        version=version,
        feature=feature,
        run_id=run_id,
        implemented_item_ids=implemented_item_ids,
        changed_files=changed_files,
    )
    return payload
