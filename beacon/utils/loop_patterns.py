"""Loop pattern registry loading and validation."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from beacon.utils.skill_config import SkillConfigError, load_yaml_like

REQUIRED_FIELDS = {
    "id",
    "cadence",
    "risk",
    "harness_skills",
    "state_surface",
    "phases",
    "human_gates",
    "token_cost",
    "daily_cap",
    "safety",
}
ALLOWED_RISKS = {"low", "medium", "high", "critical"}


def registry_path(project_root: Path, *, version: str) -> Path:
    return project_root.expanduser().resolve() / "docs" / "beacon" / version / "loop-patterns" / "registry.yaml"


def load_pattern_registry(path: Path) -> dict[str, Any]:
    try:
        payload = load_yaml_like(path)
    except (OSError, SkillConfigError) as exc:
        return {"status": "fail", "reason_code": "loop_pattern_registry_parse_error", "findings": [{"message": str(exc)}], "patterns": []}
    patterns = payload.get("patterns") if isinstance(payload.get("patterns"), list) else []
    return {"status": "loaded", "payload": payload, "patterns": [p for p in patterns if isinstance(p, dict)]}


def validate_pattern_registry(path: Path) -> dict[str, Any]:
    if not path.is_file():
        return {
            "schema_version": "1.0",
            "status": "missing",
            "reason_code": "loop_pattern_registry_missing",
            "path": str(path),
            "patterns": [],
            "findings": [{"reason_code": "loop_pattern_registry_missing", "message": "registry.yaml is missing"}],
        }
    loaded = load_pattern_registry(path)
    if loaded.get("status") == "fail":
        return {"schema_version": "1.0", "path": str(path), **loaded}
    patterns = list(loaded.get("patterns") or [])
    findings: list[dict[str, Any]] = []
    seen: set[str] = set()
    for index, pattern in enumerate(patterns):
        pattern_id = str(pattern.get("id") or "").strip()
        missing = sorted(field for field in REQUIRED_FIELDS if field not in pattern)
        if missing:
            findings.append(
                {
                    "reason_code": "loop_pattern_required_field_missing",
                    "index": index,
                    "pattern_id": pattern_id,
                    "fields": missing,
                }
            )
        if pattern_id:
            if pattern_id in seen:
                findings.append({"reason_code": "loop_pattern_duplicate_id", "pattern_id": pattern_id})
            seen.add(pattern_id)
        risk = str(pattern.get("risk") or "").strip().lower()
        if risk and risk not in ALLOWED_RISKS:
            findings.append({"reason_code": "loop_pattern_invalid_risk", "pattern_id": pattern_id, "risk": risk})
    status = "pass" if not findings else "fail"
    reason_code = str(findings[0].get("reason_code") or "") if findings else ""
    return {
        "schema_version": "1.0",
        "status": status,
        "reason_code": reason_code,
        "path": str(path),
        "pattern_count": len(patterns),
        "patterns": patterns,
        "pattern_ids": [str(p.get("id") or "") for p in patterns],
        "findings": findings,
    }
