"""Starter-pack template loading for Beacon project-skill discovery."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from beacon.utils.project_skills import project_skill_config_path
from beacon.utils.skill_config import load_yaml_like


def builtin_template_dir() -> Path:
    return Path(__file__).resolve().parents[1] / "templates" / "skill_profiles"


def configured_template_dirs(project_root: Path) -> list[Path]:
    config_path = project_skill_config_path(project_root)
    config = load_yaml_like(config_path) if config_path.exists() else {}
    project_skills = config.get("project_skills") if isinstance(config.get("project_skills"), dict) else {}
    discovery = project_skills.get("discovery") if isinstance(project_skills.get("discovery"), dict) else {}
    dirs = discovery.get("template_dirs") if isinstance(discovery.get("template_dirs"), list) else []
    out: list[Path] = []
    for item in dirs:
        text = str(item or "").strip()
        if not text:
            continue
        path = Path(text)
        if not path.is_absolute():
            path = project_root / text
        out.append(path)
    return out


def load_skill_template(project_root: Path, template_id: str) -> dict[str, Any] | None:
    return load_skill_templates(project_root).get(str(template_id or "").strip())


def list_skill_templates(project_root: Path) -> list[dict[str, Any]]:
    return list(load_skill_templates(project_root).values())


def load_skill_templates(project_root: Path) -> dict[str, dict[str, Any]]:
    templates: dict[str, dict[str, Any]] = {}
    seen_dirs: set[Path] = set()
    for directory in [builtin_template_dir(), *configured_template_dirs(project_root)]:
        if not directory.exists():
            continue
        resolved = directory.resolve()
        if resolved in seen_dirs:
            continue
        seen_dirs.add(resolved)
        for path in sorted(directory.glob("*.yaml")):
            payload = load_yaml_like(path)
            if not isinstance(payload, dict):
                continue
            nested_template = payload.get("template") if isinstance(payload.get("template"), dict) else {}
            template_id = str(nested_template.get("id") or payload.get("template_id") or path.stem).strip()
            if not template_id:
                continue
            item = dict(payload)
            if nested_template:
                for key in ("description", "project_types", "languages", "frameworks"):
                    if key not in item and key in nested_template:
                        item[key] = nested_template.get(key)
            item["id"] = template_id
            item.setdefault("template_id", template_id)
            item.setdefault("description", "")
            item.setdefault("project_types", [])
            item.setdefault("languages", [])
            item.setdefault("frameworks", [])
            project_skills = item.get("project_skills") if isinstance(item.get("project_skills"), dict) else {}
            profiles = project_skills.get("profiles") if isinstance(project_skills.get("profiles"), dict) else {}
            first_profile = next(iter(profiles.values()), {}) if profiles else {}
            first_profile_id = next(iter(profiles.keys()), "") if profiles else ""
            item.setdefault("recommended_profile_id", str(item.get("recommended_profile_id") or first_profile_id))
            item.setdefault("recommended_skills", first_profile.get("skills", {}) if isinstance(first_profile, dict) else {})
            item.setdefault("project_skills", project_skills)
            item["_path"] = str(path)
            item["_builtin"] = resolved == builtin_template_dir().resolve()
            templates[template_id] = item
    return templates


def render_template_project_skills(template_payload: dict[str, Any], *, context: dict[str, str]) -> dict[str, Any]:
    def _render(value: Any) -> Any:
        if isinstance(value, str):
            rendered = value
            for key, raw in context.items():
                rendered = rendered.replace("{" + key + "}", str(raw))
            return rendered
        if isinstance(value, list):
            return [_render(item) for item in value]
        if isinstance(value, dict):
            return {str(key): _render(item) for key, item in value.items()}
        return value

    source = template_payload.get("project_skills") if isinstance(template_payload.get("project_skills"), dict) else {}
    return _render(source)
