"""Project skill discovery for Beacon v1.2.0."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from beacon.utils.memory import memory_v1_path
from beacon.utils.project_analyzer import analyze_project
from beacon.utils.project_skills import load_project_profiles, load_skill_registry, project_skill_config_path
from beacon.utils.runtime import now_iso
from beacon.utils.skill_config import load_yaml_like, write_yaml_like
from beacon.utils.skill_templates import builtin_template_dir, list_skill_templates, load_skill_template, render_template_project_skills


def skill_discovery_state_dir(project_root: Path) -> Path:
    return project_root.resolve() / ".beacon" / "state" / "skill-discovery"


def skill_discovery_state_path(project_root: Path, target: str | None = None) -> Path:
    root = project_root.resolve()
    name = str(target or root.name or "project").strip().lower().replace(" ", "-")
    return skill_discovery_state_dir(root) / f"{name}.json"


def load_skill_discovery(project_root: Path, target: str | None = None) -> dict[str, Any] | None:
    path = skill_discovery_state_path(project_root, target)
    if not path.exists():
        return None
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except Exception:  # noqa: BLE001
        return None
    return payload if isinstance(payload, dict) else None


def _memory_signals(project_root: Path) -> list[str]:
    path = memory_v1_path(project_root)
    if not path.exists():
        return []
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except Exception:  # noqa: BLE001
        return []
    items = payload.get("items") if isinstance(payload, dict) else []
    tokens: list[str] = []
    for item in items if isinstance(items, list) else []:
        if not isinstance(item, dict):
            continue
        text = str(item.get("content", "") or "")
        tokens.extend(part.strip().lower() for part in text.replace("\n", " ").split(" ") if part.strip())
        for tag in item.get("tags", []) if isinstance(item.get("tags"), list) else []:
            tag_text = str(tag or "").strip().lower()
            if tag_text:
                tokens.append(tag_text)
    return tokens


def _deep_merge(base: Any, override: Any) -> Any:
    if isinstance(base, dict) and isinstance(override, dict):
        merged = {str(key): value for key, value in base.items()}
        for key, value in override.items():
            if key in merged:
                merged[key] = _deep_merge(merged[key], value)
            else:
                merged[key] = value
        return merged
    if isinstance(base, list) and isinstance(override, list):
        out = list(base)
        for item in override:
            if item not in out:
                out.append(item)
        return out
    return override


def _score_template(template: dict[str, Any], features: dict[str, Any], *, memory_signals: list[str] | None = None) -> tuple[float, list[str]]:
    score = 0.0
    reasons: list[str] = []
    feature_types = {
        str(item)
        for item in (
            features.get("top_project_types")
            if isinstance(features.get("top_project_types"), list)
            else features.get("project_types", [])
        )
    }
    languages = {str(item) for item in features.get("languages", [])}
    frameworks = {str(item) for item in features.get("frameworks", [])}
    template_types = {str(item) for item in template.get("project_types", []) if str(item).strip()}
    template_languages = {str(item) for item in template.get("languages", []) if str(item).strip()}
    template_frameworks = {str(item) for item in template.get("frameworks", []) if str(item).strip()}

    matched_types = sorted(feature_types & template_types)
    matched_languages = sorted(languages & template_languages)
    matched_frameworks = sorted(frameworks & template_frameworks)
    if matched_types:
        score += 0.7 + 0.1 * len(matched_types)
        reasons.append(f"project type match: {', '.join(matched_types)}")
    if matched_languages:
        score += 0.2 * len(matched_languages)
        reasons.append(f"language match: {', '.join(matched_languages)}")
    if matched_frameworks:
        score += 0.15 * len(matched_frameworks)
        reasons.append(f"framework match: {', '.join(matched_frameworks)}")
    if bool(features.get("tests_present")):
        score += 0.05
        reasons.append("tests detected")
    if bool(features.get("docker_present")):
        score += 0.03
        reasons.append("docker/deploy artifacts detected")
    if memory_signals:
        template_id = str(template.get("id", "") or "")
        recommended_skills = template.get("recommended_skills") if isinstance(template.get("recommended_skills"), dict) else {}
        if template_id in memory_signals or any(str(skill_id).lower() in memory_signals for skill_id in recommended_skills.values()):
            score += 0.15
            reasons.append("memory history references this template or its skills")
    return round(score, 3), reasons


def build_skill_discovery_payload(
    project_root: Path,
    *,
    template_id: str | None = None,
    from_memory: bool = False,
    profile_id: str | None = None,
    persist: bool = False,
) -> dict[str, Any]:
    project_root = project_root.resolve()
    features = analyze_project(project_root)
    signals = _memory_signals(project_root) if from_memory else []
    available_templates = list_skill_templates(project_root)
    ranked: list[dict[str, Any]] = []
    selected_template_id = str(template_id or "").strip()
    for item in available_templates:
        if selected_template_id and str(item.get("id", "")) != selected_template_id:
            continue
        score, reasons = _score_template(item, features, memory_signals=signals)
        if selected_template_id and str(item.get("id", "")) == selected_template_id:
            score = max(score, 1.0)
            reasons = reasons + ["explicit template override selected"]
        if score <= 0 and not selected_template_id:
            continue
        ranked.append({**item, "score": score, "reasons": reasons or ["starter-pack fallback"]})
    ranked.sort(key=lambda item: (-float(item.get("score", 0.0)), str(item.get("id", ""))))
    selected = ranked[0] if ranked else None
    selected_template = load_skill_template(project_root, str(selected.get("id", ""))) if selected else None

    recommended_profile_id = str(profile_id or (selected.get("recommended_profile_id", "") if selected else "") or f"{project_root.name}-default").strip()
    context = {
        "project_name": project_root.name,
        "project_root": str(project_root),
        "profile_id": recommended_profile_id,
        "feature_name": project_root.name,
        "version": "auto",
    }

    proposed_config: dict[str, Any] = {"project_skills": {"discovery": {"preferred_templates": [], "recommendation_policy": "auto", "memory_enabled": bool(from_memory), "template_dirs": []}}}
    if selected_template:
        rendered = render_template_project_skills(selected_template, context=context)
        profiles = rendered.get("profiles") if isinstance(rendered.get("profiles"), dict) else {}
        if profiles:
            first_key = next(iter(profiles.keys()), "")
            if first_key and first_key != recommended_profile_id:
                profiles[recommended_profile_id] = profiles.pop(first_key)
            if isinstance(profiles.get(recommended_profile_id), dict):
                profiles[recommended_profile_id]["profile_id"] = recommended_profile_id
                profiles[recommended_profile_id]["project"] = project_root.name
            rendered["profiles"] = profiles
        rendered["default_profile"] = recommended_profile_id
        proposed_config["project_skills"] = _deep_merge(proposed_config["project_skills"], rendered)
        proposed_config["project_skills"]["discovery"]["preferred_templates"] = [str(selected_template.get("id", ""))]
        template_parent = Path(str(selected_template.get("_path", ""))).parent
        if template_parent and template_parent.resolve() != builtin_template_dir().resolve():
            proposed_config["project_skills"]["discovery"]["template_dirs"] = [str(template_parent)]

    registry = load_skill_registry(project_root)
    recommended_skills: list[dict[str, Any]] = []
    selected_skill_map = selected.get("recommended_skills") if selected and isinstance(selected.get("recommended_skills"), dict) else {}
    for stage, skill_id in selected_skill_map.items():
        skill_payload = registry.get(str(skill_id), {})
        recommended_skills.append(
            {
                "stage": str(stage),
                "skill_id": str(skill_id),
                "capabilities": list(skill_payload.get("capabilities", [])) if isinstance(skill_payload, dict) else [],
                "supported_stages": list(skill_payload.get("supported_stages", [])) if isinstance(skill_payload, dict) else [],
            }
        )

    payload = {
        "schema_version": "1.0",
        "generated_at": now_iso(),
        "status": "applied" if False else "preview",
        "project_root": str(project_root),
        "project_name": project_root.name,
        "project_features": features,
        "memory": {"enabled": bool(from_memory), "signals": signals},
        "available_templates": ranked,
        "selected_template": str(selected.get("id", "") if selected else ""),
        "recommended_templates": ranked[:3],
        "recommended_profile_id": recommended_profile_id,
        "recommended_skills": recommended_skills,
        "source_evidence": list(features.get("source_evidence", features.get("evidence", []))),
        "config_diff": proposed_config,
        "applied": False,
        "config_path": str(project_skill_config_path(project_root).relative_to(project_root)),
    }
    if selected_template:
        payload["template_path"] = str(selected_template.get("_path", ""))
    if persist:
        write_skill_discovery_state(project_root, payload)
    return payload


def apply_skill_discovery(project_root: Path, payload: dict[str, Any]) -> dict[str, Any]:
    project_root = project_root.resolve()
    config_path = project_skill_config_path(project_root)
    config = load_yaml_like(config_path) if config_path.exists() else {}
    proposed = payload.get("config_diff") if isinstance(payload.get("config_diff"), dict) else {}
    merged = _deep_merge(config, proposed)
    write_yaml_like(config_path, merged)

    updated = dict(payload)
    updated["status"] = "applied"
    updated["applied"] = True
    updated["applied_at"] = now_iso()
    updated["config_path"] = str(config_path.relative_to(project_root))
    return updated


def write_skill_discovery_state(project_root: Path, payload: dict[str, Any], *, target: str | None = None) -> Path:
    project_root = project_root.resolve()
    path = skill_discovery_state_path(project_root, target)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return path


def validate_skill_discovery_payload(project_root: Path, payload: dict[str, Any]) -> list[str]:
    issues: list[str] = []
    if not isinstance(payload.get("project_features"), dict):
        issues.append("project_features missing")
    if not isinstance(payload.get("recommended_templates"), list):
        issues.append("recommended_templates missing")
    if not isinstance(payload.get("recommended_skills"), list):
        issues.append("recommended_skills missing")
    template_id = str(payload.get("selected_template", "") or "")
    if template_id and not load_skill_template(project_root, template_id):
        issues.append(f"template missing: {template_id}")
    if payload.get("applied"):
        config = load_yaml_like(project_skill_config_path(project_root))
        project_skills = config.get("project_skills") if isinstance(config.get("project_skills"), dict) else {}
        profiles = project_skills.get("profiles") if isinstance(project_skills.get("profiles"), dict) else {}
        profile_id = str(payload.get("recommended_profile_id", "") or "")
        if profile_id and profile_id not in profiles:
            issues.append(f"applied profile missing: {profile_id}")
        preferred_templates = project_skills.get("discovery", {}).get("preferred_templates", []) if isinstance(project_skills.get("discovery"), dict) else []
        if template_id and template_id not in preferred_templates:
            issues.append(f"preferred template missing: {template_id}")
    return issues


def build_discovery_hint(project_root: Path, *, target: str | None = None) -> dict[str, Any]:
    project_root = project_root.resolve()
    config_path = project_skill_config_path(project_root)
    config = load_yaml_like(config_path) if config_path.exists() else {}
    project_skills = config.get("project_skills") if isinstance(config.get("project_skills"), dict) else {}
    if isinstance(project_skills.get("profiles"), dict) and project_skills.get("profiles"):
        return {
            "recommended": False,
            "reason": "project profiles are already configured",
            "command": "",
            "templates": [],
            "state_path": str(skill_discovery_state_path(project_root, target).relative_to(project_root)),
            "source": "config",
        }
    state = load_skill_discovery(project_root, target)
    if state and state.get("recommended_templates"):
        return {
            "recommended": True,
            "reason": "project-skill discovery preview is available and no profile is bound yet",
            "command": f"beacon skill discover --project-root {project_root} --dry-run",
            "templates": [item.get("id") or item.get("template_id") for item in state.get("recommended_templates", []) if isinstance(item, dict)],
            "state_path": str(skill_discovery_state_path(project_root, target).relative_to(project_root)),
            "source": "state",
        }
    preview = build_skill_discovery_payload(project_root, persist=False)
    return {
        "recommended": bool(preview.get("recommended_templates")),
        "reason": "project shows detectable structure that can be bound into Beacon project-skill workflow" if preview.get("recommended_templates") else "no project-skill starter template matched strongly enough",
        "command": f"beacon skill discover --project-root {project_root} --dry-run" if preview.get("recommended_templates") else "",
        "templates": [item.get("id") or item.get("template_id") for item in preview.get("recommended_templates", []) if isinstance(item, dict)],
        "state_path": str(skill_discovery_state_path(project_root, target).relative_to(project_root)),
        "source": "live-analysis",
    }
