"""Shared helpers for explicit Beacon team surfaces."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from beacon.utils.runtime import now_iso, write_json
from beacon.utils.story_state import feature_slug


def _team_roles_root() -> Path:
    return Path(__file__).resolve().parents[1] / "team_roles"


def _load_team_role_config(surface: str) -> dict[str, Any]:
    path = _team_roles_root() / f"{surface}.json"
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:  # noqa: BLE001
        raise RuntimeError(f"invalid team role config for {surface}: {path}") from exc
    if not isinstance(payload, dict):
        raise RuntimeError(f"team role config must be an object: {path}")
    payload["source_path"] = str(path.relative_to(path.parents[2]))
    return payload


def build_context_isolation(
    *,
    role_plane: str,
    isolated_from: list[str],
    shared_inputs: list[str],
    shared_outputs: list[str],
    rule: str,
) -> dict[str, Any]:
    return {
        "role_plane": role_plane,
        "isolated_from": isolated_from,
        "shared_inputs": shared_inputs,
        "shared_outputs": shared_outputs,
        "rule": rule,
    }


def implement_team_contract(project_root: Path, *, version: str, feature: str) -> dict[str, Any]:
    feature_text = str(feature or "").strip()
    config = _load_team_role_config("implement-team")
    context = config.get("context_isolation") if isinstance(config.get("context_isolation"), dict) else {}
    contract = {
        "preferred_surface": str(config.get("preferred_surface", "implement-team")),
        "preferred_runner": str(config.get("preferred_runner", "codex-subagents")),
        "plan_command": f'beacon implement team-plan "{feature_text}" --project-root {project_root} --version {version}',
        "run_command": f'beacon implement team-run "{feature_text}" --project {project_root} --version {version}',
        "dev_run_command": f'beacon implement dev-run "{feature_text}" --project {project_root} --version {version}',
        "qa_team_command": f'beacon qa team-run "{feature_text}" --project {project_root} --version {version}',
        "roles": list(config.get("roles", [])),
        "context_isolation": dict(context),
        "config_source": str(config.get("source_path", "")),
    }
    if isinstance(config.get("execution_order"), list):
        contract["execution_order"] = list(config.get("execution_order", []))
    if isinstance(config.get("formal_writeback_roles"), list):
        contract["formal_writeback_roles"] = list(config.get("formal_writeback_roles", []))
    if isinstance(config.get("role_contracts"), dict):
        contract["role_contracts"] = dict(config.get("role_contracts", {}))
    return contract


def qa_team_contract(project_root: Path, *, version: str, feature: str) -> dict[str, Any]:
    feature_text = str(feature or "").strip()
    config = _load_team_role_config("qa-team")
    context = config.get("context_isolation") if isinstance(config.get("context_isolation"), dict) else {}
    contract = {
        "preferred_surface": str(config.get("preferred_surface", "qa-team")),
        "plan_command": f'beacon qa team-plan "{feature_text}" --project {project_root} --version {version}',
        "run_command": f'beacon qa team-run "{feature_text}" --project {project_root} --version {version}',
        "roles": list(config.get("roles", [])),
        "context_isolation": dict(context),
        "config_source": str(config.get("source_path", "")),
    }
    if isinstance(config.get("role_contracts"), dict):
        contract["role_contracts"] = dict(config.get("role_contracts", {}))
    return contract


def implement_to_qa_handoff_path(project_root: Path, *, feature: str, run_id: str) -> Path:
    return project_root / ".beacon" / "handoffs" / "implement-to-qa" / feature_slug(feature) / f"{run_id}.json"


def write_implement_to_qa_handoff(
    project_root: Path,
    *,
    version: str,
    feature: str,
    run_id: str,
    summary_ref: str,
    technical_archive_ref: str,
    evidence_refs: list[str],
    changed_files: list[str],
    implementation_plan_ref: str,
) -> Path:
    path = implement_to_qa_handoff_path(project_root, feature=feature, run_id=run_id)
    payload = {
        "schema_version": "1.0",
        "handoff_type": "implement-to-qa",
        "generated_at": now_iso(),
        "feature": feature,
        "feature_slug": feature_slug(feature),
        "version": version,
        "run_id": run_id,
        "source_surface": "implement-team",
        "target_surface": "qa-team",
        "summary_ref": summary_ref,
        "technical_archive_ref": technical_archive_ref,
        "implementation_plan_ref": implementation_plan_ref,
        "changed_files": changed_files,
        "evidence_refs": evidence_refs,
        "context_rule": "qa_must_not_inherit_implement_private_context",
    }
    write_json(path, payload)
    return path


def load_implement_to_qa_handoff(project_root: Path, *, feature: str, run_id: str) -> dict[str, Any]:
    path = implement_to_qa_handoff_path(project_root, feature=feature, run_id=run_id)
    if not path.exists():
        return {}
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except Exception:  # noqa: BLE001
        return {}
    return payload if isinstance(payload, dict) else {}
