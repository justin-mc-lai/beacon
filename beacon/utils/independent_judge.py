"""Independent gate judge (v1.6.16 P3): re-compute key gate values from raw
evidence with an independent algorithm, then compare against the system verdict.

Purpose: a gate value (e.g. coverage_rate) computed and judged by the same
system is self-endorsed. This module recomputes from raw scenario results using
a deliberately separate algorithm, so a systematic bias in the system judge can
surface as a comparison deviation.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from beacon.utils.story_state import feature_slug
from beacon.utils.versioning import resolve_target_version

SCHEMA_JUDGE = "independent-judge.v1"


def recalc_coverage_from_scenarios(
    scenario_results: list[dict[str, Any]],
    *,
    required_families: list[str],
) -> float:
    """Independent coverage recomputation.

    Unlike the system judge (which may apply type weights / quantity floors),
    this simply counts: of the required families, how many have at least one
    executed scenario with evidence. This is deliberately a different formula —
    a divergent answer between system and independent judge is a signal worth
    auditing, not something to paper over.
    """
    required = {str(f) for f in required_families if str(f).strip()}
    if not required:
        return 1.0
    covered: set[str] = set()
    for item in scenario_results:
        if not isinstance(item, dict):
            continue
        if not bool(item.get("evidence_ref")):
            continue
        family = str(item.get("scenario_family") or "").strip()
        if family:
            covered.add(family)
    return round(len(covered & required) / float(len(required)), 4)


def load_feature_scorecard(project_root: Path, *, version: str, feature: str) -> dict[str, Any] | None:
    slug = feature_slug(feature)
    path = project_root / ".beacon" / "qa" / "features" / slug / "scorecard.json"
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:  # noqa: BLE001
        return None


def compare_coverage_verdict(
    project_root: Path,
    *,
    version: str,
    feature: str,
    scenario_results: list[dict[str, Any]] | None = None,
    required_families: list[str] | None = None,
) -> dict[str, Any]:
    """Compare system coverage_rate against independent recomputation.

    Returns match/diff + audit record. Never mutates gate rules and never
    issues a pass/fail verdict itself — it only checks whether the system value
    is credible.
    """
    project_root = Path(project_root).expanduser().resolve()
    resolved_version = resolve_target_version(project_root, version)
    slug = feature_slug(feature)
    scorecard = load_feature_scorecard(project_root, version=resolved_version, feature=slug)
    system_coverage = None
    system_required = None
    if scorecard:
        cc = scorecard.get("coverage_current") if isinstance(scorecard.get("coverage_current"), dict) else {}
        system_coverage = cc.get("coverage_rate")
        system_required = cc.get("required_scenario_families") or []

    # If raw inputs not provided, fall back to system-required families and the
    # scorecard's executed scenarios are unavailable here — mark pending.
    if scenario_results is None:
        if system_coverage is None:
            return {
                "schema": SCHEMA_JUDGE,
                "status": "pending",
                "reason_code": "independent_judge_data_missing",
                "gate": "coverage_rate",
                "details": {},
            }
        return {
            "schema": SCHEMA_JUDGE,
            "status": "pending",
            "reason_code": "independent_judge_scenarios_missing",
            "gate": "coverage_rate",
            "system_coverage": system_coverage,
            "details": {},
        }

    families = required_families if required_families is not None else (system_required or [])
    independent = recalc_coverage_from_scenarios(scenario_results, required_families=families)

    if system_coverage is None:
        return {
            "schema": SCHEMA_JUDGE,
            "status": "pending",
            "reason_code": "independent_judge_system_value_missing",
            "gate": "coverage_rate",
            "independent_coverage": independent,
            "details": {"independent_only": True},
        }

    match = abs(float(system_coverage) - independent) < 1e-6
    audit = {
        "gate": "coverage_rate",
        "system_coverage": system_coverage,
        "independent_coverage": independent,
        "diff": round(float(system_coverage or 0.0) - independent, 4),
        "required_families": sorted(families),
        "match": bool(match),
    }
    return {
        "schema": SCHEMA_JUDGE,
        "status": "verified" if match else "flagged",
        "reason_code": "" if match else "independent_judge_deviation",
        "gate": "coverage_rate",
        "audit": audit,
    }


def schema_contract() -> dict[str, Any]:
    """Public field contract for independent-judge.v1 (AC-004 no verdict authority)."""
    return {
        "schema": SCHEMA_JUDGE,
        "fields": {
            "compare": ["gate", "system_coverage", "independent_coverage", "diff", "match"],
            "statuses": ["verified", "flagged", "pending"],
        },
        "authority": {"issues_verdict": False, "only_checks_credibility": True},
    }
