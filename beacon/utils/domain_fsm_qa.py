"""Domain FSM QA gate — legal walk + illegal rejection + coverage fail-closed (v1.6.7)."""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any

from beacon.utils.domain_fsm import (
    build_domain_fsm_gate_payload,
    evaluate_domain_fsm_authority,
    parse_domain_fsm_from_truth,
)
from beacon.utils.feature_package import _read_text, package_paths
from beacon.utils.golden_commerce_fixture import validate_negative_package
from beacon.utils.qa_state_machine import build_state_coverage_model, extract_fsm_from_truth
from beacon.utils.story_state import feature_slug
from beacon.utils.versioning import normalize_version, resolve_target_version

SCHEMA_VERSION = "1.0"
DOMAIN_FSM_COVERAGE_KEY = "domain_fsm_coverage"

REASON_LEGAL_WALK_MISSING = "domain_fsm_legal_walk_missing"
REASON_ILLEGAL_CASE_MISSING = "domain_fsm_illegal_case_missing"
REASON_COVERAGE_MISSING = "domain_fsm_coverage_missing"
REASON_COVERAGE_BELOW_THRESHOLD = "domain_fsm_coverage_below_threshold"
REASON_GOLDEN_NEGATIVE_NOT_CONSUMED = "golden_negative_not_consumed"

DEFAULT_COVERAGE_THRESHOLD = 1.0  # require full declared legal+illegal matrix presence

_LEGAL_MARKERS = (
    "legal",
    "legal walk",
    "合法",
    "合法路径",
    "happy path",
    "full path",
    "全路径",
)
_ILLEGAL_MARKERS = (
    "illegal",
    "非法",
    "negative",
    "无前置",
    "without product",
    "reject",
    "拒绝",
    "precedence",
)


def _semver_tuple(version: str | None) -> tuple[int, int, int]:
    normalized = normalize_version(version) or "v0.0.0"
    try:
        major, minor, patch = normalized.lstrip("v").split(".")
        return int(major), int(minor), int(patch)
    except Exception:  # noqa: BLE001
        return 0, 0, 0


def domain_fsm_qa_supported(version: str | None) -> bool:
    return _semver_tuple(version) >= (1, 6, 7)


def _table_rows(markdown: str) -> list[list[str]]:
    rows: list[list[str]] = []
    for line in str(markdown or "").splitlines():
        stripped = line.strip()
        if not stripped.startswith("|"):
            continue
        cells = [cell.strip() for cell in stripped.strip("|").split("|")]
        if not cells:
            continue
        if all(set(cell) <= {"-", ":", " "} for cell in cells if cell):
            continue
        rows.append(cells)
    return rows


def parse_domain_qa_matrix(tests_markdown: str) -> dict[str, Any]:
    """Parse tests.md coverage matrix for legal walk / illegal rows."""
    rows = _table_rows(tests_markdown)
    legal_rows: list[dict[str, str]] = []
    illegal_rows: list[dict[str, str]] = []
    other_rows: list[dict[str, str]] = []
    if not rows:
        return {
            "legal_walk_rows": [],
            "illegal_rows": [],
            "other_rows": [],
            "has_legal_walk": False,
            "has_illegal": False,
        }
    header = [cell.lower() for cell in rows[0]]
    start = 1 if any(token in " ".join(header) for token in ("ac", "tc", "path", "layer", "assertion")) else 0
    for row in rows[start:]:
        joined = " | ".join(row).lower()
        item = {
            "ac_id": row[0] if row else "",
            "tc_id": row[1] if len(row) > 1 else "",
            "path_type": row[2] if len(row) > 2 else "",
            "raw": " | ".join(row),
        }
        path_blob = f"{item['path_type']} {joined}"
        if any(marker in path_blob for marker in _ILLEGAL_MARKERS):
            illegal_rows.append(item)
        elif any(marker in path_blob for marker in _LEGAL_MARKERS):
            legal_rows.append(item)
        else:
            # fallback: legal walk keywords in assertion
            if any(marker in joined for marker in ("draft→", "draft->", "→paid", "->paid", "walk")):
                legal_rows.append(item)
            else:
                other_rows.append(item)
    return {
        "legal_walk_rows": legal_rows,
        "illegal_rows": illegal_rows,
        "other_rows": other_rows,
        "has_legal_walk": bool(legal_rows),
        "has_illegal": bool(illegal_rows),
    }


def build_domain_fsm_coverage(
    *,
    truth_markdown: str,
    tests_markdown: str,
    covered_legal: int | None = None,
    covered_illegal: int | None = None,
    threshold: float = DEFAULT_COVERAGE_THRESHOLD,
) -> dict[str, Any]:
    """Build domain_fsm_coverage payload for scorecard / release gates."""
    matrix = parse_domain_qa_matrix(tests_markdown)
    domain = evaluate_domain_fsm_authority(truth_markdown=truth_markdown, tests_markdown=tests_markdown)
    projection = parse_domain_fsm_from_truth(truth_markdown)
    # Also reuse arrow FSM extractor when present
    arrow_fsm = extract_fsm_from_truth(truth_markdown)
    legal_required = max(1, len(matrix["legal_walk_rows"])) if domain.get("required") else len(matrix["legal_walk_rows"])
    illegal_required = max(1, len(matrix["illegal_rows"])) if domain.get("required") else len(matrix["illegal_rows"])
    legal_present = len(matrix["legal_walk_rows"])
    illegal_present = len(matrix["illegal_rows"])
    legal_covered = legal_present if covered_legal is None else int(covered_legal)
    illegal_covered = illegal_present if covered_illegal is None else int(covered_illegal)

    legal_ratio = round(legal_covered / float(legal_required or 1), 4) if legal_required else 1.0
    illegal_ratio = round(illegal_covered / float(illegal_required or 1), 4) if illegal_required else 1.0
    # Presence-first coverage for matrix authoring; execution layer may raise later.
    coverage_ratio = round(min(legal_ratio, illegal_ratio), 4) if domain.get("required") else 1.0

    findings: list[dict[str, str]] = []
    if domain.get("required"):
        if legal_present < 1:
            findings.append(
                {
                    "kind": "legal_walk_missing",
                    "reason_code": REASON_LEGAL_WALK_MISSING,
                    "text": "domain QA matrix requires ≥1 legal FSM walk row",
                }
            )
        if illegal_present < 1:
            findings.append(
                {
                    "kind": "illegal_case_missing",
                    "reason_code": REASON_ILLEGAL_CASE_MISSING,
                    "text": "domain QA matrix requires ≥1 illegal/precedence rejection row",
                }
            )
        if coverage_ratio < float(threshold):
            findings.append(
                {
                    "kind": "coverage_below_threshold",
                    "reason_code": REASON_COVERAGE_BELOW_THRESHOLD,
                    "text": f"domain_fsm_coverage {coverage_ratio} < threshold {threshold}",
                }
            )

    state_coverage = {}
    if not bool(arrow_fsm.get("blocked")):
        transitions = [
            (str(t.get("from") or ""), str(t.get("to") or ""))
            for t in (arrow_fsm.get("transitions") or [])
            if isinstance(t, dict)
        ]
        state_coverage = build_state_coverage_model(
            arrow_fsm,
            covered_transitions=transitions,
            covered_boundary_states=list(arrow_fsm.get("boundary_states") or []),
        )

    blocked = bool(findings)
    return {
        "schema_version": SCHEMA_VERSION,
        "required": bool(domain.get("required")),
        "blocked": blocked,
        "status": "blocked" if blocked else ("not_required" if not domain.get("required") else "pass"),
        "reason_code": findings[0]["reason_code"] if findings else "",
        "findings": findings,
        "threshold": float(threshold),
        "coverage_ratio": coverage_ratio,
        "legal_walk": {
            "required": legal_required if domain.get("required") else 0,
            "present": legal_present,
            "covered": legal_covered,
            "rows": matrix["legal_walk_rows"],
        },
        "illegal": {
            "required": illegal_required if domain.get("required") else 0,
            "present": illegal_present,
            "covered": illegal_covered,
            "rows": matrix["illegal_rows"],
        },
        "matrix": matrix,
        "aggregates": [
            str(item.get("name") or "")
            for item in (projection.get("aggregates") or [])
            if isinstance(item, dict)
        ],
        "state_machine_coverage": state_coverage,
        "deep_route_recommended": bool(domain.get("required") and legal_present + illegal_present >= 8),
    }


def evaluate_domain_fsm_qa_gate(
    *,
    truth_markdown: str,
    tests_markdown: str,
    threshold: float = DEFAULT_COVERAGE_THRESHOLD,
) -> dict[str, Any]:
    coverage = build_domain_fsm_coverage(
        truth_markdown=truth_markdown,
        tests_markdown=tests_markdown,
        threshold=threshold,
    )
    return {
        "schema_version": SCHEMA_VERSION,
        "required": coverage.get("required"),
        "blocked": coverage.get("blocked"),
        "status": coverage.get("status"),
        "reason_code": coverage.get("reason_code") or "",
        "findings": coverage.get("findings") or [],
        DOMAIN_FSM_COVERAGE_KEY: coverage,
        "release_ready_allowed": not bool(coverage.get("blocked")),
    }


def build_domain_fsm_qa_gate_payload(
    project_root: Path,
    *,
    version: str = "auto",
    feature: str,
    threshold: float = DEFAULT_COVERAGE_THRESHOLD,
) -> dict[str, Any]:
    project_root = Path(project_root).expanduser().resolve()
    resolved_version = resolve_target_version(project_root, version)
    slug = feature_slug(feature)
    # Brownfield docs lines (< v1.6.7) still enforce when domain_gate.required (opt-in/sections).
    domain_gate = build_domain_fsm_gate_payload(project_root, version=resolved_version, feature=feature)
    if not domain_fsm_qa_supported(resolved_version) and not domain_gate.get("required"):
        return {
            "schema_version": SCHEMA_VERSION,
            "feature": feature,
            "feature_slug": slug,
            "version": resolved_version,
            "required": False,
            "blocked": False,
            "status": "not_supported",
            "reason_code": "",
            DOMAIN_FSM_COVERAGE_KEY: {},
            "release_ready_allowed": True,
            "domain_gate": domain_gate,
        }
    paths = package_paths(project_root, version=resolved_version, feature=slug)
    truth_md = _read_text(paths["truth"])
    tests_md = _read_text(paths["tests"])
    if not domain_gate.get("required"):
        return {
            "schema_version": SCHEMA_VERSION,
            "feature": feature,
            "feature_slug": slug,
            "version": resolved_version,
            "required": False,
            "blocked": False,
            "status": "not_required",
            "reason_code": "",
            DOMAIN_FSM_COVERAGE_KEY: {"required": False, "coverage_ratio": 1.0, "status": "not_required"},
            "release_ready_allowed": True,
            "domain_gate": domain_gate,
        }

    if not truth_md.strip():
        return {
            "schema_version": SCHEMA_VERSION,
            "feature": feature,
            "feature_slug": slug,
            "version": resolved_version,
            "required": True,
            "blocked": True,
            "status": "blocked",
            "reason_code": REASON_COVERAGE_MISSING,
            "findings": [
                {
                    "kind": "coverage_missing",
                    "reason_code": REASON_COVERAGE_MISSING,
                    "text": "domain feature missing truth package for QA domain_fsm_coverage",
                }
            ],
            DOMAIN_FSM_COVERAGE_KEY: {},
            "release_ready_allowed": False,
        }

    gate = evaluate_domain_fsm_qa_gate(
        truth_markdown=truth_md,
        tests_markdown=tests_md,
        threshold=threshold,
    )
    return {
        **gate,
        "feature": feature,
        "feature_slug": slug,
        "version": resolved_version,
        "domain_gate": domain_gate,
        "truth_path": str(paths["truth"].relative_to(project_root)),
        "tests_path": str(paths["tests"].relative_to(project_root)) if paths["tests"].exists() else "",
    }


def apply_domain_fsm_to_scorecard(
    scorecard: dict[str, Any],
    domain_qa_gate: dict[str, Any],
) -> dict[str, Any]:
    """Mutate/return scorecard with domain_fsm_coverage and fail-closed release_ready."""
    payload = dict(scorecard or {})
    coverage = domain_qa_gate.get(DOMAIN_FSM_COVERAGE_KEY) if isinstance(domain_qa_gate.get(DOMAIN_FSM_COVERAGE_KEY), dict) else {}
    payload[DOMAIN_FSM_COVERAGE_KEY] = coverage
    if not domain_qa_gate.get("required"):
        return payload

    stop_reasons = list(payload.get("stop_reasons") or [])
    if domain_qa_gate.get("blocked"):
        reason = str(domain_qa_gate.get("reason_code") or REASON_COVERAGE_MISSING)
        if reason not in stop_reasons:
            stop_reasons.append(reason)
        payload["release_ready"] = False
        if str(payload.get("continue_decision") or "") == "ready_for_release":
            payload["continue_decision"] = "stop_for_repair"
        payload["stop_reasons"] = sorted({str(item) for item in stop_reasons if str(item).strip()})
        payload["domain_fsm_qa_blocked"] = True
        payload["domain_fsm_qa_reason_code"] = reason
    else:
        payload["domain_fsm_qa_blocked"] = False
        payload["domain_fsm_qa_reason_code"] = ""
    return payload


def consume_golden_negative_for_qa(project_root: Path, *, version: str = "v1.6.7") -> dict[str, Any]:
    """QA must consume golden negative fixture and expect fail-closed."""
    negative = validate_negative_package(project_root, version=version)
    consumed = bool(negative.get("fails_closed"))
    return {
        "schema_version": SCHEMA_VERSION,
        "consumed": consumed,
        "expected_fail": True,
        "blocked": not consumed,
        "status": "pass" if consumed else "blocked",
        "reason_code": "" if consumed else REASON_GOLDEN_NEGATIVE_NOT_CONSUMED,
        "negative": negative,
    }


def recommend_deep_route(domain_qa_gate: dict[str, Any]) -> dict[str, Any]:
    coverage = domain_qa_gate.get(DOMAIN_FSM_COVERAGE_KEY) if isinstance(domain_qa_gate.get(DOMAIN_FSM_COVERAGE_KEY), dict) else {}
    recommend = bool(coverage.get("deep_route_recommended"))
    return {
        "recommended": recommend,
        "skill": "beacon-eval-qa-deep" if recommend else "beacon-eval-qa",
        "reason": "combinatorial domain paths" if recommend else "standard domain matrix",
    }
