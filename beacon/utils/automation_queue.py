"""Queue contract helpers for host-scheduled Beacon automation."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from beacon.utils.runtime import read_json


ALLOWED_SCHEMA_VERSIONS = {"v0"}
ALLOWED_JOB_KINDS = {"status", "qa", "implement"}
ALLOWED_TARGET_AGENTS = {"codex", "claude", "cursor", "windsurf", "trae"}
ALLOWED_WORKSPACE_MODES = {"worktree", "local"}
ALLOWED_RISK_LEVELS = {"low", "medium", "high"}
ALLOWED_ACTIONS = {"report_only", "handoff_to_human", "trigger_qa"}
ALLOWED_SELECTOR_MODES = {"all_active", "explicit_list"}


def default_queue_path(project_root: Path) -> Path:
    return project_root / "automation" / "beacon-automation-queue.json"


def load_automation_queue(path: Path) -> dict[str, Any]:
    payload = read_json(path, {})
    return payload if isinstance(payload, dict) else {}


def validate_automation_queue(payload: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if not isinstance(payload, dict):
        return ["queue payload must be a JSON object"]

    schema_version = payload.get("version")
    if schema_version not in ALLOWED_SCHEMA_VERSIONS:
        errors.append(f"version must be one of {sorted(ALLOWED_SCHEMA_VERSIONS)}")

    project_root = payload.get("project_root")
    if not isinstance(project_root, str) or not project_root.strip():
        errors.append("project_root must be a non-empty string")

    workspace_mode = payload.get("default_workspace_mode")
    if workspace_mode not in ALLOWED_WORKSPACE_MODES:
        errors.append(f"default_workspace_mode must be one of {sorted(ALLOWED_WORKSPACE_MODES)}")

    jobs = payload.get("jobs")
    if not isinstance(jobs, list) or not jobs:
        errors.append("jobs must be a non-empty array")
        return errors

    seen_job_ids: set[str] = set()
    for index, job in enumerate(jobs):
        prefix = f"jobs[{index}]"
        if not isinstance(job, dict):
            errors.append(f"{prefix} must be an object")
            continue

        job_id = job.get("job_id")
        if not isinstance(job_id, str) or not job_id.strip():
            errors.append(f"{prefix}.job_id must be a non-empty string")
        elif job_id in seen_job_ids:
            errors.append(f"{prefix}.job_id must be unique")
        else:
            seen_job_ids.add(job_id)

        job_kind = job.get("job_kind")
        if job_kind not in ALLOWED_JOB_KINDS:
            errors.append(f"{prefix}.job_kind must be one of {sorted(ALLOWED_JOB_KINDS)}")

        target_agent = job.get("target_agent")
        if target_agent not in ALLOWED_TARGET_AGENTS:
            errors.append(f"{prefix}.target_agent must be one of {sorted(ALLOWED_TARGET_AGENTS)}")

        enabled = job.get("enabled")
        if not isinstance(enabled, bool):
            errors.append(f"{prefix}.enabled must be a boolean")

        selector = job.get("feature_selector")
        if not isinstance(selector, dict):
            errors.append(f"{prefix}.feature_selector must be an object")
        else:
            mode = selector.get("mode")
            if mode not in ALLOWED_SELECTOR_MODES:
                errors.append(f"{prefix}.feature_selector.mode must be one of {sorted(ALLOWED_SELECTOR_MODES)}")
            if mode == "explicit_list":
                features = selector.get("features")
                if not isinstance(features, list):
                    errors.append(f"{prefix}.feature_selector.features must be an array when mode=explicit_list")
                elif any(not isinstance(item, str) or not item.strip() for item in features):
                    errors.append(f"{prefix}.feature_selector.features must contain non-empty strings")
            if mode == "all_active" and job_kind != "status":
                errors.append(f"{prefix}.feature_selector.mode=all_active is supported only for status jobs")

        preconditions = job.get("preconditions")
        if not isinstance(preconditions, list) or any(not isinstance(item, str) or not item.strip() for item in preconditions):
            errors.append(f"{prefix}.preconditions must be an array of non-empty strings")

        job_workspace_mode = job.get("workspace_mode")
        if job_workspace_mode not in ALLOWED_WORKSPACE_MODES:
            errors.append(f"{prefix}.workspace_mode must be one of {sorted(ALLOWED_WORKSPACE_MODES)}")

        risk_level = job.get("risk_level")
        if risk_level not in ALLOWED_RISK_LEVELS:
            errors.append(f"{prefix}.risk_level must be one of {sorted(ALLOWED_RISK_LEVELS)}")

        on_blocked = job.get("on_blocked")
        if on_blocked not in ALLOWED_ACTIONS:
            errors.append(f"{prefix}.on_blocked must be one of {sorted(ALLOWED_ACTIONS)}")

        on_success = job.get("on_success")
        if on_success not in ALLOWED_ACTIONS:
            errors.append(f"{prefix}.on_success must be one of {sorted(ALLOWED_ACTIONS)}")

        notes = job.get("notes")
        if not isinstance(notes, str):
            errors.append(f"{prefix}.notes must be a string")

        if job_kind == "implement" and risk_level != "high":
            errors.append(f"{prefix}.implement jobs must declare risk_level=high")
        if job_kind == "implement" and on_success != "trigger_qa":
            errors.append(f"{prefix}.implement jobs must declare on_success=trigger_qa")
        if job_kind == "status" and on_success != "report_only":
            errors.append(f"{prefix}.status jobs must declare on_success=report_only")

    return errors


def build_automation_queue_validation_payload(project_root: Path, queue_path: Path) -> dict[str, Any]:
    payload = load_automation_queue(queue_path)
    errors = validate_automation_queue(payload)
    return {
        "schema_version": "1.0",
        "status": "valid" if not errors else "invalid",
        "project_root": str(project_root),
        "queue_path": str(queue_path),
        "error_count": len(errors),
        "errors": errors,
        "queue": payload,
    }
