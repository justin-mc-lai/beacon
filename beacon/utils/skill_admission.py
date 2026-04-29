"""Runtime skill admission helpers for implement --skill."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from beacon.utils.implement_adapters import load_beacon_config
from beacon.utils.runtime import now_iso, write_json
from beacon.utils.story_state import feature_slug
from beacon.utils.subagent_readiness import detect_host_runtime
from beacon.utils.versioning import resolve_target_version


_SUPPORTED_STAGES = {
    "prototype": "prototype",
    "implement": "implement",
    "implementation": "implement",
    "qa": "qa",
    "verify": "qa",
    "review": "qa",
    "release": "release",
}


def _normalize_stage(value: str | None) -> str:
    text = str(value or "").strip().lower()
    return _SUPPORTED_STAGES.get(text, text)


def _slug(value: str) -> str:
    return feature_slug(value)


def _skill_slug(value: str) -> str:
    return _slug(Path(str(value or "")).name or str(value or "skill"))


def skill_admission_state_path(project_root: Path, *, version: str, feature: str, skill: str) -> Path:
    return (
        project_root
        / ".beacon"
        / "state"
        / "skill-admission"
        / resolve_target_version(project_root, version)
        / f"{feature_slug(feature)}--{_skill_slug(skill)}.json"
    )


def skill_admission_machine_path(project_root: Path, *, version: str, feature: str) -> Path:
    resolved_version = resolve_target_version(project_root, version)
    return (
        project_root
        / "docs"
        / "beacon"
        / resolved_version
        / ".machine"
        / "execution"
        / f"skill-admission-{feature_slug(feature)}.json"
    )


def _hint_payload(project_root: Path, skill: str) -> dict[str, Any]:
    config = load_beacon_config(project_root)
    skill_cfg = config.get("skill") if isinstance(config.get("skill"), dict) else {}
    admission_cfg = skill_cfg.get("admission") if isinstance(skill_cfg.get("admission"), dict) else {}
    hints = admission_cfg.get("skills") if isinstance(admission_cfg.get("skills"), dict) else {}
    payload = hints.get(skill)
    return dict(payload) if isinstance(payload, dict) else {}


def _candidate_skill_roots(project_root: Path, *, skill: str, host_runtime: str) -> list[Path]:
    candidates: list[Path] = []
    seen: set[str] = set()

    def _add(path: Path | None) -> None:
        if path is None:
            return
        key = str(path.expanduser().resolve()) if path.exists() else str(path.expanduser())
        if key in seen:
            return
        seen.add(key)
        candidates.append(path.expanduser())

    skill_path = Path(skill).expanduser()
    if skill_path.exists():
        _add(skill_path)

    hints = _hint_payload(project_root, skill)
    hint_path = str(hints.get("path", "") or "").strip()
    if hint_path:
        _add(Path(hint_path))

    local_roots = [
        project_root / "skills" / skill,
        project_root / ".agents" / "skills" / skill,
        project_root / ".codex" / "skills" / skill,
        project_root / ".claude" / "skills" / skill,
    ]
    home = Path.home()
    home_roots = [
        home / ".agents" / "skills" / skill,
        home / ".codex" / "skills" / skill,
        home / ".claude" / "skills" / skill,
    ]
    preferred = (
        [project_root / "skills" / skill, project_root / ".claude" / "skills" / skill, home / ".claude" / "skills" / skill]
        if host_runtime == "claude"
        else [
            project_root / "skills" / skill,
            project_root / ".agents" / "skills" / skill,
            home / ".agents" / "skills" / skill,
            project_root / ".codex" / "skills" / skill,
            home / ".codex" / "skills" / skill,
        ]
    )
    for item in [*preferred, *local_roots, *home_roots]:
        _add(item)
    return candidates


def _contract_candidates(project_root: Path, *, skill_root: Path, skill: str) -> list[Path]:
    candidates: list[Path] = []
    seen: set[str] = set()

    def _add(path: Path | None) -> None:
        if path is None:
            return
        key = str(path.expanduser())
        if key in seen:
            return
        seen.add(key)
        candidates.append(path.expanduser())

    hints = _hint_payload(project_root, skill)
    hint_contract = str(hints.get("contract", "") or "").strip()
    if hint_contract:
        _add(Path(hint_contract))
    _add(skill_root / "beacon-skill-contract.json")
    _add(skill_root / ".beacon" / "beacon-skill-contract.json")
    return candidates


def _read_json(path: Path) -> dict[str, Any]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except Exception:  # noqa: BLE001
        return {}
    return payload if isinstance(payload, dict) else {}


def _contract_validation_errors(contract: dict[str, Any], *, host_runtime: str, stage: str) -> list[dict[str, Any]]:
    issues: list[dict[str, Any]] = []
    skill_id = str(contract.get("skill_id", "") or "").strip()
    supported_stages = [
        _normalize_stage(item)
        for item in contract.get("supported_stages", [])
        if str(item or "").strip()
    ] if isinstance(contract.get("supported_stages"), list) else []
    supported_hosts = [
        str(item or "").strip().lower()
        for item in contract.get("supported_host_runtimes", [])
        if str(item or "").strip()
    ] if isinstance(contract.get("supported_host_runtimes"), list) else []
    if not skill_id:
        issues.append({"reason_code": "skill_contract_missing_field", "field": "skill_id"})
    if not supported_stages:
        issues.append({"reason_code": "skill_contract_missing_field", "field": "supported_stages"})
    if not supported_hosts:
        issues.append({"reason_code": "skill_contract_missing_field", "field": "supported_host_runtimes"})
    if not str(contract.get("surface_kind", "") or "").strip():
        issues.append({"reason_code": "skill_contract_missing_field", "field": "surface_kind"})
    if not isinstance(contract.get("output_contract"), dict):
        issues.append({"reason_code": "skill_contract_missing_field", "field": "output_contract"})
    if not isinstance(contract.get("evidence_contract"), (dict, list)):
        issues.append({"reason_code": "skill_contract_missing_field", "field": "evidence_contract"})
    if supported_stages and stage not in supported_stages:
        issues.append(
            {
                "reason_code": "skill_stage_unsupported",
                "stage": stage,
                "supported_stages": supported_stages,
            }
        )
    if supported_hosts and host_runtime not in supported_hosts and "any" not in supported_hosts:
        issues.append(
            {
                "reason_code": "skill_host_incompatible",
                "host_runtime": host_runtime,
                "supported_host_runtimes": supported_hosts,
            }
        )
    return issues


def _legacy_inline_payload(
    *,
    project_root: Path,
    version: str,
    feature: str,
    skill: str,
    host_runtime: str,
    adapter_id: str,
    adapter_type: str,
    stage: str,
) -> dict[str, Any]:
    state_path = skill_admission_state_path(project_root, version=version, feature=feature, skill=skill)
    machine_path = skill_admission_machine_path(project_root, version=version, feature=feature)
    payload = {
        "schema_version": "1.0",
        "feature": feature,
        "feature_slug": feature_slug(feature),
        "version": resolve_target_version(project_root, version),
        "stage": stage,
        "status": "pass",
        "admission_mode": "legacy_inline",
        "reason_code": "",
        "skill_ref": skill,
        "skill_id": skill,
        "host_runtime": host_runtime,
        "adapter_id": adapter_id,
        "adapter_type": adapter_type,
        "discovery": {"status": "legacy_inline", "skill_root": "", "contract_path": "", "used_hint": False},
        "validation": {"status": "not_applicable", "issues": []},
        "compatibility": {"status": "legacy_inline", "supported": True, "supported_host_runtimes": [], "supported_stages": [stage]},
        "contract": {},
        "artifacts": {
            "state_path": str(state_path.relative_to(project_root)),
            "machine_path": str(machine_path.relative_to(project_root)),
        },
        "generated_at": now_iso(),
    }
    write_json(state_path, payload)
    write_json(machine_path, payload)
    return payload


def admit_runtime_skill(
    project_root: Path,
    *,
    version: str,
    feature: str,
    skill: str,
    host_runtime: str | None,
    stage: str = "implement",
    adapter_id: str = "",
    adapter_type: str = "",
) -> dict[str, Any]:
    resolved_version = resolve_target_version(project_root, version)
    resolved_stage = _normalize_stage(stage) or "implement"
    resolved_host = detect_host_runtime(host_runtime)
    state_path = skill_admission_state_path(project_root, version=resolved_version, feature=feature, skill=skill)
    machine_path = skill_admission_machine_path(project_root, version=resolved_version, feature=feature)
    payload = {
        "schema_version": "1.0",
        "feature": feature,
        "feature_slug": feature_slug(feature),
        "version": resolved_version,
        "stage": resolved_stage,
        "skill_ref": skill,
        "skill_id": skill,
        "host_runtime": resolved_host,
        "adapter_id": adapter_id,
        "adapter_type": adapter_type,
        "generated_at": now_iso(),
        "artifacts": {
            "state_path": str(state_path.relative_to(project_root)),
            "machine_path": str(machine_path.relative_to(project_root)),
        },
    }

    if resolved_host == "unknown":
        payload.update(
            {
                "status": "blocked",
                "reason_code": "host_runtime_unknown",
                "discovery": {"status": "not_started", "skill_root": "", "contract_path": "", "used_hint": False},
                "validation": {"status": "blocked", "issues": [{"reason_code": "host_runtime_unknown"}]},
                "compatibility": {"status": "blocked", "supported": False},
                "contract": {},
                "recommended_command": "set --host-runtime codex|claude when using beacon implement --skill",
            }
        )
        write_json(state_path, payload)
        write_json(machine_path, payload)
        return payload

    roots = _candidate_skill_roots(project_root, skill=skill, host_runtime=resolved_host)
    discovered_root = next((path for path in roots if path.exists()), None)
    if discovered_root is None:
        legacy_allowed = adapter_type == "command-skill" or adapter_id in {"omx", "omc"}
        if legacy_allowed:
            return _legacy_inline_payload(
                project_root=project_root,
                version=resolved_version,
                feature=feature,
                skill=skill,
                host_runtime=resolved_host,
                adapter_id=adapter_id,
                adapter_type=adapter_type,
                stage=resolved_stage,
            )
        payload.update(
            {
                "status": "blocked",
                "reason_code": "skill_not_discovered",
                "discovery": {
                    "status": "blocked",
                    "skill_root": "",
                    "contract_path": "",
                    "candidates": [str(path) for path in roots],
                    "used_hint": bool(_hint_payload(project_root, skill)),
                },
                "validation": {"status": "blocked", "issues": [{"reason_code": "skill_not_discovered"}]},
                "compatibility": {"status": "blocked", "supported": False},
                "contract": {},
            }
        )
        write_json(state_path, payload)
        write_json(machine_path, payload)
        return payload

    contract_candidates = _contract_candidates(project_root, skill_root=discovered_root, skill=skill)
    contract_path = next((path for path in contract_candidates if path.exists()), None)
    if contract_path is None:
        payload.update(
            {
                "status": "blocked",
                "reason_code": "skill_contract_missing",
                "discovery": {
                    "status": "pass",
                    "skill_root": str(discovered_root),
                    "contract_path": "",
                    "candidates": [str(path) for path in contract_candidates],
                    "used_hint": bool(_hint_payload(project_root, skill)),
                },
                "validation": {"status": "blocked", "issues": [{"reason_code": "skill_contract_missing"}]},
                "compatibility": {"status": "blocked", "supported": False},
                "contract": {},
            }
        )
        write_json(state_path, payload)
        write_json(machine_path, payload)
        return payload

    contract = _read_json(contract_path)
    validation_issues = _contract_validation_errors(contract, host_runtime=resolved_host, stage=resolved_stage)
    skill_id = str(contract.get("skill_id", "") or skill).strip() or skill
    payload.update(
        {
            "skill_id": skill_id,
            "discovery": {
                "status": "pass",
                "skill_root": str(discovered_root),
                "contract_path": str(contract_path),
                "used_hint": bool(_hint_payload(project_root, skill)),
            },
            "validation": {"status": "blocked" if validation_issues else "pass", "issues": validation_issues},
            "compatibility": {
                "status": "blocked" if validation_issues else "pass",
                "supported": not validation_issues,
                "supported_host_runtimes": list(contract.get("supported_host_runtimes", [])) if isinstance(contract.get("supported_host_runtimes"), list) else [],
                "supported_stages": list(contract.get("supported_stages", [])) if isinstance(contract.get("supported_stages"), list) else [],
            },
            "contract": contract,
        }
    )
    if validation_issues:
        payload["status"] = "blocked"
        payload["reason_code"] = str(validation_issues[0].get("reason_code") or "skill_contract_invalid")
    else:
        payload["status"] = "pass"
        payload["reason_code"] = ""
    write_json(state_path, payload)
    write_json(machine_path, payload)
    return payload
