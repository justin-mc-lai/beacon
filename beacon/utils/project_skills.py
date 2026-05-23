"""Project skill registry, profile, orchestration, and evidence gate helpers."""

from __future__ import annotations

import json
import shlex
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


def capability_learning_events_path(project_root: Path) -> Path:
    return project_root / ".beacon" / "state" / "learning" / "capability-composition-events.jsonl"


def capability_learning_map_path(project_root: Path) -> Path:
    return project_root / ".beacon" / "state" / "learning" / "capability-composition-map.json"


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


_CANONICAL_STAGE_ALIASES: dict[str, str] = {
    "prototype": "prototype",
    "implement": "implement",
    "implementation": "implement",
    "qa": "qa",
    "verify": "qa",
    "review": "qa",
    "release": "release",
    "delivery": "release",
    "debug": "debug",
    "pipeline": "pipeline",
}

_CANONICAL_STAGE_ALTERNATES: dict[str, list[str]] = {
    "prototype": ["prototype"],
    "implement": ["implement", "implementation"],
    "qa": ["qa", "verify", "review"],
    "release": ["release", "delivery"],
    "debug": ["debug"],
    "pipeline": ["pipeline"],
}


def _normalize_stage_name(stage: str | None) -> str:
    normalized = str(stage or "").strip().lower()
    return _CANONICAL_STAGE_ALIASES.get(normalized, normalized)


def _canonical_stage_aliases(stage: str | None) -> list[str]:
    canonical = _normalize_stage_name(stage)
    if not canonical:
        return []
    return list(_CANONICAL_STAGE_ALTERNATES.get(canonical, [canonical]))


def _normalize_stage_list(stages: list[Any]) -> list[str]:
    normalized: list[str] = []
    seen: set[str] = set()
    for item in stages:
        stage = _normalize_stage_name(str(item))
        if not stage or stage in seen:
            continue
        seen.add(stage)
        normalized.append(stage)
    return normalized


def _expand_capabilities(capabilities: list[Any]) -> set[str]:
    expanded: set[str] = set()
    for item in capabilities:
        raw = str(item or "").strip().lower()
        if not raw:
            continue
        expanded.add(raw)
        expanded.add(_normalize_stage_name(raw))
    expanded.discard("")
    return expanded


def _resolve_profile_skill_id(profile_skills: dict[str, Any], stage: str) -> str:
    for key in _canonical_stage_aliases(stage):
        skill_id = str(profile_skills.get(key, "") or "").strip()
        if skill_id:
            return skill_id
    return ""


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


def builtin_skill_registry() -> dict[str, dict[str, Any]]:
    return {
        "native-single": {
            "id": "native-single",
            "kind": "builtin",
            "entry": "beacon implement run --runner native-single",
            "capabilities": ["implement", "implementation"],
            "supported_stages": ["implement"],
            "evidence_contract": ["implementation_summary", "story_writeback"],
        },
        "native-team": {
            "id": "native-team",
            "kind": "builtin",
            "entry": "beacon implement run --runner native-team",
            "capabilities": ["implement", "implementation", "coordination"],
            "supported_stages": ["implement"],
            "evidence_contract": ["implementation_summary", "team_execution", "story_writeback"],
        },
        "codex-subagents": {
            "id": "codex-subagents",
            "kind": "builtin",
            "entry": "beacon implement run --runner codex-subagents",
            "capabilities": ["implement", "implementation", "coordination", "codex-native-team"],
            "supported_stages": ["implement"],
            "evidence_contract": ["implementation_summary", "team_execution", "story_writeback", "context_isolation"],
        },
        "qa9-default": {
            "id": "qa9-default",
            "kind": "builtin",
            "entry": "beacon auto-test create qa9",
            "capabilities": ["qa", "verify"],
            "supported_stages": ["qa"],
            "evidence_contract": ["auto_test_status", "qa_matrix_evidence"],
        },
        "review-quality": {
            "id": "review-quality",
            "kind": "builtin",
            "entry": "beacon review quality",
            "capabilities": ["qa", "review", "gate", "release-readiness"],
            "supported_stages": ["qa"],
            "evidence_contract": ["review_quality_report"],
        },
        "taste-skill": {
            "id": "taste-skill",
            "kind": "external-default-bridge",
            "entry": _default_external_entry("taste-skill"),
            "repo": "https://github.com/Leonxlnx/taste-skill",
            "install_hint": "npx skills add https://github.com/Leonxlnx/taste-skill --skill taste-skill",
            "capabilities": ["prototype", "implement", "taste-design", "semantic-normalization"],
            "supported_stages": ["prototype", "implement"],
            "evidence_contract": ["semantic_dictionary", "semantic_usage_guidelines", "design_review_notes"],
        },
    }


def builtin_capability_sources() -> dict[str, dict[str, Any]]:
    return {
        "baoyu-skills": {
            "source_id": "baoyu-skills",
            "kind": "external-governed-source",
            "governance_status": "canonical-sample",
            "compatibility": {
                "admission_mode": "philosophy-first",
                "host_runtime": ["codex", "claude-code", "cursor", "trae"],
                "runtime_dependency_policy": "no_ungoverned_download",
            },
            "source_identity": {
                "label": "core-skills/baoyu-skills",
                "sample_origin": "oss-sync mirror core-skills/baoyu-skills",
            },
            "intended_domains": ["content", "operations", "cross-industry-analysis", "travel", "publishing"],
            "skill_philosophy": {
                "strategy_philosophy": [
                    "optimize for business outcome and result shape before choosing a skill chain",
                    "preserve domain strategy instead of collapsing everything into procedural scripts",
                ],
                "minimum_complete_tools": ["markdown", "image-generation", "formatting", "distribution"],
                "necessary_factual_grounding": [
                    "target audience",
                    "delivery channel",
                    "source material or policy facts",
                ],
            },
            "task_contracts": [
                {
                    "task_type": "content-outline",
                    "output_shape": "markdown-outline",
                    "skill_chain": ["baoyu-article-illustrator", "baoyu-format-markdown"],
                },
                {
                    "task_type": "travel-notice",
                    "output_shape": "wechat-post",
                    "skill_chain": ["baoyu-translate", "baoyu-post-to-wechat"],
                },
                {
                    "task_type": "industry-analysis",
                    "output_shape": "longform-markdown",
                    "skill_chain": ["baoyu-url-to-markdown", "baoyu-format-markdown"],
                },
            ],
            "boundary_contract": {
                "truth_boundary_preserved": True,
                "guidance_boundary_preserved": True,
                "runtime_boundary_preserved": True,
            },
        }
    }


def load_capability_sources(project_root: Path) -> dict[str, dict[str, Any]]:
    config = _load_config(project_root)
    section = _project_skills_section(config)
    registry = dict(builtin_capability_sources())
    external = section.get("capability_sources")
    if isinstance(external, dict):
        for source_id, payload in external.items():
            if not isinstance(payload, dict):
                continue
            merged = dict(payload)
            merged.setdefault("source_id", str(source_id))
            merged.setdefault("kind", "external-governed-source")
            merged.setdefault("governance_status", "project-local")
            merged.setdefault("compatibility", {})
            merged.setdefault("source_identity", {"label": str(source_id)})
            merged.setdefault("intended_domains", [])
            merged.setdefault("skill_philosophy", {})
            merged.setdefault("task_contracts", [])
            merged.setdefault(
                "boundary_contract",
                {
                    "truth_boundary_preserved": True,
                    "guidance_boundary_preserved": True,
                    "runtime_boundary_preserved": True,
                },
            )
            registry[str(source_id)] = merged
    return registry


def list_capability_sources(project_root: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for source_id, payload in sorted(load_capability_sources(project_root).items()):
        rows.append(
            {
                "source_id": source_id,
                "kind": str(payload.get("kind", "") or ""),
                "governance_status": str(payload.get("governance_status", "") or ""),
                "source_identity": dict(payload.get("source_identity", {})) if isinstance(payload.get("source_identity"), dict) else {},
                "compatibility": dict(payload.get("compatibility", {})) if isinstance(payload.get("compatibility"), dict) else {},
                "intended_domains": [str(item) for item in payload.get("intended_domains", []) if str(item).strip()],
                "task_contracts": list(payload.get("task_contracts", [])),
                "skill_philosophy": dict(payload.get("skill_philosophy", {})) if isinstance(payload.get("skill_philosophy"), dict) else {},
                "boundary_contract": dict(payload.get("boundary_contract", {})) if isinstance(payload.get("boundary_contract"), dict) else {},
            }
        )
    return rows


def _infer_task_type(goal: str, output_shape: str = "", explicit_task_type: str = "") -> str:
    if str(explicit_task_type or "").strip():
        return str(explicit_task_type).strip()
    text = " ".join([str(goal or ""), str(output_shape or "")]).lower()
    if any(token in text for token in ("travel", "airline", "ticket", "reminder", "notice", "航空", "出行")):
        return "travel-notice"
    if any(token in text for token in ("wechat", "weibo", "xhs", "post", "article", "outline", "blog")):
        return "content-outline"
    if any(token in text for token in ("strategy", "industry", "market", "analysis", "positioning")):
        return "industry-analysis"
    return "cross-domain-goal"


def select_capability_composition(
    project_root: Path,
    *,
    goal: str,
    output_shape: str = "",
    task_type: str = "",
) -> dict[str, Any]:
    inferred_task_type = _infer_task_type(goal, output_shape, explicit_task_type=task_type)
    registry = load_capability_sources(project_root)
    preferred = registry.get("baoyu-skills", {})
    selected_contract = next(
        (
            item
            for item in preferred.get("task_contracts", [])
            if isinstance(item, dict) and str(item.get("task_type", "") or "") == inferred_task_type
        ),
        None,
    )
    if not isinstance(selected_contract, dict):
        selected_contract = {
            "task_type": inferred_task_type,
            "output_shape": output_shape or "markdown",
            "skill_chain": ["baoyu-format-markdown"],
        }
    return {
        "schema_version": "1.0",
        "goal": str(goal or "").strip(),
        "task_type": inferred_task_type,
        "output_shape": str(selected_contract.get("output_shape") or output_shape or "markdown").strip(),
        "selected_source_id": "baoyu-skills",
        "candidate_skill_chain": list(selected_contract.get("skill_chain", [])),
        "source_governance_status": str(preferred.get("governance_status", "") or ""),
        "boundary_checks": dict(preferred.get("boundary_contract", {})) if isinstance(preferred.get("boundary_contract"), dict) else {},
        "selection_contract": {
            "user_declares_business_goal_not_chain": True,
            "source_identity": dict(preferred.get("source_identity", {})) if isinstance(preferred.get("source_identity"), dict) else {},
            "compatibility": dict(preferred.get("compatibility", {})) if isinstance(preferred.get("compatibility"), dict) else {},
        },
        "skill_philosophy": dict(preferred.get("skill_philosophy", {})) if isinstance(preferred.get("skill_philosophy"), dict) else {},
    }


def _append_jsonl(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(payload, ensure_ascii=False) + "\n")


def _read_capability_learning_events(project_root: Path) -> list[dict[str, Any]]:
    path = capability_learning_events_path(project_root)
    if not path.exists():
        return []
    rows: list[dict[str, Any]] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        text = line.strip()
        if not text:
            continue
        try:
            payload = json.loads(text)
        except json.JSONDecodeError:
            continue
        if isinstance(payload, dict):
            rows.append(payload)
    return rows


def refresh_capability_learning_map(project_root: Path) -> dict[str, Any]:
    events = _read_capability_learning_events(project_root)
    mappings: dict[tuple[str, str, str], dict[str, Any]] = {}
    for event in events:
        task_type = str(event.get("task_type", "") or "").strip()
        output_shape = str(event.get("output_shape", "") or "").strip()
        source_id = str(event.get("source_id", "") or "").strip()
        if not task_type or not output_shape or not source_id:
            continue
        chain = [str(item).strip() for item in event.get("skill_chain", []) if str(item).strip()]
        key = (task_type, ",".join(chain), output_shape)
        row = mappings.setdefault(
            key,
            {
                "task_type": task_type,
                "skill_chain": chain,
                "output_shape": output_shape,
                "source_id": source_id,
                "success_count": 0,
                "failure_count": 0,
                "fallback_count": 0,
                "adopted_count": 0,
                "rejected_count": 0,
                "event_refs": [],
            },
        )
        outcome = str(event.get("outcome", "") or "").strip()
        if outcome == "success":
            row["success_count"] += 1
        elif outcome == "failure":
            row["failure_count"] += 1
        elif outcome == "fallback":
            row["fallback_count"] += 1
        elif outcome == "adopted":
            row["adopted_count"] += 1
        elif outcome == "rejected":
            row["rejected_count"] += 1
        row["event_refs"].append(str(event.get("event_id", "") or ""))
    payload = {
        "schema_version": "1.0",
        "generated_at": now_iso(),
        "mappings": sorted(mappings.values(), key=lambda item: (item["task_type"], item["output_shape"], item["source_id"])),
    }
    write_json(capability_learning_map_path(project_root), payload)
    return payload


def write_capability_learning_event(
    project_root: Path,
    *,
    task_type: str,
    source_id: str,
    skill_chain: list[str],
    output_shape: str,
    outcome: str,
    fallback_path: str = "",
    human_adoption: str = "",
) -> dict[str, Any]:
    event = {
        "schema_version": "1.0",
        "event_id": generate_run_id("capability"),
        "generated_at": now_iso(),
        "task_type": str(task_type or "").strip(),
        "source_id": str(source_id or "").strip(),
        "skill_chain": [str(item).strip() for item in skill_chain if str(item).strip()],
        "output_shape": str(output_shape or "").strip(),
        "outcome": str(outcome or "").strip(),
        "fallback_path": str(fallback_path or "").strip(),
        "human_adoption": str(human_adoption or "").strip(),
    }
    _append_jsonl(capability_learning_events_path(project_root), event)
    refresh_capability_learning_map(project_root)
    return event


def load_capability_learning_map(project_root: Path) -> dict[str, Any]:
    payload = read_json(capability_learning_map_path(project_root), {})
    if isinstance(payload, dict) and payload:
        return payload
    return refresh_capability_learning_map(project_root)


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
            merged["supported_stages"] = _normalize_stage_list(list(merged.get("supported_stages", [])))
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
                "supported_stages": _normalize_stage_list(list(payload.get("supported_stages", []))),
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
                "supported_stages": ["qa", "release", "debug", "pipeline"],
                "evidence_contract": ["uat_pipeline_run", "gateway_smoke", "interface_response", "log_sql_snapshot"],
            }
        },
        "profiles": {
            "rolo-uat": {
                "project": "rolo",
                "profile_id": "rolo-uat",
                "description": "Rolo UAT multi-service verification profile.",
                "skills": {
                    "qa": "rolo-dev",
                    "release": "rolo-dev",
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
                            "stage": "qa",
                            "skill": "rolo-dev",
                            "command_template": "{skill_entry} pipeline --service {service_name}",
                            "produces_evidence": ["uat_pipeline_run"],
                        },
                        {
                            "id": "gateway-smoke",
                            "stage": "qa",
                            "skill": "rolo-dev",
                            "command_template": "{skill_entry} uat-smoke --jwt {jwt_token}",
                            "produces_evidence": ["gateway_smoke", "interface_response"],
                        },
                    ]
                },
            }
        },
    }


def _go_uniapp_profile_example(project: str, profile_id: str) -> dict[str, Any]:
    return {
        "project": project,
        "profile_id": profile_id,
        "description": "Go backend + UniApp frontend verification profile.",
        "skills": {},
        "required_evidence": [
            "go_backend_target_tests",
            "uniapp_typecheck",
            "miniapp_build",
            "route_check",
        ],
        "required_cases": [],
        "contracts": [],
        "qa_layer_commands": {
            "contract": "go test ./... -run '${BEACON_GO_TEST_PATTERN:-Test}'",
            "integration": "go test ./... -run '${BEACON_GO_TEST_PATTERN:-Test}'",
            "regression": "npm run test:routes --if-present",
            "functional": "npm run build:mp-weixin --if-present",
            "smoke": "npm run type-check --if-present",
            "unit": "go test ./...",
            "default": "go test ./...",
        },
        "runner_taxonomy": {
            "environment_blockers": ["docker", "testcontainers", "mysql", "postgres", "connection refused"],
            "runner_admission_blockers": ["missing script", "command not found", "no such file"],
            "auth_session_blockers": ["401", "403", "jwt", "cookie", "session"],
        },
        "orchestration": {"nodes": []},
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
    elif example in {"go-uniapp", "bmtop-go-uniapp"}:
        profiles = section.setdefault("profiles", {})
        if isinstance(profiles, dict):
            profiles[profile_id] = _go_uniapp_profile_example(project, profile_id)
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


def _truth_refs_for_feature(project_root: Path, *, version: str, feature: str) -> list[str]:
    slug = feature_slug(feature)
    refs: list[str] = []
    candidates = [
        project_root / "docs" / "beacon" / version / "prd" / f"{slug}.md",
        project_root / "docs" / "beacon" / version / "user-story" / f"{slug}.md",
        project_root / "docs" / "beacon" / version / "qa" / "test-cases" / f"{slug}.md",
    ]
    for path in candidates:
        if path.exists():
            refs.append(str(path.relative_to(project_root)))
    return refs


def _default_work_item_type(stage: str) -> str:
    normalized = _normalize_stage_name(stage)
    return {
        "implement": "implement_delivery",
        "qa": "qa_repair",
        "release": "release_closure",
        "debug": "ralph_step",
        "prototype": "team_task",
        "pipeline": "team_task",
    }.get(normalized, "team_task")


def _runtime_next_action(status: str) -> str:
    return {
        "queued": "dispatch",
        "running": "observe",
        "retry_waiting": "repair",
        "blocked": "repair",
        "handoff_required": "handoff",
        "completed": "close",
        "cancelled": "close",
    }.get(status, "observe")


def _runtime_board_summary(work_items: list[dict[str, Any]]) -> dict[str, Any]:
    counts: dict[str, int] = {}
    next_actions: list[str] = []
    for item in work_items:
        status = str(item.get("status") or "queued")
        counts[status] = counts.get(status, 0) + 1
        action = _runtime_next_action(status)
        if action not in next_actions:
            next_actions.append(action)
    return {
        "status_counts": counts,
        "running_runs": counts.get("running", 0),
        "retry_queue": counts.get("retry_waiting", 0),
        "blocked_runs": counts.get("blocked", 0),
        "handoff_runs": counts.get("handoff_required", 0),
        "completed_runs": counts.get("completed", 0),
        "next_actions": next_actions,
    }


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


def _stage_capabilities(stage: str) -> list[str]:
    normalized = _normalize_stage_name(stage)
    mapping = {
        "prototype": ["prototype"],
        "implement": ["implement", "implementation"],
        "qa": ["qa", "verify", "review", "gate"],
        "release": ["release", "delivery", "gate", "release-readiness"],
        "debug": ["debug"],
        "pipeline": ["pipeline"],
    }
    return mapping.get(normalized, [normalized] if normalized else [])


def _first_reason_code(issues: list[dict[str, Any]]) -> str:
    for item in issues:
        if not isinstance(item, dict):
            continue
        code = str(item.get("reason_code", "") or "").strip()
        if code:
            return code
    return ""


def _validate_orchestration_node(
    *,
    skill_payload: dict[str, Any],
    node: dict[str, Any],
) -> list[dict[str, Any]]:
    issues: list[dict[str, Any]] = []
    requested_stage = str(node.get("stage", "") or "").strip()
    node_stage = _normalize_stage_name(requested_stage)
    supported_stages = set(_normalize_stage_list(list(skill_payload.get("supported_stages", []))))
    capabilities = _expand_capabilities(list(skill_payload.get("capabilities", [])))
    evidence_contract = {str(item).strip() for item in skill_payload.get("evidence_contract", []) if str(item).strip()}
    entry = str(skill_payload.get("entry", "") or "").strip()

    if not node_stage or (supported_stages and node_stage not in supported_stages):
        issues.append(
            {
                "reason_code": "project_skill_stage_unsupported",
                "message": f"skill does not support stage `{node_stage or requested_stage or '-'}'",
                "stage": node_stage,
                "requested_stage": requested_stage,
                "supported_stages": sorted(supported_stages),
            }
        )
    required_capabilities = _stage_capabilities(node_stage)
    if required_capabilities and capabilities and not any(item in capabilities for item in required_capabilities):
        issues.append(
            {
                "reason_code": "project_skill_capability_missing",
                "message": f"skill capabilities {sorted(capabilities)} do not satisfy stage `{node_stage}`",
                "required_capabilities": required_capabilities,
            }
        )
    if not entry:
        issues.append(
            {
                "reason_code": "project_skill_entry_missing",
                "message": "skill entry is missing",
            }
        )

    missing_evidence = [
        key
        for key in node.get("produces_evidence", [])
        if str(key).strip() and str(key).strip() not in evidence_contract
    ]
    if missing_evidence:
        issues.append(
            {
                "reason_code": "project_skill_evidence_contract_mismatch",
                "message": f"node evidence is outside skill evidence contract: {missing_evidence}",
                "missing_evidence": missing_evidence,
                "evidence_contract": sorted(evidence_contract),
            }
        )

    produces_cases = [str(item).strip() for item in node.get("produces_cases", []) if str(item).strip()]
    if produces_cases and capabilities and not any(item in capabilities for item in {"verify", "qa"}):
        issues.append(
            {
                "reason_code": "project_skill_case_surface_unsupported",
                "message": f"skill capabilities {sorted(capabilities)} cannot produce verification cases",
                "produces_cases": produces_cases,
            }
        )
    return issues


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
    normalized_stage = _normalize_stage_name(stage)
    selected_nodes = [
        dict(node)
        for node in nodes
        if isinstance(node, dict) and (not normalized_stage or _normalize_stage_name(str(node.get("stage", "") or "")) == normalized_stage)
    ]
    run_id = generate_run_id(project_root)
    param_map = {str(k): str(v) for k, v in (params or {}).items()}
    node_results: list[dict[str, Any]] = []
    produced_evidence: list[dict[str, Any]] = []
    produced_cases: list[dict[str, Any]] = []
    truth_refs = _truth_refs_for_feature(project_root, version=resolved_version, feature=feature)
    work_items: list[dict[str, Any]] = []
    status = "completed"

    for node in selected_nodes:
        node_id = str(node.get("id", "") or f"node-{len(node_results)+1:03d}")
        node_stage = _normalize_stage_name(str(node.get("stage", "") or ""))
        item_id = f"{run_id}-{node_id}"
        profile_skills = profile.get("skills", {}) if isinstance(profile.get("skills"), dict) else {}
        skill_id = str(node.get("skill", "") or _resolve_profile_skill_id(profile_skills, node_stage) or "")
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
        work_item = {
            "item_id": item_id,
            "item_type": str(node.get("item_type") or _default_work_item_type(node_stage)),
            "feature": feature,
            "version": resolved_version,
            "source_surface": "project_profile_orchestration",
            "priority": str(node.get("priority") or "normal"),
            "requested_action": node_stage or "run",
            "truth_refs": truth_refs,
            "status": "queued" if dry_run else "running",
        }
        result_payload = {
            "node_id": node_id,
            "stage": node_stage,
            "skill_id": skill_id,
            "skill_kind": str(skill_payload.get("kind", "")),
            "command": command,
            "status": "planned" if dry_run else "pending",
            "work_item": work_item,
            "run_record": {
                "run_id": run_id,
                "item_id": item_id,
                "workspace_ref": str(project_root),
                "runtime_mode": "dry_run" if dry_run else "local_subprocess",
                "status": "queued" if dry_run else "running",
                "attempt_seq": 1,
                "next_action": "dispatch" if dry_run else "observe",
                "evidence_refs": [],
            },
            "evidence_path": str(_node_evidence_path(project_root, feature, run_id, node_id).relative_to(project_root)),
            "produces_evidence": list(node.get("produces_evidence", [])),
            "produces_cases": list(node.get("produces_cases", [])),
            "execution_boundary": {
                "mode": "validated_shell_template" if command_template else "missing_command_template",
                "skill_entry": skill_entry,
                "supported_stages": _normalize_stage_list(list(skill_payload.get("supported_stages", []))),
                "capabilities": list(skill_payload.get("capabilities", [])),
                "evidence_contract": list(skill_payload.get("evidence_contract", [])),
            },
        }
        work_items.append(work_item)

        node_issues = _validate_orchestration_node(skill_payload=skill_payload, node=node)
        if node_issues:
            result_payload["status"] = "blocked"
            result_payload["work_item"]["status"] = "blocked"
            result_payload["run_record"]["status"] = "blocked"
            result_payload["run_record"]["next_action"] = "repair"
            result_payload["issues"] = node_issues
            result_payload["reason_code"] = _first_reason_code(node_issues) or "project_skill_boundary_blocked"
            status = "blocked"
            write_json(_node_evidence_path(project_root, feature, run_id, node_id), result_payload)
            node_results.append(result_payload)
            break

        if dry_run:
            node_results.append(result_payload)
            continue

        if not command:
            result_payload["status"] = "blocked"
            result_payload["work_item"]["status"] = "blocked"
            result_payload["reason_code"] = "orchestration_command_missing"
            result_payload["run_record"]["status"] = "blocked"
            result_payload["run_record"]["next_action"] = "repair"
            status = "blocked"
            node_results.append(result_payload)
            break

        try:
            command_argv = shlex.split(command)
        except ValueError as exc:
            result_payload["status"] = "blocked"
            result_payload["work_item"]["status"] = "blocked"
            result_payload["run_record"]["status"] = "blocked"
            result_payload["run_record"]["next_action"] = "repair"
            result_payload["reason_code"] = "project_skill_command_parse_failed"
            result_payload["stderr"] = str(exc)
            status = "blocked"
            write_json(_node_evidence_path(project_root, feature, run_id, node_id), result_payload)
            node_results.append(result_payload)
            break
        if not command_argv:
            result_payload["status"] = "blocked"
            result_payload["work_item"]["status"] = "blocked"
            result_payload["run_record"]["status"] = "blocked"
            result_payload["run_record"]["next_action"] = "repair"
            result_payload["reason_code"] = "project_skill_command_parse_failed"
            result_payload["stderr"] = "empty argv after parsing"
            status = "blocked"
            write_json(_node_evidence_path(project_root, feature, run_id, node_id), result_payload)
            node_results.append(result_payload)
            break

        completed = subprocess.run(
            command_argv,
            cwd=project_root,
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
        result_payload["work_item"]["status"] = "completed" if completed.returncode == 0 else "blocked"
        result_payload["run_record"]["status"] = "completed" if completed.returncode == 0 else "blocked"
        result_payload["run_record"]["next_action"] = "close" if completed.returncode == 0 else "repair"
        result_payload["run_record"]["evidence_refs"] = [result_payload["evidence_path"]]
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
        "stage": normalized_stage or "",
        "status": "dry_run" if dry_run else status,
        "runtime_mode": "dry_run" if dry_run else "local_subprocess",
        "next_action": "dispatch" if dry_run else ("close" if status == "completed" else "repair" if status in {"failed", "blocked"} else "observe"),
        "generated_at": now_iso(),
        "truth_refs": truth_refs,
        "work_items": work_items,
        "runtime_board": _runtime_board_summary(work_items),
        "nodes": node_results,
        "produced_evidence": produced_evidence,
        "produced_cases": produced_cases,
        "required_evidence": list(profile.get("required_evidence", [])),
        "required_cases": list(profile.get("required_cases", [])),
    }
    if status == "blocked":
        summary["reason_code"] = _first_reason_code(
            [item for node in node_results for item in (node.get("issues") or []) if isinstance(item, dict)]
        ) or "project_skill_boundary_blocked"
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
    orchestration_nodes = orchestration.get("nodes") if isinstance(orchestration.get("nodes"), list) else []
    for node in orchestration_nodes:
        if not isinstance(node, dict):
            continue
        for item in node.get("issues", []):
            if isinstance(item, dict):
                issues.append(item)

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
