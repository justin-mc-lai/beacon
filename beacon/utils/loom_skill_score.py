"""Score Loom skill packages accurately (structure + content-source fidelity).

Loom skills under skills/loom/loom-* are brand surfaces; CONTENT_SOURCE points
to skills/beacon/* single source. Scoring must:
- credit valid facade + pointer (not punish for thin SKILL.md)
- score content package structure via the source
- never treat loom skill as incomplete solely because body is a router
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any

SCHEMA = "loom-skill-score.v1"
REASON_MISSING = "loom_skill_missing"
REASON_SOURCE_MISSING = "loom_content_source_missing"
REASON_BRAND_DRIFT = "loom_skill_brand_drift"

_PUBLIC_PRIMARY = frozenset({"loom-goal"})
_SUPPORT_ONLY = frozenset({"loom-loop-goal"})


def _read(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except OSError:
        return ""


def _parse_frontmatter(text: str) -> dict[str, str]:
    out: dict[str, str] = {}
    if not text.lstrip().startswith("---"):
        return out
    parts = text.split("---", 2)
    if len(parts) < 3:
        return out
    for line in parts[1].splitlines():
        if ":" not in line:
            continue
        k, v = line.split(":", 1)
        out[k.strip()] = v.strip().strip('"').strip("'")
    return out


def resolve_content_source(project_root: Path, skill_dir: Path) -> dict[str, Any]:
    pointer = skill_dir / "CONTENT_SOURCE"
    skill_md = skill_dir / "SKILL.md"
    text = _read(skill_md)
    fm = _parse_frontmatter(text)
    source_rel = ""
    if pointer.exists():
        source_rel = _read(pointer).strip().splitlines()[0].strip() if _read(pointer).strip() else ""
    if not source_rel:
        # try metadata / body
        source_rel = fm.get("content_source") or ""
        m = re.search(r"skills/beacon/[a-z0-9._-]+", text)
        if not source_rel and m:
            source_rel = m.group(0)
    source_path = (project_root / source_rel) if source_rel else None
    exists = bool(source_path and source_path.is_dir() and (source_path / "SKILL.md").is_file())
    return {
        "content_source": source_rel,
        "content_source_path": str(source_path) if source_path else "",
        "content_source_exists": exists,
        "frontmatter": fm,
    }


def _structure_points(skill_name: str, skill_md: str, fm: dict[str, str], source: dict[str, Any]) -> tuple[float, list[str]]:
    score = 0.0
    notes: list[str] = []
    if fm.get("name") == skill_name or skill_name in skill_md:
        score += 15
        notes.append("name_present")
    if "Loom" in skill_md or fm.get("brand") == "Loom" or "brand: Loom" in skill_md:
        score += 15
        notes.append("brand_loom")
    else:
        notes.append("brand_missing")
    if source.get("content_source") or skill_name in _PUBLIC_PRIMARY:
        score += 20
        notes.append("content_source_declared")
    if source.get("content_source_exists") or skill_name in _PUBLIC_PRIMARY:
        score += 25
        notes.append("content_source_resolves")
    elif skill_name not in _PUBLIC_PRIMARY:
        notes.append("content_source_broken")
    # dual-install / no replace
    if any(x in skill_md for x in ("不覆盖", "dual-install", "dual_install", "禁止", "does not replace", "不得")):
        score += 10
        notes.append("dual_install_stated")
    # entry class
    if skill_name in _PUBLIC_PRIMARY and ("public" in skill_md.lower() or "公共" in skill_md):
        score += 10
        notes.append("public_entry_marked")
    elif skill_name in _SUPPORT_ONLY and ("support" in skill_md.lower() or "support only" in skill_md.lower()):
        score += 10
        notes.append("support_entry_marked")
    elif skill_name not in _PUBLIC_PRIMARY and skill_name not in _SUPPORT_ONLY:
        score += 5
        notes.append("progressive_surface")
    return min(score, 100.0), notes


def _content_structure_points(source_skill_md: str) -> tuple[float, list[str]]:
    """Lightweight structure of content package (not rewriting source)."""
    score = 0.0
    notes: list[str] = []
    if not source_skill_md.strip():
        return 0.0, ["source_empty"]
    if source_skill_md.lstrip().startswith("---"):
        score += 20
        notes.append("source_frontmatter")
    if re.search(r"^#\s+\S+", source_skill_md, re.M):
        score += 20
        notes.append("source_title")
    # meaningful body
    body_len = len(source_skill_md.strip())
    if body_len >= 200:
        score += 30
        notes.append("source_body_substantial")
    elif body_len >= 80:
        score += 15
        notes.append("source_body_minimal")
    if any(k in source_skill_md.lower() for k in ("hard", "禁止", "must", "rule", "gate")):
        score += 15
        notes.append("source_rules_signal")
    if "```" in source_skill_md or "beacon" in source_skill_md.lower() or "loom" in source_skill_md.lower():
        score += 15
        notes.append("source_usage_signal")
    return min(score, 100.0), notes


def score_loom_skill(project_root: Path, skill_name: str) -> dict[str, Any]:
    project_root = Path(project_root).expanduser().resolve()
    name = str(skill_name or "").strip()
    if name and not name.startswith("loom-") and name != "loom":
        # allow bare name
        if (project_root / "skills" / "loom" / f"loom-{name}").is_dir():
            name = f"loom-{name}"
    skill_dir = project_root / "skills" / "loom" / (name if name != "loom" else "")
    if name == "loom":
        skill_dir = project_root / "skills" / "loom"
    if not skill_dir.is_dir() or not (skill_dir / "SKILL.md").is_file():
        return {
            "schema": SCHEMA,
            "skill": name,
            "ok": False,
            "blocked": True,
            "reason_code": REASON_MISSING,
            "scores": {},
        }

    skill_md = _read(skill_dir / "SKILL.md")
    source = resolve_content_source(project_root, skill_dir)
    facade_score, facade_notes = _structure_points(name if name != "loom" else "loom", skill_md, source.get("frontmatter") or {}, source)

    content_score = 100.0 if name in _PUBLIC_PRIMARY and not source.get("content_source") else 0.0
    content_notes: list[str] = []
    if source.get("content_source_exists"):
        content_md = _read(Path(source["content_source_path"]) / "SKILL.md")
        content_score, content_notes = _content_structure_points(content_md)
    elif name in _PUBLIC_PRIMARY:
        content_score, content_notes = _content_structure_points(skill_md)
        content_notes.append("public_entry_self_contained_ok")

    # composite: facade 40% + content 60% (accurate for thin loom wrappers)
    if name == "loom":
        composite = facade_score
    else:
        composite = round(0.4 * facade_score + 0.6 * content_score, 2)

    brand_ok = "Loom" in skill_md or "brand: Loom" in skill_md or name == "loom"
    findings = []
    if not brand_ok:
        findings.append({"reason_code": REASON_BRAND_DRIFT, "text": "SKILL.md missing Loom brand"})
    if name not in _PUBLIC_PRIMARY and name != "loom" and not source.get("content_source_exists"):
        findings.append({"reason_code": REASON_SOURCE_MISSING, "text": "CONTENT_SOURCE missing or broken"})

    grade = (
        "A" if composite >= 85 else
        "B" if composite >= 70 else
        "C" if composite >= 55 else
        "D" if composite >= 40 else
        "F"
    )
    return {
        "schema": SCHEMA,
        "skill": name if name != "loom" else "loom",
        "ok": not findings or composite >= 55,
        "blocked": bool(findings) and composite < 55,
        "reason_code": findings[0]["reason_code"] if findings and composite < 55 else "",
        "scores": {
            "facade_structure": facade_score,
            "content_structure": content_score,
            "composite": composite,
            "grade": grade,
        },
        "facade_notes": facade_notes,
        "content_notes": content_notes,
        "content_source": source.get("content_source"),
        "content_source_exists": source.get("content_source_exists"),
        "findings": findings,
        "policy": "thin_loom_facade_ok_if_content_source_valid",
    }


def score_all_loom_skills(project_root: Path) -> dict[str, Any]:
    root = Path(project_root).expanduser().resolve() / "skills" / "loom"
    skills = []
    if (root / "SKILL.md").is_file():
        skills.append("loom")
    for d in sorted(root.iterdir()):
        if d.is_dir() and d.name.startswith("loom-") and (d / "SKILL.md").is_file():
            skills.append(d.name)
    results = [score_loom_skill(project_root, s) for s in skills]
    composites = [float(r["scores"]["composite"]) for r in results if r.get("scores")]
    avg = round(sum(composites) / len(composites), 2) if composites else 0.0
    failed = [r["skill"] for r in results if r.get("blocked") or not r.get("ok")]
    return {
        "schema": SCHEMA,
        "brand": "Loom",
        "count": len(results),
        "average_composite": avg,
        "failed": failed,
        "ok": not failed,
        "skills": results,
    }
