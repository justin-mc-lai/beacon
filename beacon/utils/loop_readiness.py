"""Loop readiness audit scoring."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from beacon.utils.loop_budget import build_loop_budget_status
from beacon.utils.loop_failure_catalog import catalog_path, validate_failure_catalog
from beacon.utils.loop_patterns import registry_path, validate_pattern_registry

REQUIRED_SIGNAL_IDS = [
    "version_governance",
    "global_boundaries",
    "feature_packages",
    "workspace_admission",
    "qa_status",
    "release_status",
    "pattern_registry",
    "token_budget",
    "run_log",
    "failure_catalog",
]


def readiness_level(score: int) -> str:
    if score < 40:
        return "L0"
    if score < 60:
        return "L1"
    if score < 80:
        return "L2"
    return "L3"


def _signal(signal_id: str, status: str, *, weight: int = 10, reason_code: str = "", suggestion: dict[str, str] | None = None, details: dict[str, Any] | None = None) -> dict[str, Any]:
    return {
        "id": signal_id,
        "status": status,
        "weight": weight,
        "reason_code": reason_code,
        "suggestion": suggestion or {},
        "details": details or {},
    }


def build_loop_readiness_audit(
    project_root: Path,
    *,
    version: str,
    strict: bool = False,
    threshold: int = 80,
    suggest: bool = True,
) -> dict[str, Any]:
    root = project_root.expanduser().resolve()
    version_root = root / "docs" / "beacon" / version
    signals: list[dict[str, Any]] = []
    signals.append(
        _signal(
            "version_governance",
            "pass" if (root / "docs/beacon/governance/project-version-governance.md").is_file() else "fail",
            reason_code="" if (root / "docs/beacon/governance/project-version-governance.md").is_file() else "version_governance_missing",
            suggestion={"command": f"beacon doctor metadata verify --project-root {root} --version {version} --json"},
        )
    )
    signals.append(
        _signal(
            "global_boundaries",
            "pass" if (root / "docs/beacon/global-boundaries.md").is_file() else "fail",
            reason_code="" if (root / "docs/beacon/global-boundaries.md").is_file() else "global_boundaries_missing",
            suggestion={"route": "beacon-gov-doctor"},
        )
    )
    features_root = version_root / "features"
    feature_count = len([p for p in features_root.iterdir() if p.is_dir()]) if features_root.is_dir() else 0
    signals.append(
        _signal(
            "feature_packages",
            "pass" if feature_count else "fail",
            reason_code="" if feature_count else "feature_packages_missing",
            suggestion={"command": f"beacon doctor verify-materials --project-root {root} --version {version} --strict --json"},
            details={"feature_count": feature_count},
        )
    )
    admission_root = root / ".beacon/state/workspace-admission" / version
    admission_count = len(list(admission_root.glob("*.json"))) if admission_root.is_dir() else 0
    signals.append(
        _signal(
            "workspace_admission",
            "pass" if admission_count else "fail",
            reason_code="" if admission_count else "workspace_admission_missing",
            suggestion={"command": f"beacon workspace admit --project-root {root} --version {version} --feature <feature> --json"},
            details={"artifact_count": admission_count},
        )
    )
    qa_status_path = root / ".beacon/qa-status.json"
    signals.append(
        _signal(
            "qa_status",
            "pass" if qa_status_path.is_file() else "warn",
            reason_code="" if qa_status_path.is_file() else "qa_status_missing",
            suggestion={"route": "beacon-eval-qa"},
            weight=8,
        )
    )
    release_root = version_root / "release"
    signals.append(
        _signal(
            "release_status",
            "pass" if release_root.is_dir() else "warn",
            reason_code="" if release_root.is_dir() else "release_status_missing",
            suggestion={"route": "beacon-eval-release"},
            weight=8,
        )
    )
    registry = validate_pattern_registry(registry_path(root, version=version))
    signals.append(
        _signal(
            "pattern_registry",
            "pass" if registry.get("status") == "pass" else "fail" if registry.get("status") == "fail" else "warn",
            reason_code=str(registry.get("reason_code") or ""),
            suggestion={"command": f"beacon doctor loop-audit --project-root {root} --version {version} --json"},
            details={"findings": registry.get("findings", []), "pattern_count": registry.get("pattern_count", 0)},
        )
    )
    budget = build_loop_budget_status(root, version=version)
    signals.append(
        _signal(
            "token_budget",
            "fail" if budget.get("blocked") else "pass",
            reason_code=str(budget.get("reason_code") or ""),
            suggestion={"command": f"beacon status loop-budget --project-root {root} --version {version} --json"},
            details={"caps": budget.get("caps", {}), "kill_switch_active": budget.get("kill_switch_active", False)},
        )
    )
    run_root = root / ".beacon/runs"
    signals.append(
        _signal(
            "run_log",
            "pass" if run_root.is_dir() and any(run_root.iterdir()) else "warn",
            reason_code="" if run_root.is_dir() and any(run_root.iterdir()) else "run_log_missing",
            suggestion={"route": "beacon-gen-implement"},
            weight=8,
        )
    )
    catalog = validate_failure_catalog(catalog_path(root, version=version))
    signals.append(
        _signal(
            "failure_catalog",
            "pass" if catalog.get("status") == "pass" else "fail" if catalog.get("status") == "fail" else "warn",
            reason_code=str(catalog.get("reason_code") or ""),
            suggestion={"route": "beacon-gen-implement"},
            details={"findings": catalog.get("findings", []), "entry_count": catalog.get("entry_count", 0)},
        )
    )
    total_weight = sum(int(signal.get("weight", 0) or 0) for signal in signals)
    earned = sum(int(signal.get("weight", 0) or 0) for signal in signals if signal.get("status") == "pass")
    score = int(round((earned / total_weight) * 100)) if total_weight else 0
    level = readiness_level(score)
    below = score < int(threshold)
    status = "blocked" if strict and below else "pass" if not below else "report_only"
    suggestions = [
        {"signal_id": signal["id"], **signal.get("suggestion", {})}
        for signal in signals
        if suggest and signal.get("status") != "pass" and signal.get("suggestion")
    ]
    return {
        "schema_version": "loop-readiness-audit-v1",
        "status": status,
        "blocked": bool(strict and below),
        "reason_code": "loop_readiness_below_threshold" if strict and below else "",
        "version": version,
        "score": score,
        "level": level,
        "threshold": int(threshold),
        "strict": strict,
        "authority": "advisory" if not strict else "strict_support_gate",
        "release_verdict": False,
        "signals": signals,
        "findings": [signal for signal in signals if signal.get("status") != "pass"],
        "suggestions": suggestions,
        "required_signal_ids": REQUIRED_SIGNAL_IDS,
    }
