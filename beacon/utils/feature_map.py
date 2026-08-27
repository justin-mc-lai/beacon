"""Feature map: truth projection with entry points + verification (v1.6.14 L3).

A feature-map.md is a one-way projection of frozen truth: it tells an agent
WHERE a feature lives and HOW to verify it, always binding to frozen AC ids
(AC-001). Phase 2 adds reproduce routing from a fuzzy symptom hint (AC-002).
Phase 3 exposes runnable verification commands an agent can execute and assert
on signals (AC-003). The map never rewrites truth (AC-004).
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any

from beacon.utils.code2truth import _looks_like_entrypoint
from beacon.utils.feature_package import _read_text, package_paths
from beacon.utils.story_state import feature_slug
from beacon.utils.truth_review_gate import extract_fsm_five_tuple
from beacon.utils.versioning import resolve_target_version

SCHEMA_FEATURE_MAP = "feature-map.v1"
REASON_NO_AC = "feature_map_no_ac_binding"


def _extract_acceptance_criteria(truth_markdown: str) -> list[dict[str, str]]:
    acs: list[dict[str, str]] = []
    for m in re.finditer(r"\b(AC-[A-Z0-9]+(?:-[A-Z0-9]+)*)\b", str(truth_markdown or ""), re.IGNORECASE):
        acs.append({"ac_id": m.group(1).upper()})
    seen: set[str] = set()
    uniq: list[dict[str, str]] = []
    for item in acs:
        if item["ac_id"] in seen:
            continue
        seen.add(item["ac_id"])
        uniq.append(item)
    return uniq


def _derive_entry_points(project_root: Path, truth_markdown: str) -> list[dict[str, str]]:
    """Derive candidate entry points from the project source inventory (AC-001).

    Uses code2truth's entrypoint heuristic; the list is a skeleton the
    implementer fills with real routes/commands. A custom scan skips only
    child `.beacon` runtimes, not a worktree that lives inside `.beacon/`.
    """
    root = Path(project_root)
    entries: list[dict[str, str]] = []
    seen: set[str] = set()
    skip_dirs = {"node_modules", "__pycache__", ".pytest_cache", ".mypy_cache", ".ruff_cache", ".git", ".venv"}
    for path in sorted(root.rglob("*")):
        if len(entries) >= 20:
            break
        if not path.is_file():
            continue
        if any(part in skip_dirs for part in path.parts):
            continue
        if not _looks_like_entrypoint(path):
            continue
        rel = str(path.relative_to(root))
        if rel in seen:
            continue
        seen.add(rel)
        entries.append(
            {
                "ac_id": "",
                "type": "file",
                "path": rel,
                "how_to_enter": "",
            }
        )
    return entries


def _derive_verifications(ac_ids: list[str], tests_markdown: str) -> list[dict[str, str]]:
    """Pull runnable verification commands from tests.md, bound to AC ids (AC-003)."""
    verifications: list[dict[str, str]] = []
    for row in _tests_table_rows(str(tests_markdown or "")):
        tc_id = row[0] if len(row) > 0 else ""
        ac_id = row[1] if len(row) > 1 else ""
        command = row[2] if len(row) > 2 else ""
        assertion = row[3] if len(row) > 3 else ""
        if not command or not command.strip():
            continue
        ac_norm = ac_id.strip().upper()
        if ac_norm not in {a["ac_id"] for a in ac_ids}:
            continue
        verifications.append(
            {
                "ac_id": ac_norm,
                "command": command.strip().strip("`"),
                "assertion": assertion.strip(),
                "signal": "exit_code_0",
            }
        )
    return verifications


def _tests_table_rows(markdown: str) -> list[list[str]]:
    rows: list[list[str]] = []
    for line in str(markdown or "").splitlines():
        stripped = line.strip()
        if not stripped.startswith("|"):
            continue
        cells = [c.strip() for c in stripped.strip("|").split("|")]
        if not cells or all(set(c) <= {"-", ":", " "} for c in cells if c):
            continue
        rows.append(cells)
    return rows


def _reproduce_routes(truth_markdown: str, entry_points: list[dict[str, str]]) -> list[dict[str, Any]]:
    """Phase 2: map fuzzy symptom hints to entry points (AC-002)."""
    routes: list[dict[str, Any]] = []
    states = list(extract_fsm_five_tuple(truth_markdown).get("from_states") or [])
    if states and entry_points:
        hint = states[0]
        routes.append(
            {
                "symptom_hint": hint,
                "steps": [f"open {entry_points[0]['path']}", "run feature entrypoint", "observe signal"],
            }
        )
    return routes


def derive_feature_map(
    project_root: Path,
    *,
    version: str,
    feature: str,
) -> dict[str, Any]:
    """Build the feature-map projection from frozen truth + tests (AC-001..004)."""
    project_root = Path(project_root).expanduser().resolve()
    resolved_version = resolve_target_version(project_root, version)
    slug = feature_slug(feature)
    paths = package_paths(project_root, version=resolved_version, feature=slug)
    truth_md = _read_text(paths["truth"])
    tests_md = _read_text(paths["tests"])
    ac_ids = _extract_acceptance_criteria(truth_md)
    entry_points = _derive_entry_points(project_root, truth_md)
    verifications = _derive_verifications(ac_ids, tests_md)
    reproduce = _reproduce_routes(truth_md, entry_points)
    map_data = {
        "schema": SCHEMA_FEATURE_MAP,
        "slug": slug,
        "version": resolved_version,
        "ac_ids": [a["ac_id"] for a in ac_ids],
        "entry_points": entry_points,
        "verification": verifications,
        "reproduce": reproduce,
    }
    # AC-001: skeleton must bind entry_points + verification to AC ids. Verification
    # commands come from tests.md which always bind AC; entry points get ac bound on fill.
    map_data["ac_bound"] = bool(verifications) or bool(ac_ids)
    return map_data


def render_feature_map_markdown(map_data: dict[str, Any]) -> str:
    """Render feature-map.md skeleton markdown (AC-001)."""
    lines = [
        "---",
        f"slug: {map_data.get('slug', '')}",
        f"version: {map_data.get('version', '')}",
        f"schema: {SCHEMA_FEATURE_MAP}",
        "status: derived",
        "---",
        "",
        f"# Feature Map: {map_data.get('slug', '')}",
        "",
        "> 单向投影：地图引用 truth 的 AC，绝不反向改写 truth（AC-004）。",
        "",
        "## 入口（Entry Points）",
        "",
        "| AC ID | type | path | how_to_enter |",
        "|-------|------|------|--------------|",
    ]
    for e in map_data.get("entry_points") or []:
        lines.append(
            f"| {e.get('ac_id', '')} | {e.get('type', '')} | {e.get('path', '')} | {e.get('how_to_enter', '')} |"
        )
    lines += ["", "## 验证命令（Verification Commands）", "", "| AC ID | command | assertion | signal |", "|-------|---------|-----------|--------|"]
    for v in map_data.get("verification") or []:
        lines.append(
            f"| {v.get('ac_id', '')} | `{v.get('command', '')}` | {v.get('assertion', '')} | {v.get('signal', '')} |"
        )
    lines += ["", "## 复现路由（Reproduce Routes）", "", "| symptom_hint | steps |", "|--------------|-------|"]
    for r in map_data.get("reproduce") or []:
        steps = "; ".join(r.get("steps") or [])
        lines.append(f"| {r.get('symptom_hint', '')} | {steps} |")
    return "\n".join(lines) + "\n"


def scaffold_feature_map(
    project_root: Path,
    *,
    version: str,
    feature: str,
) -> dict[str, Any]:
    """Write features/<slug>/feature-map.md skeleton (AC-001)."""
    map_data = derive_feature_map(project_root, version=version, feature=feature)
    project_root = Path(project_root).expanduser().resolve()
    resolved_version = resolve_target_version(project_root, version)
    slug = feature_slug(feature)
    target = project_root / "docs" / "beacon" / resolved_version / "features" / slug / "feature-map.md"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(render_feature_map_markdown(map_data), encoding="utf-8")
    return {
        "schema": SCHEMA_FEATURE_MAP,
        "slug": slug,
        "version": resolved_version,
        "path": str(target.relative_to(project_root)),
        "ac_bound": map_data.get("ac_bound", False),
        "status": "scaffolded",
    }


def route_reproduce(map_data: dict[str, Any], symptom_hint: str) -> list[dict[str, Any]]:
    """Phase 2: route a fuzzy bug description to matching entry/verification (AC-002)."""
    hint = str(symptom_hint or "").lower()
    matches: list[dict[str, Any]] = []
    for route in map_data.get("reproduce") or []:
        if route.get("symptom_hint", "").lower() in hint or hint in route.get("symptom_hint", "").lower():
            matches.append(route)
    if not matches:
        for e in map_data.get("entry_points") or []:
            if e.get("path") and e["path"].lower() in hint:
                matches.append(
                    {
                        "symptom_hint": symptom_hint,
                        "steps": [f"open {e['path']}", "run feature entrypoint", "observe signal"],
                        "entry_point": e["path"],
                    }
                )
    return matches


def verify_map_one_way(project_root: Path, *, version: str, feature: str) -> dict[str, Any]:
    """AC-004: map references truth AC ids; map never rewrites truth; drift detectable."""
    project_root = Path(project_root).expanduser().resolve()
    resolved_version = resolve_target_version(project_root, version)
    slug = feature_slug(feature)
    paths = package_paths(project_root, version=resolved_version, feature=slug)
    truth_md = _read_text(paths["truth"])
    map_path = paths["dir"] / "feature-map.md"
    if not map_path.exists():
        return {"schema": SCHEMA_FEATURE_MAP, "ok": True, "drift": False, "blocked": False, "reason_code": ""}
    map_md = _read_text(map_path)
    truth_acs = {a["ac_id"] for a in _extract_acceptance_criteria(truth_md)}
    map_acs = {a["ac_id"] for a in _extract_acceptance_criteria(map_md)}
    drift_acs = sorted(map_acs - truth_acs)
    return {
        "schema": SCHEMA_FEATURE_MAP,
        "ok": not drift_acs,
        "drift": bool(drift_acs),
        "blocked": bool(drift_acs),
        "reason_code": "feature_map_ac_drift" if drift_acs else "",
        "drift_acs": drift_acs,
    }
