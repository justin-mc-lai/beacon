"""UI Design Philosophy Ship Gate (v1.6.7 P1).

ui-state-matrix.v1 binds domain FSM states to UI surfaces.
UX features require DESIGN.md (or version design contracts) unless deferred.
Ship/release_ready fails closed when matrix/design baseline missing.
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any

from beacon.utils.domain_fsm import build_domain_fsm_gate_payload, parse_domain_fsm_from_truth
from beacon.utils.feature_package import _parse_frontmatter, _read_text, package_paths
from beacon.utils.story_state import feature_slug
from beacon.utils.versioning import normalize_version, resolve_target_version

SCHEMA_VERSION = "1.0"
UI_STATE_MATRIX_SCHEMA = "ui-state-matrix.v1"

REASON_MATRIX_MISSING = "ui_state_matrix_missing"
REASON_MATRIX_UNBOUND = "ui_state_matrix_unbound_to_fsm"
REASON_DESIGN_MISSING = "design_baseline_missing"
REASON_SHIP_BLOCKED = "ui_design_ship_blocked"

_HEADING_RE = re.compile(r"^(#{2,6})\s+(.+?)\s*$")
_UX_MARKERS = (
    "ui",
    "ux",
    "页面",
    "界面",
    "前端",
    "visual",
    "design",
    "badge",
    "checkout",
    "order detail",
    "组件",
)


def _semver_tuple(version: str | None) -> tuple[int, int, int]:
    normalized = normalize_version(version) or "v0.0.0"
    try:
        major, minor, patch = normalized.lstrip("v").split(".")
        return int(major), int(minor), int(patch)
    except Exception:  # noqa: BLE001
        return 0, 0, 0


def ui_design_ship_supported(version: str | None) -> bool:
    return _semver_tuple(version) >= (1, 6, 7)


def _truthy(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    return str(value or "").strip().lower() in {"1", "true", "yes", "y", "on", "required"}


def _table_rows(text: str) -> list[list[str]]:
    rows: list[list[str]] = []
    for line in str(text or "").splitlines():
        stripped = line.strip()
        if not stripped.startswith("|"):
            continue
        cells = [c.strip() for c in stripped.strip("|").split("|")]
        if not cells or all(set(c) <= {"-", ":", " "} for c in cells if c):
            continue
        rows.append(cells)
    return rows


def parse_ui_state_matrix(markdown: str) -> dict[str, Any]:
    """Parse ui-state-matrix.v1 from markdown tables."""
    rows = _table_rows(markdown)
    states: list[dict[str, str]] = []
    if not rows:
        return {
            "schema": UI_STATE_MATRIX_SCHEMA,
            "states": [],
            "state_names": [],
            "has_matrix": False,
        }
    header = [c.lower() for c in rows[0]]
    start = 1 if any(tok in " ".join(header) for tok in ("state", "状态", "page", "badge", "order")) else 0
    for row in rows[start:]:
        if not row:
            continue
        state = row[0].strip()
        if not state or state.lower() in {"state", "order state", "状态"}:
            continue
        states.append(
            {
                "state": state,
                "page": row[1] if len(row) > 1 else "",
                "badge": row[2] if len(row) > 2 else "",
                "primary_action": row[3] if len(row) > 3 else "",
            }
        )
    return {
        "schema": UI_STATE_MATRIX_SCHEMA,
        "states": states,
        "state_names": [s["state"] for s in states],
        "has_matrix": bool(states),
    }


def find_design_baselines(project_root: Path, *, version: str, feature: str = "") -> dict[str, Any]:
    root = Path(project_root)
    resolved = resolve_target_version(root, version)
    candidates = [
        root / "DESIGN.md",
        root / "docs" / "beacon" / resolved / "design" / "style.md",
        root / "docs" / "beacon" / resolved / "design" / "component-system.md",
        root / "docs" / "beacon" / resolved / "design" / "interaction-contract.md",
        root / "docs" / "beacon" / resolved / "design" / "state-matrix.md",
    ]
    if feature:
        slug = feature_slug(feature)
        candidates.extend(
            [
                root / "docs" / "beacon" / resolved / "features" / slug / "DESIGN.md",
                root / "docs" / "beacon" / resolved / "features" / slug / "ui-state-matrix.md",
                root / "docs" / "beacon" / resolved / "fixtures" / "golden-commerce-checkout" / "positive" / "DESIGN.md",
                root / "docs" / "beacon" / resolved / "fixtures" / "golden-commerce-checkout" / "positive" / "ui-state-matrix.md",
            ]
        )
    existing = [str(p.relative_to(root)) for p in candidates if p.exists()]
    return {
        "paths": existing,
        "has_design_md": any(p.endswith("DESIGN.md") or p.endswith("design/style.md") for p in existing),
        "has_matrix_file": any("ui-state-matrix" in p or p.endswith("state-matrix.md") for p in existing),
        "has_any": bool(existing),
    }


def feature_requires_ux(
    *,
    truth_markdown: str = "",
    frontmatter: dict[str, Any] | None = None,
    explicit_ux: bool | None = None,
) -> bool:
    if explicit_ux is not None:
        return bool(explicit_ux)
    fm = frontmatter if isinstance(frontmatter, dict) else {}
    if any(_truthy(fm.get(k)) for k in ("ux_required", "ui_required", "design_required", "require_design")):
        return True
    if _truthy(fm.get("ux_deferred")) or str(fm.get("design_deferral") or "").strip():
        return False
    lowered = str(truth_markdown or "").lower()
    return any(token in lowered for token in _UX_MARKERS)


def evaluate_ui_state_matrix(
    *,
    matrix_markdown: str,
    truth_markdown: str = "",
    domain_states: list[str] | None = None,
) -> dict[str, Any]:
    matrix = parse_ui_state_matrix(matrix_markdown)
    findings: list[dict[str, str]] = []
    if not matrix["has_matrix"]:
        findings.append(
            {
                "kind": "matrix_missing",
                "reason_code": REASON_MATRIX_MISSING,
                "text": "ui-state-matrix.v1 requires at least one business-state → UI surface row",
            }
        )
        return {
            "schema_version": SCHEMA_VERSION,
            "schema": UI_STATE_MATRIX_SCHEMA,
            "blocked": True,
            "status": "blocked",
            "reason_code": REASON_MATRIX_MISSING,
            "findings": findings,
            "matrix": matrix,
        }

    # bind to domain FSM states when available
    fsm_states: set[str] = {s.lower() for s in (domain_states or []) if s}
    if not fsm_states and truth_markdown:
        projection = parse_domain_fsm_from_truth(truth_markdown)
        for agg in projection.get("aggregates") or []:
            if not isinstance(agg, dict):
                continue
            for st in agg.get("states") or []:
                fsm_states.add(str(st).lower())
    matrix_states = {str(s).lower() for s in matrix["state_names"]}
    unbound = sorted(s for s in matrix_states if fsm_states and s not in fsm_states)
    # If domain states known, matrix should map subset of them (at least one overlap)
    if fsm_states and not (matrix_states & fsm_states):
        findings.append(
            {
                "kind": "matrix_unbound",
                "reason_code": REASON_MATRIX_UNBOUND,
                "text": f"ui-state-matrix states {sorted(matrix_states)} do not bind domain FSM states {sorted(fsm_states)}",
            }
        )
    return {
        "schema_version": SCHEMA_VERSION,
        "schema": UI_STATE_MATRIX_SCHEMA,
        "blocked": bool(findings),
        "status": "blocked" if findings else "pass",
        "reason_code": findings[0]["reason_code"] if findings else "",
        "findings": findings,
        "matrix": matrix,
        "domain_states": sorted(fsm_states),
        "unbound_matrix_states": unbound,
        "overlap": sorted(matrix_states & fsm_states),
    }


def build_ui_design_ship_gate(
    project_root: Path,
    *,
    version: str = "auto",
    feature: str = "",
    truth_markdown: str = "",
    matrix_markdown: str = "",
    ux_required: bool | None = None,
) -> dict[str, Any]:
    project_root = Path(project_root).expanduser().resolve()
    resolved = resolve_target_version(project_root, version)
    # Docs < v1.6.7: still enforce when UX is explicitly required or DESIGN/matrix present.
    version_supported = ui_design_ship_supported(resolved)

    slug = feature_slug(feature) if feature else ""
    truth_md = truth_markdown
    matrix_md = matrix_markdown
    fm: dict[str, Any] = {}
    if slug and not truth_md:
        paths = package_paths(project_root, version=resolved, feature=slug)
        truth_md = _read_text(paths["truth"])
        fm, _, _ = _parse_frontmatter(truth_md)
        # matrix candidates
        for rel in (
            paths["dir"] / "ui-state-matrix.md",
            paths["dir"] / "DESIGN.md",
            project_root / "docs" / "beacon" / resolved / "design" / "state-matrix.md",
        ):
            if rel.exists() and not matrix_md:
                matrix_md = _read_text(rel)

    requires_ux = feature_requires_ux(truth_markdown=truth_md, frontmatter=fm if isinstance(fm, dict) else {}, explicit_ux=ux_required)
    baselines = find_design_baselines(project_root, version=resolved, feature=slug)
    deferred = _truthy((fm or {}).get("ux_deferred")) or bool(str((fm or {}).get("design_deferral") or "").strip())
    if not version_supported and not requires_ux and not baselines.get("has_any"):
        return {
            "schema_version": SCHEMA_VERSION,
            "feature": feature,
            "feature_slug": slug,
            "version": resolved,
            "required": False,
            "blocked": False,
            "status": "not_supported",
            "release_ready_allowed": True,
        }

    findings: list[dict[str, str]] = []
    design_alignment = {
        "required": requires_ux and not deferred,
        "has_baseline": baselines["has_any"],
        "paths": baselines["paths"],
        "deferred": deferred,
        "status": "pass",
    }
    if design_alignment["required"] and not baselines["has_any"]:
        findings.append(
            {
                "kind": "design_missing",
                "reason_code": REASON_DESIGN_MISSING,
                "text": "UX feature requires DESIGN.md or docs/beacon/<v>/design/* baseline (or explicit deferral)",
            }
        )
        design_alignment["status"] = "blocked"

    # domain states for binding
    domain_states: list[str] = []
    if slug:
        domain_gate = build_domain_fsm_gate_payload(project_root, version=resolved, feature=slug)
        proj = domain_gate.get("projection") if isinstance(domain_gate.get("projection"), dict) else {}
        for agg in proj.get("aggregates") or []:
            if isinstance(agg, dict):
                domain_states.extend(str(s) for s in (agg.get("states") or []))
    elif truth_md:
        proj = parse_domain_fsm_from_truth(truth_md)
        for agg in proj.get("aggregates") or []:
            if isinstance(agg, dict):
                domain_states.extend(str(s) for s in (agg.get("states") or []))

    # google design.md lint evidence (ux required)
    lint_eval: dict[str, Any] = {
        "required": requires_ux and not deferred,
        "status": "not_required",
        "blocked": False,
        "reason_code": "",
        "evidence_path": "",
        "summary": {},
    }
    if lint_eval["required"] and baselines["has_any"]:
        from beacon.utils.design_md_lint import run_design_md_lint

        lint_payload = run_design_md_lint(
            project_root,
            feature=slug or "project",
            version=resolved,
            write_evidence=True,
        )
        lint_eval = {
            "required": True,
            "status": lint_payload.get("status"),
            "blocked": bool(lint_payload.get("blocked")),
            "reason_code": lint_payload.get("reason_code") or "",
            "evidence_path": lint_payload.get("evidence_path") or "",
            "summary": lint_payload.get("summary") or {},
            "runner": lint_payload.get("runner") or "",
        }
        if lint_eval["blocked"]:
            findings.append(
                {
                    "kind": "design_md_lint",
                    "reason_code": str(lint_eval.get("reason_code") or "design_md_lint_failed"),
                    "text": "google design.md lint failed or DESIGN.md structural errors",
                }
            )
    elif lint_eval["required"] and not baselines["has_any"]:
        lint_eval["status"] = "blocked"
        lint_eval["blocked"] = True
        lint_eval["reason_code"] = "design_md_lint_missing"

    matrix_eval = {
        "schema": UI_STATE_MATRIX_SCHEMA,
        "required": requires_ux and not deferred,
        "status": "not_required",
        "blocked": False,
        "reason_code": "",
        "findings": [],
    }
    if matrix_eval["required"]:
        # if matrix content not provided, try baselines matrix file text
        if not matrix_md:
            for p in baselines["paths"]:
                if "matrix" in p.lower():
                    matrix_md = _read_text(project_root / p)
                    if matrix_md:
                        break
        matrix_eval = evaluate_ui_state_matrix(
            matrix_markdown=matrix_md,
            truth_markdown=truth_md,
            domain_states=domain_states,
        )
        matrix_eval["required"] = True
        if matrix_eval.get("blocked"):
            findings.extend(list(matrix_eval.get("findings") or []))

    blocked = bool(findings)
    return {
        "schema_version": SCHEMA_VERSION,
        "feature": feature,
        "feature_slug": slug,
        "version": resolved,
        "required": requires_ux and not deferred,
        "blocked": blocked,
        "status": "blocked" if blocked else ("not_required" if not (requires_ux and not deferred) else "pass"),
        "reason_code": findings[0]["reason_code"] if findings else "",
        "findings": findings,
        "design_alignment": design_alignment,
        "design_md_lint": lint_eval,
        "ui_state_matrix": matrix_eval,
        "release_ready_allowed": not blocked,
        "recommended_action": (
            "author DESIGN.md + ui-state-matrix bound to domain FSM states before ship"
            if blocked
            else ""
        ),
    }


def apply_ui_design_to_scorecard(scorecard: dict[str, Any], ship_gate: dict[str, Any]) -> dict[str, Any]:
    payload = dict(scorecard or {})
    payload["design_alignment"] = ship_gate.get("design_alignment") or {}
    payload["design_md_lint"] = ship_gate.get("design_md_lint") or {}
    payload["ui_state_matrix"] = ship_gate.get("ui_state_matrix") or {}
    if not ship_gate.get("required"):
        payload["ui_design_ship_blocked"] = False
        return payload
    if ship_gate.get("blocked"):
        payload["release_ready"] = False
        if str(payload.get("continue_decision") or "") == "ready_for_release":
            payload["continue_decision"] = "stop_for_repair"
        stops = list(payload.get("stop_reasons") or [])
        reason = str(ship_gate.get("reason_code") or REASON_SHIP_BLOCKED)
        if reason not in stops:
            stops.append(reason)
        payload["stop_reasons"] = sorted({str(s) for s in stops if str(s).strip()})
        payload["ui_design_ship_blocked"] = True
        payload["ui_design_ship_reason_code"] = reason
    else:
        payload["ui_design_ship_blocked"] = False
        payload["ui_design_ship_reason_code"] = ""
    return payload


def golden_commerce_matrix_present(project_root: Path, *, version: str = "v1.6.7") -> dict[str, Any]:
    root = Path(project_root)
    path = root / "docs" / "beacon" / version / "fixtures" / "golden-commerce-checkout" / "positive" / "ui-state-matrix.md"
    text = _read_text(path) if path.exists() else ""
    parsed = parse_ui_state_matrix(text)
    return {
        "path": str(path.relative_to(root)) if path.exists() else "",
        "exists": path.exists(),
        "has_matrix": parsed["has_matrix"],
        "state_names": parsed["state_names"],
        "status": "pass" if parsed["has_matrix"] else "blocked",
    }
