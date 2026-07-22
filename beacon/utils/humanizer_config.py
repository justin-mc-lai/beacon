"""Humanizer runtime config resolve (v1.6.10).

default zh → oss-sync/core-skills/Humanizer-zh/SKILL.md
en → oss-sync/core-skills/humanizer/SKILL.md
Merge: global (~/.config/beacon/config.yaml) ⊕ project (beacon.config.yaml)
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any

from beacon.utils.implement_adapters import load_beacon_config

REASON_HUMANIZER_PATH_MISSING = "humanizer_skill_path_missing"
REASON_HUMANIZER_PROFILE_MISSING = "humanizer_profile_missing"

DEFAULT_REL_ZH = "core-skills/Humanizer-zh/SKILL.md"
DEFAULT_REL_EN = "core-skills/humanizer/SKILL.md"


def _candidate_oss_sync_roots(project_root: Path) -> list[Path]:
    roots: list[Path] = []
    env = os.environ.get("BEACON_OSS_SYNC_ROOT") or os.environ.get("OSS_SYNC_ROOT")
    if env:
        roots.append(Path(env).expanduser())
    # sibling of products/beacon → Personal/oss-sync
    roots.append(project_root / "oss-sync")
    roots.append(project_root.parent / "oss-sync")
    roots.append(project_root.parent.parent / "oss-sync")
    # known personal layout
    roots.append(Path.home() / "Developer" / "Personal" / "oss-sync")
    # de-dupe
    seen: set[str] = set()
    out: list[Path] = []
    for r in roots:
        key = str(r.resolve()) if r.exists() else str(r)
        if key in seen:
            continue
        seen.add(key)
        out.append(r)
    return out


def default_humanizer_block(project_root: Path) -> dict[str, Any]:
    zh_path = ""
    en_path = ""
    for root in _candidate_oss_sync_roots(project_root):
        zh = root / DEFAULT_REL_ZH
        en = root / DEFAULT_REL_EN
        if not zh_path and zh.is_file():
            zh_path = str(zh.resolve())
        if not en_path and en.is_file():
            en_path = str(en.resolve())
        if zh_path and en_path:
            break
    if not zh_path:
        zh_path = str((project_root / "oss-sync" / DEFAULT_REL_ZH))
    if not en_path:
        en_path = str((project_root / "oss-sync" / DEFAULT_REL_EN))
    return {
        "default_language": "zh",
        "require_on_truth_write": True,
        "preserve_machine_fields": True,
        "profiles": {
            "zh": {
                "skill_path": zh_path,
                "l0_heading": "## 人话",
            },
            "en": {
                "skill_path": en_path,
                "l0_heading": "## Plain language",
            },
        },
    }


def resolve_humanizer_config(project_root: Path) -> dict[str, Any]:
    """Merge defaults ⊕ load_beacon_config humanizer block."""
    root = Path(project_root).expanduser().resolve()
    base = default_humanizer_block(root)
    cfg = load_beacon_config(root)
    override = cfg.get("humanizer") if isinstance(cfg.get("humanizer"), dict) else {}
    if not override:
        return base
    out = dict(base)
    for key, value in override.items():
        if key == "profiles" and isinstance(value, dict):
            profiles = dict(out.get("profiles") or {})
            for lang, prof in value.items():
                if not isinstance(prof, dict):
                    continue
                merged = dict(profiles.get(lang) or {})
                merged.update(prof)
                profiles[lang] = merged
            out["profiles"] = profiles
        else:
            out[key] = value
    return out


def resolve_humanizer_profile(
    project_root: Path,
    *,
    language: str | None = None,
) -> dict[str, Any]:
    """Resolve active profile + load skill path existence."""
    root = Path(project_root).expanduser().resolve()
    config = resolve_humanizer_config(root)
    lang = (language or str(config.get("default_language") or "zh")).strip().lower()
    if lang in {"zh-cn", "zh_cn", "chinese"}:
        lang = "zh"
    if lang in {"en-us", "en_us", "english"}:
        lang = "en"
    profiles = config.get("profiles") if isinstance(config.get("profiles"), dict) else {}
    profile = profiles.get(lang) if isinstance(profiles.get(lang), dict) else None
    if profile is None and lang == "bilingual":
        # bilingual → return zh as primary; caller may load both
        profile = profiles.get("zh") if isinstance(profiles.get("zh"), dict) else None
        lang = "zh"
    if not isinstance(profile, dict):
        return {
            "ok": False,
            "blocked": bool(config.get("require_on_truth_write", True)),
            "reason_code": REASON_HUMANIZER_PROFILE_MISSING,
            "language": lang,
            "config": config,
            "skill_path": "",
            "skill_exists": False,
            "skill_text": "",
            "l0_heading": "",
            "preserve_machine_fields": bool(config.get("preserve_machine_fields", True)),
        }
    skill_path_raw = str(profile.get("skill_path") or "").strip()
    skill_path = Path(skill_path_raw).expanduser()
    if not skill_path.is_absolute():
        skill_path = (root / skill_path).resolve()
    exists = skill_path.is_file()
    skill_text = skill_path.read_text(encoding="utf-8") if exists else ""
    require = bool(config.get("require_on_truth_write", True))
    ok = exists or not require
    return {
        "ok": ok,
        "blocked": (not exists) and require,
        "reason_code": "" if ok else REASON_HUMANIZER_PATH_MISSING,
        "language": lang,
        "config": config,
        "skill_path": str(skill_path),
        "skill_exists": exists,
        "skill_text": skill_text,
        "skill_chars": len(skill_text),
        "l0_heading": str(profile.get("l0_heading") or ("## 人话" if lang == "zh" else "## Plain language")),
        "preserve_machine_fields": bool(config.get("preserve_machine_fields", True)),
        "require_on_truth_write": require,
    }


def humanizer_ready_after_gate(gate_payload: dict[str, Any], profile: dict[str, Any]) -> dict[str, Any]:
    """Humanizer may run only after A/B/C pass (ordering contract)."""
    abc_pass = bool(gate_payload.get("review_gate_pass") or gate_payload.get("pass"))
    return {
        "allowed": abc_pass and bool(profile.get("ok")),
        "abc_pass": abc_pass,
        "profile_ok": bool(profile.get("ok")),
        "reason_code": (
            ""
            if abc_pass and profile.get("ok")
            else ("truth_review_gate_failed" if not abc_pass else profile.get("reason_code") or "humanizer_not_ready")
        ),
        "language": profile.get("language"),
        "skill_path": profile.get("skill_path"),
    }
