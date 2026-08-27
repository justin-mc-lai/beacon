"""Auto-merge gate (v1.6.15 L2): merge-to-main safety check.

Three conditions must hold before an agent may auto-merge back to main:
1. type coverage ok (v1.6.15 L1 coverage_rate is type-weighted; >= threshold)
2. failure-mode regression catalog hit count == 0 (v1.6.13 D3 catalog)
3. adversarial review delivered (3-5 flip points + evidence)

Release human gate is untouched: this gate only guards the merge step, never
the release verdict. Merging is reversible; publishing is not.
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any

from beacon.utils.feature_package import _read_text
from beacon.utils.story_state import feature_slug
from beacon.utils.versioning import resolve_target_version

SCHEMA_AUTOMERGE = "automerge-gate.v1"
REASON_COVERAGE_LOW = "automerge_coverage_below_threshold"
REASON_REGRESSION_HIT = "automerge_regression_catalog_hit"
REASON_ADVERSARIAL_MISSING = "automerge_adversarial_review_missing"
DEFAULT_COVERAGE_THRESHOLD = 0.85

FM_CATALOG_CANDIDATES = (
    "skills/beacon/beacon-qa/references/failure-mode-catalog.md",
    "beacon-qa/references/failure-mode-catalog.md",
)


def _find_failure_mode_catalog(project_root: Path) -> Path | None:
    for rel in FM_CATALOG_CANDIDATES:
        candidate = project_root / rel
        if candidate.exists():
            return candidate
    return None


def _count_failure_mode_hits(
    catalog_md: str,
    *,
    agent_signals: list[str] | None = None,
) -> dict[str, Any]:
    """Count failure modes whose symptoms match agent signals (AC-002).

    A hit means a known failure mode (e.g. docs_only_closure, soft_test_only)
    is detected in the incoming merge. Hit > 0 blocks the merge.
    """
    signals = [str(s or "").lower() for s in (agent_signals or [])]
    if not signals:
        return {"hits": 0, "hit_ids": [], "checked": 0}
    hits: list[str] = []
    checked = 0
    for match in re.finditer(r"^##\s+(FM-\d+)\s+[^\n]*?[（(]([^）)]+)[）)]", catalog_md, re.IGNORECASE | re.MULTILINE):
        checked += 1
        fm_id = match.group(1)
        signal_key = match.group(2).strip().lower()
        if any(signal_key in signal or signal in signal_key for signal in signals):
            hits.append(fm_id)
    return {"hits": len(hits), "hit_ids": sorted(hits), "checked": checked}


def build_automerge_gate_payload(
    project_root: Path,
    *,
    version: str = "auto",
    feature: str,
    coverage_rate: float | None = None,
    agent_signals: list[str] | None = None,
    adversarial_review: dict[str, Any] | None = None,
    coverage_threshold: float = DEFAULT_COVERAGE_THRESHOLD,
) -> dict[str, Any]:
    """Build the auto-merge gate payload (AC-001..004). Fail-closed on any condition."""
    project_root = Path(project_root).expanduser().resolve()
    resolved_version = resolve_target_version(project_root, version)
    slug = feature_slug(feature)
    findings: list[dict[str, Any]] = []

    # Condition 1: type coverage (v1.6.15 L1 type-weighted rate)
    if coverage_rate is None:
        coverage_rate = _resolve_feature_coverage(project_root, resolved_version, slug)
    coverage_ok = bool(coverage_rate is not None and coverage_rate >= float(coverage_threshold))
    if not coverage_ok:
        findings.append(
            {
                "kind": "coverage_below_threshold",
                "reason_code": REASON_COVERAGE_LOW,
                "text": f"type-weighted coverage {coverage_rate} < threshold {coverage_threshold}",
            }
        )

    # Condition 2: failure-mode regression catalog hit == 0
    catalog_path = _find_failure_mode_catalog(project_root)
    regression = _count_failure_mode_hits(
        _read_text(catalog_path) if catalog_path else "",
        agent_signals=agent_signals,
    )
    if regression["hits"] > 0:
        findings.append(
            {
                "kind": "regression_catalog_hit",
                "reason_code": REASON_REGRESSION_HIT,
                "text": f"failure-mode regression catalog hit: {regression['hit_ids']}",
                "hits": regression["hit_ids"],
            }
        )

    # Condition 3: adversarial review delivered (3-5 flip points + evidence)
    adv = adversarial_review if isinstance(adversarial_review, dict) else {}
    adv_ok = bool(
        isinstance(adv.get("flip_points"), list)
        and len(adv["flip_points"]) >= 3
        and bool(adv.get("evidence"))
        and str(adv.get("verdict") or "").strip().lower() not in {"blocked", "fail"}
    )
    if not adv_ok:
        findings.append(
            {
                "kind": "adversarial_review_missing",
                "reason_code": REASON_ADVERSARIAL_MISSING,
                "text": "adversarial review requires >=3 flip points + evidence + non-blocked verdict",
            }
        )

    blocked = bool(findings)
    return {
        "schema": SCHEMA_AUTOMERGE,
        "feature": feature,
        "feature_slug": slug,
        "version": resolved_version,
        "coverage_rate": coverage_rate,
        "coverage_threshold": float(coverage_threshold),
        "coverage_ok": coverage_ok,
        "regression": regression,
        "adversarial_ok": adv_ok,
        "blocked": blocked,
        "status": "blocked" if blocked else "pass",
        "reason_codes": [f.get("reason_code") for f in findings],
        "findings": findings,
        "release_human_gate_preserved": True,
    }


def _resolve_feature_coverage(
    project_root: Path,
    version: str,
    slug: str,
) -> float | None:
    """Read type-weighted coverage from QA scorecard / coverage summary."""
    import json

    scorecard = project_root / ".beacon" / "qa" / "features" / slug / "scorecard.json"
    if scorecard.exists():
        try:
            payload = json.loads(scorecard.read_text(encoding="utf-8"))
            coverage = payload.get("coverage_current") if isinstance(payload.get("coverage_current"), dict) else {}
            rate = coverage.get("coverage_rate")
            if rate is not None:
                return float(rate)
        except Exception:  # noqa: BLE001
            pass
    summary = project_root / ".beacon" / "coverage-summary.json"
    if summary.exists():
        try:
            payload = json.loads(summary.read_text(encoding="utf-8"))
            rate = payload.get("coverage_rate")
            if rate is not None:
                return float(rate)
        except Exception:  # noqa: BLE001
            pass
    return None


def schema_contract() -> dict[str, Any]:
    """Public field contract for automerge-gate.v1 (AC-004 no new command surface)."""
    return {
        "schema": SCHEMA_AUTOMERGE,
        "fields": {
            "conditions": ["coverage_ok", "regression", "adversarial_ok"],
            "blocked_reasons": [
                REASON_COVERAGE_LOW,
                REASON_REGRESSION_HIT,
                REASON_ADVERSARIAL_MISSING,
            ],
        },
        "authority": {
            "merge_gate": ["qa_passed", "coverage_ok", "regression_zero", "adversarial_ok"],
            "release_gate_never_auto": True,
        },
    }
