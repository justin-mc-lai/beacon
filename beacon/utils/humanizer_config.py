"""Humanizer runtime config resolve (v1.6.10).

default zh → oss-sync/core-skills/Humanizer-zh/SKILL.md
en → oss-sync/core-skills/humanizer/SKILL.md
Merge: global (~/.config/beacon/config.yaml) ⊕ project (beacon.config.yaml)
"""

from __future__ import annotations

import re

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


# Common AI-slop phrases (zh/en) — deterministic L0 polish without LLM.
_AI_SLOP_SUBS: list[tuple[re.Pattern[str], str]] = []


def _build_slop_subs() -> list[tuple["re.Pattern[str]", str]]:
    import re as _re

    pairs = [
        (r"标志着", "说明"),
        (r"赋能", "支持"),
        (r"在.*?的浪潮中", ""),
        (r"不仅.*?更是", "是"),
        (r"全方位", ""),
        (r"一站式", ""),
        (r"delve into", "look at"),
        (r"it's important to note that\s*", ""),
        (r"In conclusion,\s*", ""),
        (r"leverages?\s+", "uses "),
        (r"robust\s+", ""),
        (r"seamless\s+", ""),
        (r"cutting-edge\s+", ""),
    ]
    return [(_re.compile(p, _re.I), r) for p, r in pairs]


def _ensure_slop() -> list[tuple["re.Pattern[str]", str]]:
    global _AI_SLOP_SUBS
    if not _AI_SLOP_SUBS:
        _AI_SLOP_SUBS = _build_slop_subs()
    return _AI_SLOP_SUBS


def _extract_l0_section(body: str, headings: list[str]) -> tuple[str, str, str, str]:
    """Return (before, heading_line, l0_body, after)."""
    import re as _re

    lines = body.splitlines(keepends=True)
    start = -1
    heading_line = ""
    for i, line in enumerate(lines):
        for h in headings:
            if line.strip() == h or line.strip().startswith(h + " "):
                start = i
                heading_line = line
                break
        if start >= 0:
            break
    if start < 0:
        return body, "", "", ""
    end = len(lines)
    for j in range(start + 1, len(lines)):
        if lines[j].startswith("## ") and not any(
            lines[j].strip() == h or lines[j].strip().startswith(h + " ") for h in headings
        ):
            end = j
            break
    before = "".join(lines[:start])
    l0 = "".join(lines[start + 1 : end])
    after = "".join(lines[end:])
    return before, heading_line, l0, after


def polish_l0_text(l0_body: str, *, language: str = "zh", skill_text: str = "") -> str:
    """Deterministic L0 polish; skill_text is loaded for contract (agent/runtime context)."""
    _ = skill_text  # fulltext available to callers; apply uses rule set + structure
    text = l0_body
    for pat, rep in _ensure_slop():
        text = pat.sub(rep, text)
    # collapse multi-blank
    import re as _re

    text = _re.sub(r"\n{3,}", "\n\n", text).strip() + "\n"
    # Ensure 能做/不能做/怎样算完 or can/cannot/done when zh/en
    if language == "zh":
        needed = [("能做", "- 能做："), ("不能做", "- 不能做："), ("怎样算完", "- 怎样算完：")]
    else:
        needed = [("can:", "- can:"), ("cannot:", "- cannot:"), ("done when", "- done when:")]
    lower = text.lower()
    missing_lines = []
    for key, bullet in needed:
        if key not in text and key.lower() not in lower:
            missing_lines.append(bullet + " （待补）" if language == "zh" else bullet + " (TBD)")
    if missing_lines:
        text = text.rstrip() + "\n\n" + "\n".join(missing_lines) + "\n"
    return text


def apply_humanizer_l0(
    truth_md: str,
    *,
    profile: dict[str, Any] | None = None,
    language: str | None = None,
) -> dict[str, Any]:
    """Rewrite L0 (人话 / Plain language) only; preserve machine fields outside L0.

    Does not modify frontmatter tables for AC/FSM/Matrix when preserve_machine_fields.
    """
    import re as _re

    prof = profile or {}
    lang = (language or str(prof.get("language") or "zh")).strip().lower()
    if lang in {"zh-cn", "zh_cn", "chinese"}:
        lang = "zh"
    if lang in {"en-us", "en_us", "english"}:
        lang = "en"
    preserve = bool(prof.get("preserve_machine_fields", True))
    headings = ["## 人话", "## Plain language"]
    if lang == "en":
        headings = ["## Plain language", "## 人话"]
    fm_match = _re.match(r"\A---\n.*?\n---\n?", truth_md, _re.S)
    if fm_match:
        fm = fm_match.group(0)
        body = truth_md[fm_match.end() :]
    else:
        fm = ""
        body = truth_md
    before, heading_line, l0, after = _extract_l0_section(body, headings)
    if not heading_line:
        return {
            "applied": False,
            "reason_code": "l0_section_missing",
            "truth_md": truth_md,
            "language": lang,
        }
    polished = polish_l0_text(
        l0,
        language=lang if lang in {"zh", "en"} else "zh",
        skill_text=str(prof.get("skill_text") or ""),
    )
    new_body = before + heading_line
    if not heading_line.endswith("\n"):
        new_body += "\n"
    new_body += "\n" if not polished.startswith("\n") and not heading_line.endswith("\n\n") else ""
    # normalize single blank after heading
    new_body = before + heading_line.rstrip("\n") + "\n\n" + polished.lstrip("\n")
    if after and not after.startswith("\n") and not new_body.endswith("\n"):
        new_body += "\n"
    new_body += after if after.startswith("\n") or not after else "\n" + after
    new_md = fm + new_body
    # Safety: preserve machine field tables if preserve_machine_fields
    if preserve:
        for marker in (
            "## Intent Coverage Matrix",
            "## Acceptance Criteria",
            "## FSM",
            "### invalid",
            "materials_status:",
            "parser_contract:",
        ):
            if marker in truth_md and marker not in new_md:
                return {
                    "applied": False,
                    "reason_code": "preserve_machine_fields_failed",
                    "truth_md": truth_md,
                    "language": lang,
                }
    changed = new_md != truth_md
    # stamp humanizer note in frontmatter lightly
    if changed and fm and "humanizer_applied:" not in fm:
        fm2 = fm.rstrip()
        if fm2.endswith("---"):
            fm2 = fm2[:-3] + "humanizer_applied: true\n---\n"
            new_md = fm2 + new_body
    return {
        "applied": changed,
        "reason_code": "",
        "truth_md": new_md,
        "language": lang,
        "l0_chars_before": len(l0),
        "l0_chars_after": len(polished),
        "skill_path": prof.get("skill_path") or "",
        "skill_chars": prof.get("skill_chars") or len(str(prof.get("skill_text") or "")),
        "preserve_machine_fields": preserve,
    }


def apply_humanizer_l0_to_path(
    project_root: Path,
    *,
    version: str,
    feature: str,
    profile: dict[str, Any] | None = None,
    language: str | None = None,
) -> dict[str, Any]:
    """Load profile if needed, apply L0 polish to features/<slug>/truth.md."""
    from beacon.utils.feature_package import package_paths
    from beacon.utils.story_state import feature_slug as _slug
    from beacon.utils.versioning import resolve_target_version

    root = Path(project_root).expanduser().resolve()
    resolved = resolve_target_version(root, version)
    slug = _slug(feature)
    paths = package_paths(root, version=resolved, feature=slug)
    truth_path = paths["truth"]
    if not truth_path.is_file():
        return {"applied": False, "reason_code": "truth_missing", "path": str(truth_path)}
    prof = profile if isinstance(profile, dict) else resolve_humanizer_profile(root, language=language)
    original = truth_path.read_text(encoding="utf-8")
    result = apply_humanizer_l0(original, profile=prof, language=language or prof.get("language"))
    if result.get("applied") and result.get("truth_md"):
        truth_path.write_text(str(result["truth_md"]), encoding="utf-8")
    result["path"] = str(truth_path)
    result["version"] = resolved
    result["feature"] = slug
    return result
