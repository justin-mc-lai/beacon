"""Project skill registry, profile, orchestration, and evidence gate helpers."""

from __future__ import annotations

import json
import subprocess
from pathlib import Path
from typing import Any

from beacon.utils.artifact_paths import machine_execution_dir
from beacon.utils.implement_adapters import format_template
from beacon.utils.runtime import generate_run_id, now_iso, read_json, write_json
from beacon.utils.skill_config import load_yaml_like, write_yaml_like
from beacon.utils.story_state import feature_slug
from beacon.utils.versioning import resolve_target_version


def project_skill_config_path(project_root: Path) -> Path:
    return project_root / "beacon.config.yaml"


def _load_config(project_root: Path) -> dict[str, Any]:
    path = project_skill_config_path(project_root)
    if not path.exists():
        return {}
    payload = load_yaml_like(path)
    return payload if isinstance(payload, dict) else {}


def _write_config(project_root: Path, payload: dict[str, Any]) -> Path:
    path = project_skill_config_path(project_root)
    write_yaml_like(path, payload)
    return path


def _project_skills_section(config: dict[str, Any]) -> dict[str, Any]:
    section = config.get("project_skills")
    if isinstance(section, dict):
        return section
    section = {}
    config["project_skills"] = section
    return section


def builtin_skill_registry() -> dict[str, dict[str, Any]]:
    return {
        "native-single": {
            "id": "native-single",
            "kind": "builtin",
            "entry": "beacon implement run --runner native-single",
            "capabilities": ["implementation"],
            "supported_stages": ["implementation"],
            "evidence_contract": ["implementation_summary", "story_writeback"],
        },
        "native-team": {
            "id": "native-team",
            "kind": "builtin",
            "entry": "beacon implement run --runner native-team",
            "capabilities": ["implementation", "coordination"],
            "supported_stages": ["implementation"],
            "evidence_contract": ["implementation_summary", "team_execution", "story_writeback"],
        },
        "qa9-default": {
            "id": "qa9-default",
            "kind": "builtin",
            "entry": "beacon auto-test create qa9",
            "capabilities": ["verify", "qa"],
            "supported_stages": ["verify"],
            "evidence_contract": ["auto_test_status", "qa_matrix_evidence"],
        },
        "review-quality": {
            "id": "review-quality",
            "kind": "builtin",
            "entry": "beacon review quality",
            "capabilities": ["review", "gate"],
            "supported_stages": ["review"],
            "evidence_contract": ["review_quality_report"],
        },
    }


def _default_external_entry(skill_id: str) -> str:
    home = Path.home()
    if (home / ".agents" / "skills" / skill_id / "scripts").exists():
        candidates = sorted((home / ".agents" / "skills" / skill_id / "scripts").glob("*.sh"))
        if candidates:
            return str(candidates[0])
    if (home / ".codex" / "skills" / skill_id / "scripts").exists():
        candidates = sorted((home / ".codex" / "skills" / skill_id / "scripts").glob("*.sh"))
        if candidates:
            return str(candidates[0])
    return ""


def load_skill_registry(project_root: Path) -> dict[str, dict[str, Any]]:
    config = _load_config(project_root)
    section = _project_skills_section(config)
    registry = dict(builtin_skill_registry())
    external = section.get("registry")
    if isinstance(external, dict):
        for skill_id, payload in external.items():
            if not isinstance(payload, dict):
                continue
            merged = dict(payload)
            merged.setdefault("id", str(skill_id))
            merged.setdefault("kind", "external")
            merged.setdefault("entry", _default_external_entry(str(skill_id)))
            merged.setdefault("capabilities", [])
            merged.setdefault("supported_stages", [])
            merged.setdefault("evidence_contract", [])
            registry[str(skill_id)] = merged
    return registry


def list_skill_registry(project_root: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for skill_id, payload in sorted(load_skill_registry(project_root).items()):
        entry = str(payload.get("entry", "") or "")
        rows.append(
            {
                "id": skill_id,
                "kind": str(payload.get("kind", "builtin")),
                "entry": entry,
                "detected": bool(entry and Path(entry).exists()) or str(payload.get("kind", "")) == "builtin",
                "capabilities": list(payload.get("capabilities", [])),
                "supported_stages": list(payload.get("supported_stages", [])),
                "evidence_contract": list(payload.get("evidence_contract", [])),
            }
        )
    return rows


def _rolo_profile_example() -> dict[str, Any]:
    rolo_entry = _default_external_entry("rolo-dev") or str(Path.home() / ".agents" / "skills" / "rolo-dev" / "scripts" / "rolo_dev.sh")
    return {
        "registry": {
            "rolo-dev": {
                "id": "rolo-dev",
                "kind": "external",
                "entry": rolo_entry,
                "capabilities": ["verify", "delivery", "debug", "pipeline", "uat-smoke"],
                "supported_stages": ["verify", "delivery", "debug", "pipeline"],
                "evidence_contract": ["uat_pipeline_run", "gateway_smoke", "interface_response", "log_sql_snapshot"],
            }
        },
        "profiles": {
            "rolo-uat": {
                "project": "rolo",
                "profile_id": "rolo-uat",
                "description": "Rolo UAT multi-service verification profile.",
                "skills": {
                    "verify": "rolo-dev",
                    "delivery": "rolo-dev",
                    "debug": "rolo-dev",
                    "pipeline": "rolo-dev",
                },
                "required_evidence": [
                    "uat_pipeline_run",
                    "gateway_smoke",
                    "interface_response",
                ],
                "required_cases": [
                    "upload_jpg_success",
                    "upload_gif_success",
                    "upload_mp4_success",
                    "invalid_type_rejected",
                    "oss_json_publish_success",
                ],
                "contracts": [
                    {
                        "id": "splash-upload-types",
                        "description": "Splash upload types must stay aligned across docs, FE, and downstream STS service.",
                        "sources": [
                            {
                                "path": "docs/beacon/v1.3.0/user-story/splash-marketing-content.md",
                                "required_tokens": ["GIF", "视频", "material_url"],
                            },
                            {
                                "path": "marketing_primary_fe/src/modules/marketing/views/SplashMarketingContent/components/SplashTaskFormCard.vue",
                                "required_tokens": ["mp4", "mov", "webm"],
                            },
                            {
                                "path": "report-svr/app/services/sts_upload_service.go",
                                "required_tokens": [".gif", ".mp4"],
                            },
                        ],
                    }
                ],
                "orchestration": {
                    "nodes": [
                        {
                            "id": "pipeline",
                            "stage": "verify",
                            "skill": "rolo-dev",
                            "command_template": "{skill_entry} pipeline --service {service_name}",
                            "produces_evidence": ["uat_pipeline_run"],
                        },
                        {
                            "id": "gateway-smoke",
                            "stage": "verify",
                            "skill": "rolo-dev",
                            "command_template": "{skill_entry} uat-smoke --jwt {jwt_token}",
                            "produces_evidence": ["gateway_smoke", "interface_response"],
                        },
                    ]
                },
            }
        },
    }


def create_project_profile(
    project_root: Path,
    *,
    project: str,
    profile_id: str,
    example: str | None = None,
) -> Path:
    config = _load_config(project_root)
    section = _project_skills_section(config)
    section.setdefault("registry", {})
    section.setdefault("profiles", {})
    if example == "rolo-uat":
        example_payload = _rolo_profile_example()
        registry = section.setdefault("registry", {})
        if isinstance(registry, dict):
            registry.update(example_payload["registry"])
        profiles = section.setdefault("profiles", {})
        if isinstance(profiles, dict):
            payload = dict(example_payload["profiles"]["rolo-uat"])
            payload["project"] = project
            payload["profile_id"] = profile_id
            profiles[profile_id] = payload
        section["default_profile"] = profile_id
    else:
        profiles = section.setdefault("profiles", {})
        if isinstance(profiles, dict):
            profiles[profile_id] = {
                "project": project,
                "profile_id": profile_id,
                "description": "Beacon project profile",
                "skills": {},
                "required_evidence": [],
                "required_cases": [],
                "contracts": [],
                "orchestration": {"nodes": []},
            }
        section["default_profile"] = profile_id
    return _write_config(project_root, config)


def load_project_profiles(project_root: Path) -> dict[str, dict[str, Any]]:
    config = _load_config(project_root)
    section = _project_skills_section(config)
    profiles = section.get("profiles")
    if not isinstance(profiles, dict):
        return {}
    return {str(key): dict(value) for key, value in profiles.items() if isinstance(value, dict)}


def load_project_profile(project_root: Path, profile_id: str) -> dict[str, Any] | None:
    return load_project_profiles(project_root).get(profile_id)


def default_project_profile(project_root: Path) -> str | None:
    config = _load_config(project_root)
    section = _project_skills_section(config)
    profile_id = str(section.get("default_profile", "") or "").strip()
    return profile_id or None


def profile_binding_path(project_root: Path, version: str, feature: str) -> Path:
    resolved_version = resolve_target_version(project_root, version)
    return machine_execution_dir(project_root, resolved_version) / f"{feature_slug(feature)}.profile.json"


def bind_feature_profile(
    project_root: Path,
    *,
    version: str,
    feature: str,
    profile_id: str,
) -> Path:
    path = profile_binding_path(project_root, version, feature)
    write_json(
        path,
        {
            "schema_version": "1.0",
            "feature": feature,
            "feature_slug": feature_slug(feature),
            "version": resolve_target_version(project_root, version),
            "profile_id": profile_id,
            "bound_at": now_iso(),
        },
    )
    return path


def load_feature_profile_binding(project_root: Path, *, version: str, feature: str) -> dict[str, Any] | None:
    path = profile_binding_path(project_root, version, feature)
    if not path.exists():
        return None
    payload = read_json(path, {})
    return payload if isinstance(payload, dict) else None


def resolve_profile_for_feature(
    project_root: Path,
    *,
    version: str,
    feature: str,
    explicit_profile: str | None = None,
) -> dict[str, Any] | None:
    profile_id = str(explicit_profile or "").strip()
    if not profile_id:
        binding = load_feature_profile_binding(project_root, version=version, feature=feature)
        if binding:
            profile_id = str(binding.get("profile_id", "") or "").strip()
    if not profile_id:
        profile_id = str(default_project_profile(project_root) or "").strip()
    if not profile_id:
        return None
    profile = load_project_profile(project_root, profile_id)
    if not profile:
        return None
    profile = dict(profile)
    profile.setdefault("profile_id", profile_id)
    return profile


def orchestration_state_path(project_root: Path, version: str, feature: str) -> Path:
    resolved_version = resolve_target_version(project_root, version)
    return machine_execution_dir(project_root, resolved_version) / f"{feature_slug(feature)}.orchestration.json"


def _node_evidence_path(project_root: Path, feature: str, run_id: str, node_id: str) -> Path:
    return project_root / ".beacon" / "evidence" / "orchestration" / feature_slug(feature) / run_id / f"{node_id}.json"


def _profile_context(
    *,
    project_root: Path,
    version: str,
    feature: str,
    profile_id: str,
    skill_entry: str,
    run_id: str,
    params: dict[str, str],
) -> dict[str, Any]:
    return {
        "project_root": str(project_root),
        "version": resolve_target_version(project_root, version),
        "feature": feature,
        "feature_slug": feature_slug(feature),
        "profile_id": profile_id,
        "skill_entry": skill_entry,
        "run_id": run_id,
        **params,
    }


def run_profile_orchestration(
    project_root: Path,
    *,
    version: str,
    feature: str,
    profile_id: str | None = None,
    stage: str | None = None,
    dry_run: bool = False,
    params: dict[str, str] | None = None,
) -> tuple[int, dict[str, Any]]:
    profile = resolve_profile_for_feature(project_root, version=version, feature=feature, explicit_profile=profile_id)
    if not profile:
        payload = {
            "schema_version": "1.0",
            "status": "blocked",
            "reason_code": "project_profile_missing",
            "feature": feature,
            "version": resolve_target_version(project_root, version),
        }
        return 2, payload

    resolved_version = resolve_target_version(project_root, version)
    resolved_profile_id = str(profile.get("profile_id", "") or profile_id or "")
    registry = load_skill_registry(project_root)
    nodes = profile.get("orchestration", {}).get("nodes", [])
    if not isinstance(nodes, list):
        nodes = []
    selected_nodes = [
        dict(node) for node in nodes if isinstance(node, dict) and (not stage or str(node.get("stage", "") or "") == stage)
    ]
    run_id = generate_run_id(project_root)
    param_map = {str(k): str(v) for k, v in (params or {}).items()}
    node_results: list[dict[str, Any]] = []
    produced_evidence: list[dict[str, Any]] = []
    produced_cases: list[dict[str, Any]] = []
    status = "completed"

    for node in selected_nodes:
        node_id = str(node.get("id", "") or f"node-{len(node_results)+1:03d}")
        skill_id = str(node.get("skill", "") or profile.get("skills", {}).get(str(node.get("stage", "")), "") or "")
        skill_payload = registry.get(skill_id, {})
        skill_entry = str(skill_payload.get("entry", "") or "")
        context = _profile_context(
            project_root=project_root,
            version=resolved_version,
            feature=feature,
            profile_id=resolved_profile_id,
            skill_entry=skill_entry,
            run_id=run_id,
            params=param_map,
        )
        command_template = str(node.get("command_template", "") or "")
        command = format_template(command_template, context) if command_template else ""
        result_payload = {
            "node_id": node_id,
            "stage": str(node.get("stage", "") or ""),
            "skill_id": skill_id,
            "skill_kind": str(skill_payload.get("kind", "")),
            "command": command,
            "status": "planned" if dry_run else "pending",
            "evidence_path": str(_node_evidence_path(project_root, feature, run_id, node_id).relative_to(project_root)),
            "produces_evidence": list(node.get("produces_evidence", [])),
            "produces_cases": list(node.get("produces_cases", [])),
        }

        if dry_run:
            node_results.append(result_payload)
            continue

        if not command:
            result_payload["status"] = "blocked"
            result_payload["reason_code"] = "orchestration_command_missing"
            status = "blocked"
            node_results.append(result_payload)
            break

        completed = subprocess.run(
            command,
            cwd=project_root,
            shell=True,
            capture_output=True,
            text=True,
            check=False,
        )
        result_payload.update(
            {
                "status": "passed" if completed.returncode == 0 else "failed",
                "exit_code": int(completed.returncode),
                "stdout": completed.stdout,
                "stderr": completed.stderr,
            }
        )
        write_json(_node_evidence_path(project_root, feature, run_id, node_id), result_payload)
        node_results.append(result_payload)
        if completed.returncode != 0:
            status = "failed"
            for key in result_payload["produces_evidence"]:
                produced_evidence.append({"key": key, "status": "failed", "node_id": node_id})
            for case_id in result_payload["produces_cases"]:
                produced_cases.append({"id": case_id, "status": "failed", "node_id": node_id})
            break

        for key in result_payload["produces_evidence"]:
            produced_evidence.append({"key": key, "status": "passed", "node_id": node_id, "ref": result_payload["evidence_path"]})
        for case_id in result_payload["produces_cases"]:
            produced_cases.append({"id": case_id, "status": "passed", "node_id": node_id, "ref": result_payload["evidence_path"]})

    summary = {
        "schema_version": "1.0",
        "feature": feature,
        "feature_slug": feature_slug(feature),
        "version": resolved_version,
        "profile_id": resolved_profile_id,
        "run_id": run_id,
        "stage": stage or "",
        "status": "dry_run" if dry_run else status,
        "generated_at": now_iso(),
        "nodes": node_results,
        "produced_evidence": produced_evidence,
        "produced_cases": produced_cases,
        "required_evidence": list(profile.get("required_evidence", [])),
        "required_cases": list(profile.get("required_cases", [])),
    }
    write_json(orchestration_state_path(project_root, resolved_version, feature), summary)
    return (0 if summary["status"] in {"completed", "dry_run"} else 2), summary


def load_orchestration_state(project_root: Path, *, version: str, feature: str) -> dict[str, Any] | None:
    path = orchestration_state_path(project_root, version, feature)
    if not path.exists():
        return None
    payload = read_json(path, {})
    return payload if isinstance(payload, dict) else None


def evaluate_contract_drifts(project_root: Path, *, profile: dict[str, Any]) -> list[dict[str, Any]]:
    drifts: list[dict[str, Any]] = []
    for contract in profile.get("contracts", []):
        if not isinstance(contract, dict):
            continue
        contract_id = str(contract.get("id", "") or "contract")
        description = str(contract.get("description", "") or "")
        missing_tokens: list[dict[str, Any]] = []
        for source in contract.get("sources", []):
            if not isinstance(source, dict):
                continue
            rel = str(source.get("path", "") or "")
            path = project_root / rel
            if not path.exists():
                missing_tokens.append({"path": rel, "missing": ["<file_missing>"]})
                continue
            text = path.read_text(encoding="utf-8")
            missing = [token for token in source.get("required_tokens", []) if str(token) not in text]
            if missing:
                missing_tokens.append({"path": rel, "missing": missing})
        if missing_tokens:
            drifts.append(
                {
                    "id": contract_id,
                    "reason_code": "contract_drift",
                    "summary": description or contract_id,
                    "details": missing_tokens,
                }
            )
    return drifts


def evaluate_project_profile_gate(
    project_root: Path,
    *,
    version: str,
    feature: str,
    profile_id: str | None = None,
) -> dict[str, Any]:
    profile = resolve_profile_for_feature(project_root, version=version, feature=feature, explicit_profile=profile_id)
    if not profile:
        return {
            "status": "not_configured",
            "profile_id": "",
            "issues": [],
            "required_evidence": [],
            "required_cases": [],
            "contract_drifts": [],
        }

    orchestration = load_orchestration_state(project_root, version=version, feature=feature) or {}
    evidence_rows = orchestration.get("produced_evidence", []) if isinstance(orchestration.get("produced_evidence"), list) else []
    case_rows = orchestration.get("produced_cases", []) if isinstance(orchestration.get("produced_cases"), list) else []
    evidence_status = {str(item.get("key", "")): str(item.get("status", "")) for item in evidence_rows if isinstance(item, dict)}
    case_status = {str(item.get("id", "")): str(item.get("status", "")) for item in case_rows if isinstance(item, dict)}

    required_evidence = [str(item) for item in profile.get("required_evidence", []) if str(item).strip()]
    required_cases = [str(item) for item in profile.get("required_cases", []) if str(item).strip()]
    issues: list[dict[str, Any]] = []

    for key in required_evidence:
        status = evidence_status.get(key, "")
        if status != "passed":
            issues.append(
                {
                    "reason_code": "required_evidence_missing",
                    "severity": "critical",
                    "message": f"required evidence missing or not passed: {key}",
                    "evidence_key": key,
                }
            )

    for case_id in required_cases:
        status = case_status.get(case_id, "")
        if status == "failed":
            issues.append(
                {
                    "reason_code": "required_case_failed",
                    "severity": "critical",
                    "message": f"required case failed: {case_id}",
                    "case_id": case_id,
                }
            )
        elif status != "passed":
            issues.append(
                {
                    "reason_code": "required_case_missing",
                    "severity": "critical",
                    "message": f"required case missing or not passed: {case_id}",
                    "case_id": case_id,
                }
            )

    contract_drifts = evaluate_contract_drifts(project_root, profile=profile)
    for drift in contract_drifts:
        issues.append(
            {
                "reason_code": "contract_drift",
                "severity": "critical",
                "message": str(drift.get("summary", "contract drift detected")),
                "contract_id": str(drift.get("id", "")),
                "details": drift.get("details", []),
            }
        )

    status = "pass" if not issues else "blocked"
    return {
        "status": status,
        "profile_id": str(profile.get("profile_id", "")),
        "issues": issues,
        "required_evidence": required_evidence,
        "required_cases": required_cases,
        "contract_drifts": contract_drifts,
        "orchestration": orchestration,
    }
