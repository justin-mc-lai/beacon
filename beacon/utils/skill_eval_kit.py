"""Skill Eval Kit contracts for v1.4.10."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from beacon.utils.runtime import now_iso, utc_compact_ts, write_json


SCORING_DIMENSIONS = (
    "route_stability",
    "boundary_preservation",
    "source_anchor_sufficiency",
    "actionability",
    "material_effect_closure",
    "clarification_quality",
    "token_efficiency",
)

REQUIRED_CASE_FIELDS = (
    "case_id",
    "prompt",
    "expected_route",
    "boundary_expectations",
    "source_anchor_requirements",
    "tags",
    "split",
    "expected_evidence",
    "scoring_dimensions",
)


def skill_eval_root(project_root: Path) -> Path:
    return project_root / ".beacon" / "state" / "skill-eval"


def default_route_stability_cases() -> list[dict[str, Any]]:
    return [
        _case("route-ordinary-support", "Use beacon brainstorm for v1.4.10 feature research", "beacon-brainstorm", ["route_stability", "support"]),
        _case("route-deep", "Run beacon-deep for a feature deep analysis", "beacon-deep", ["route_stability", "deep"]),
        _case("route-learn", "Recall governed learning influence for a feature", "beacon-learn", ["route_stability", "learn"]),
        _case("route-implement-single", "Implement a small fix with single mode", "beacon-implement --mode single", ["route_stability", "implement"]),
        _case("route-implement-team", "Implement a complex feature with team mode", "beacon-implement --mode team", ["route_stability", "implement"]),
        _case("route-implement-ralph", "Continue implementation closure with Ralph", "beacon-implement --mode ralph", ["route_stability", "implement"]),
    ]


def _case(case_id: str, prompt: str, expected_route: str, tags: list[str]) -> dict[str, Any]:
    return {
        "case_id": case_id,
        "prompt": prompt,
        "expected_route": expected_route,
        "boundary_expectations": [
            "must_not_rewrite_requirement_truth",
            "must_not_claim_gate_or_release_verdict",
        ],
        "source_anchor_requirements": ["frozen_docs_or_skill_contract"],
        "tags": tags,
        "split": "regression-core" if "route_stability" in tags else "optimization",
        "expected_evidence": ["route_decision", "boundary_statement"],
        "scoring_dimensions": list(SCORING_DIMENSIONS),
    }


def validate_eval_case(case: dict[str, Any]) -> list[dict[str, Any]]:
    issues: list[dict[str, Any]] = []
    for field in REQUIRED_CASE_FIELDS:
        value = case.get(field)
        if value in ("", None, [], {}):
            issues.append({"reason_code": "skill_eval_case_field_missing", "field": field, "case_id": str(case.get("case_id") or "")})
    dimensions = set(str(item) for item in case.get("scoring_dimensions", []) if str(item).strip())
    missing_dimensions = [item for item in SCORING_DIMENSIONS if item not in dimensions]
    if missing_dimensions:
        issues.append(
            {
                "reason_code": "skill_eval_case_scoring_dimension_missing",
                "case_id": str(case.get("case_id") or ""),
                "missing_dimensions": missing_dimensions,
            }
        )
    return issues


def validate_cases(cases: list[dict[str, Any]]) -> dict[str, Any]:
    issues: list[dict[str, Any]] = []
    for case in cases:
        issues.extend(validate_eval_case(case))
    expected_routes = {str(case.get("expected_route") or "") for case in cases}
    for bad_route in ("beacon-implement-team", "beacon-implement-ralph", "beacon-implement-single"):
        if bad_route in expected_routes:
            issues.append({"reason_code": "skill_eval_invalid_public_implement_skill_route", "route": bad_route})
    required_routes = {
        "beacon-brainstorm",
        "beacon-deep",
        "beacon-learn",
        "beacon-implement --mode single",
        "beacon-implement --mode team",
        "beacon-implement --mode ralph",
    }
    missing_routes = sorted(required_routes - expected_routes)
    if missing_routes:
        issues.append({"reason_code": "skill_eval_route_stability_case_missing", "missing_routes": missing_routes})
    return {"schema_version": "1.0", "status": "blocked" if issues else "pass", "blocked": bool(issues), "issues": issues}


def materialize_skill_eval_kit(project_root: Path, *, cases: list[dict[str, Any]] | None = None) -> dict[str, Any]:
    root = skill_eval_root(project_root)
    root.mkdir(parents=True, exist_ok=True)
    effective_cases = cases if cases is not None else default_route_stability_cases()
    validation = validate_cases(effective_cases)
    cases_path = root / "cases.json"
    tags_path = root / "tags.json"
    splits_dir = root / "splits"
    splits_dir.mkdir(parents=True, exist_ok=True)
    regression_core_path = root / "regression-core.txt"
    tags = sorted({tag for case in effective_cases for tag in case.get("tags", []) if str(tag).strip()})
    optimization = [case["case_id"] for case in effective_cases if case.get("split") == "optimization"]
    holdout = [case["case_id"] for case in effective_cases if case.get("split") == "holdout"]
    regression_core = [case["case_id"] for case in effective_cases if case.get("split") == "regression-core"]
    write_json(cases_path, {"schema_version": "1.0", "cases": effective_cases, "validation": validation})
    write_json(tags_path, {"schema_version": "1.0", "tags": tags, "scoring_dimensions": list(SCORING_DIMENSIONS)})
    (splits_dir / "optimization.txt").write_text("\n".join(optimization) + ("\n" if optimization else ""), encoding="utf-8")
    (splits_dir / "holdout.txt").write_text("\n".join(holdout) + ("\n" if holdout else ""), encoding="utf-8")
    regression_core_path.write_text("\n".join(regression_core) + "\n", encoding="utf-8")
    return {
        "schema_version": "1.0",
        "status": "ready" if not validation["blocked"] else "blocked",
        "root": str(root.relative_to(project_root)),
        "cases_path": str(cases_path.relative_to(project_root)),
        "tags_path": str(tags_path.relative_to(project_root)),
        "optimization_split_path": str((splits_dir / "optimization.txt").relative_to(project_root)),
        "holdout_split_path": str((splits_dir / "holdout.txt").relative_to(project_root)),
        "regression_core_path": str(regression_core_path.relative_to(project_root)),
        "case_count": len(effective_cases),
        "regression_core_count": len(regression_core),
        "validation": validation,
    }


def run_skill_eval(project_root: Path, *, split: str = "regression-core") -> dict[str, Any]:
    kit = materialize_skill_eval_kit(project_root)
    cases_payload = {}
    cases_path = project_root / kit["cases_path"]
    if cases_path.exists():
        import json

        cases_payload = json.loads(cases_path.read_text(encoding="utf-8"))
    cases = [case for case in cases_payload.get("cases", []) if split == "all" or case.get("split") == split]
    run_id = f"skill-eval-{utc_compact_ts().lower()}"
    run_dir = skill_eval_root(project_root) / "runs" / run_id
    traces_dir = run_dir / "traces"
    traces_dir.mkdir(parents=True, exist_ok=True)
    failures: list[dict[str, Any]] = []
    for case in cases:
        issues = validate_eval_case(case)
        if issues:
            failures.extend(issues)
        trace = {
            "schema_version": "1.0",
            "case_id": case.get("case_id"),
            "expected_route": case.get("expected_route"),
            "status": "pass" if not issues else "fail",
            "boundary_preserved": not issues,
        }
        write_json(traces_dir / f"{case.get('case_id')}.json", trace)
    metrics = {
        "schema_version": "1.0",
        "run_id": run_id,
        "split": split,
        "case_count": len(cases),
        "failure_count": len(failures),
        "status": "pass" if not failures else "fail",
        "failures": failures,
        "generated_at": now_iso(),
    }
    write_json(run_dir / "metrics.json", metrics)
    return {
        "schema_version": "1.0",
        "status": metrics["status"],
        "run_id": run_id,
        "split": split,
        "metrics_path": str((run_dir / "metrics.json").relative_to(project_root)),
        "traces_path": str(traces_dir.relative_to(project_root)),
        "runtime_evidence_only": True,
        "requirement_truth": False,
        "kit": kit,
    }
