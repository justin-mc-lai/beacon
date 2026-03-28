"""v1.1.9 control/recovery plane helpers."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from beacon.utils.runtime import newest_run_id, now_iso, read_json, write_json


def exhaustion_state_path(project_root: Path) -> Path:
    return project_root / ".beacon" / "state" / "exhaustion.json"


def checkpoint_path(project_root: Path, *, run_id: str) -> Path:
    return project_root / ".beacon" / "state" / "checkpoints" / f"{run_id}.json"


def _resolve_run_id(project_root: Path, run_id: str | None = None) -> str:
    explicit = str(run_id or "").strip()
    if explicit:
        return explicit
    latest = newest_run_id(project_root)
    return latest or ""


def _normalize_text_list(values: Any) -> list[str]:
    if values is None:
        return []
    if isinstance(values, str):
        return [values.strip()] if values.strip() else []
    if not isinstance(values, list):
        return []
    out: list[str] = []
    seen: set[str] = set()
    for item in values:
        text = str(item or "").strip()
        if not text or text in seen:
            continue
        seen.add(text)
        out.append(text)
    return out


def _escalation_level(failure_streak: int) -> str:
    if failure_streak >= 4:
        return "E4"
    if failure_streak == 3:
        return "E3"
    if failure_streak == 2:
        return "E2"
    if failure_streak == 1:
        return "E1"
    return "E0"


def _required_next_action(level: str) -> str:
    mapping = {
        "E0": "continue_current_plan",
        "E1": "switch_strategy",
        "E2": "collect_docs_or_source_evidence",
        "E3": "complete_exhaustiveness_checklist",
        "E4": "enter_recoverable_loop_or_structured_fail",
    }
    return mapping.get(str(level or "E0"), "continue_current_plan")


def _default_hypothesis(stage: str, reason_code: str, blocker: str) -> str:
    key = str(reason_code or blocker or "unknown").strip().lower()
    if "verify" in key or "evidence" in key:
        return f"refresh {stage} verification evidence and rerun only the affected scope"
    if "implementation" in key or "runner" in key:
        return f"switch {stage} execution strategy and capture a narrower technical archive"
    if "gate" in key:
        return "close blocking evidence/writeback obligations before re-entering gate"
    if "contract" in key or "drift" in key:
        return "repair requirement or spec drift before the next execution attempt"
    return f"collect one new evidence slice before retrying {stage}"


def _default_evidence_gap(stage: str, reason_code: str) -> list[str]:
    key = str(reason_code or "").strip().lower()
    if key == "verify_status_artifact_missing":
        return ["missing verify status artifact (.beacon/auto-test-status.json)"]
    if key == "verify_not_passed":
        return ["verify evidence exists but did not pass"]
    if key == "missing_implementation_command":
        return ["implementation runner/command not configured"]
    if key == "gate_blocked":
        return ["gate evidence set still has blocked items"]
    if "artifact" in key:
        return [f"missing artifact for {stage}"]
    return [f"missing conclusive evidence for {stage}"] if stage else []


def load_exhaustion_state(project_root: Path) -> dict[str, Any]:
    payload = read_json(exhaustion_state_path(project_root), {})
    if not isinstance(payload, dict):
        payload = {}
    payload.setdefault("schema_version", "1.0")
    payload.setdefault("active_run_id", "")
    payload.setdefault("updated_at", "")
    runs = payload.get("runs") if isinstance(payload.get("runs"), dict) else {}
    payload["runs"] = runs
    return payload


def save_exhaustion_state(project_root: Path, payload: dict[str, Any]) -> Path:
    payload = dict(payload)
    payload["schema_version"] = "1.0"
    payload["updated_at"] = now_iso()
    write_json(exhaustion_state_path(project_root), payload)
    return exhaustion_state_path(project_root)


def exhaustion_for_run(project_root: Path, *, run_id: str | None = None) -> dict[str, Any]:
    state = load_exhaustion_state(project_root)
    target = _resolve_run_id(project_root, run_id)
    runs = state.get("runs") if isinstance(state.get("runs"), dict) else {}
    payload = runs.get(target) if target else {}
    if not isinstance(payload, dict):
        payload = {}
    payload.setdefault("run_id", target)
    payload.setdefault("failure_streak", 0)
    payload.setdefault("escalation_level", "E0")
    payload.setdefault("last_failed_stage", "")
    payload.setdefault("attempted_strategies", [])
    payload.setdefault("excluded_causes", [])
    payload.setdefault("next_hypothesis", "")
    payload.setdefault("evidence_gap", [])
    payload.setdefault("current_blocker", "")
    payload.setdefault("required_next_action", _required_next_action(str(payload.get("escalation_level") or "E0")))
    payload.setdefault("latest_checkpoint_ref", "")
    return payload


def append_recovery_checkpoint(
    project_root: Path,
    *,
    run_id: str,
    stage: str,
    attempted_strategy: str,
    excluded_causes: list[str] | None = None,
    next_hypothesis: str = "",
    evidence_gap: list[str] | None = None,
    current_blocker: str = "",
    reason_code: str = "",
    recommended_command: str = "",
    details: dict[str, Any] | None = None,
) -> dict[str, Any]:
    path = checkpoint_path(project_root, run_id=run_id)
    payload = read_json(path, {})
    if not isinstance(payload, dict):
        payload = {}
    checkpoints = payload.get("checkpoints") if isinstance(payload.get("checkpoints"), list) else []
    checkpoint_id = f"cp-{len(checkpoints) + 1:03d}"
    entry = {
        "checkpoint_id": checkpoint_id,
        "run_id": run_id,
        "stage": str(stage or "").strip(),
        "created_at": now_iso(),
        "attempted_strategy": str(attempted_strategy or "").strip(),
        "excluded_causes": _normalize_text_list(excluded_causes),
        "next_hypothesis": str(next_hypothesis or "").strip(),
        "evidence_gap": _normalize_text_list(evidence_gap),
        "current_blocker": str(current_blocker or "").strip(),
        "reason_code": str(reason_code or "").strip(),
        "recommended_command": str(recommended_command or "").strip(),
        "details": details or {},
    }
    checkpoints.append(entry)
    payload.update(
        {
            "schema_version": "1.0",
            "run_id": run_id,
            "updated_at": now_iso(),
            "latest_checkpoint_id": checkpoint_id,
            "checkpoints": checkpoints,
        }
    )
    write_json(path, payload)
    return {**entry, "path": str(path.relative_to(project_root))}


def load_recovery_checkpoint(project_root: Path, *, run_id: str | None = None) -> dict[str, Any]:
    target = _resolve_run_id(project_root, run_id)
    if not target:
        return {}
    payload = read_json(checkpoint_path(project_root, run_id=target), {})
    if not isinstance(payload, dict):
        return {}
    checkpoints = payload.get("checkpoints") if isinstance(payload.get("checkpoints"), list) else []
    latest_id = str(payload.get("latest_checkpoint_id", "") or "")
    for item in reversed(checkpoints):
        if not isinstance(item, dict):
            continue
        if latest_id and str(item.get("checkpoint_id", "")) != latest_id:
            continue
        return {**item, "path": str(checkpoint_path(project_root, run_id=target).relative_to(project_root))}
    return {}


def record_stage_failure(
    project_root: Path,
    *,
    run_id: str,
    stage: str,
    attempted_strategy: str,
    reason_code: str,
    current_blocker: str = "",
    excluded_causes: list[str] | None = None,
    evidence_gap: list[str] | None = None,
    next_hypothesis: str = "",
    recommended_command: str = "",
    details: dict[str, Any] | None = None,
) -> dict[str, Any]:
    state = load_exhaustion_state(project_root)
    runs = state.get("runs") if isinstance(state.get("runs"), dict) else {}
    current = runs.get(run_id) if isinstance(runs.get(run_id), dict) else {}
    streak = int(current.get("failure_streak", 0) or 0) + 1
    level = _escalation_level(streak)
    attempted = _normalize_text_list([*(current.get("attempted_strategies") or []), attempted_strategy])
    excluded = _normalize_text_list([*(current.get("excluded_causes") or []), *(_normalize_text_list(excluded_causes))])
    blocker = str(current_blocker or reason_code or stage or "failure").strip()
    hypothesis = str(next_hypothesis or "").strip() or _default_hypothesis(stage, reason_code, blocker)
    gap = _normalize_text_list(evidence_gap) or _default_evidence_gap(stage, reason_code)
    checkpoint = append_recovery_checkpoint(
        project_root,
        run_id=run_id,
        stage=stage,
        attempted_strategy=attempted_strategy,
        excluded_causes=excluded,
        next_hypothesis=hypothesis,
        evidence_gap=gap,
        current_blocker=blocker,
        reason_code=reason_code,
        recommended_command=recommended_command,
        details=details,
    )
    payload = {
        "run_id": run_id,
        "failure_streak": streak,
        "escalation_level": level,
        "last_failed_stage": str(stage or "").strip(),
        "attempted_strategies": attempted,
        "excluded_causes": excluded,
        "next_hypothesis": hypothesis,
        "evidence_gap": gap,
        "current_blocker": blocker,
        "required_next_action": _required_next_action(level),
        "latest_failure_ts": now_iso(),
        "latest_checkpoint_ref": checkpoint.get("path", ""),
    }
    runs[run_id] = payload
    state["active_run_id"] = run_id
    state["runs"] = runs
    save_exhaustion_state(project_root, state)
    return payload


def record_stage_success(project_root: Path, *, run_id: str, stage: str) -> dict[str, Any]:
    state = load_exhaustion_state(project_root)
    runs = state.get("runs") if isinstance(state.get("runs"), dict) else {}
    current = runs.get(run_id) if isinstance(runs.get(run_id), dict) else exhaustion_for_run(project_root, run_id=run_id)
    current["failure_streak"] = 0
    current["escalation_level"] = "E0"
    current["required_next_action"] = _required_next_action("E0")
    current["last_resolved_stage"] = str(stage or "").strip()
    current["last_resolved_at"] = now_iso()
    runs[run_id] = current
    state["active_run_id"] = run_id
    state["runs"] = runs
    save_exhaustion_state(project_root, state)
    return current


def build_resume_contract(project_root: Path, *, run_id: str | None = None) -> dict[str, Any]:
    target = _resolve_run_id(project_root, run_id)
    exhaustion = exhaustion_for_run(project_root, run_id=target)
    checkpoint = load_recovery_checkpoint(project_root, run_id=target)
    return {
        "run_id": target,
        "failure_streak": int(exhaustion.get("failure_streak", 0) or 0),
        "escalation_level": str(exhaustion.get("escalation_level", "E0") or "E0"),
        "required_next_action": str(exhaustion.get("required_next_action", "continue_current_plan") or "continue_current_plan"),
        "last_failed_stage": str(exhaustion.get("last_failed_stage", "") or ""),
        "tried_approaches": _normalize_text_list(exhaustion.get("attempted_strategies")),
        "excluded_causes": _normalize_text_list(exhaustion.get("excluded_causes")),
        "next_hypothesis": str(checkpoint.get("next_hypothesis") or exhaustion.get("next_hypothesis") or ""),
        "evidence_gap": _normalize_text_list(checkpoint.get("evidence_gap") or exhaustion.get("evidence_gap")),
        "current_blocker": str(checkpoint.get("current_blocker") or exhaustion.get("current_blocker") or ""),
        "recommended_command": str(checkpoint.get("recommended_command") or ""),
        "checkpoint_ref": str(checkpoint.get("path") or exhaustion.get("latest_checkpoint_ref") or ""),
        "checkpoint": checkpoint,
    }
