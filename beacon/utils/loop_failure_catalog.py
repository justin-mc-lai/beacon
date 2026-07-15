"""Loop failure-mode catalog parsing and validation."""

from __future__ import annotations

from pathlib import Path
from typing import Any

REQUIRED_FIELDS = {"id", "severity", "symptom", "cause", "mitigation", "route", "evidence_expectation"}
ALLOWED_SEVERITIES = {"S1", "S2", "S3"}
BASELINE_MODE_IDS = {
    "truth-drift",
    "git-alignment-blocked",
    "stale-evidence-manifest",
    "infinite-fix-loop",
    "protected-path-attempt",
}


def catalog_path(project_root: Path, *, version: str) -> Path:
    return project_root.expanduser().resolve() / "docs" / "beacon" / version / "execution" / "loop-failure-modes.md"


def parse_failure_catalog(text: str) -> list[dict[str, str]]:
    entries: list[dict[str, str]] = []
    current: dict[str, str] | None = None
    for line in text.splitlines():
        stripped = line.strip()
        if stripped.startswith("### "):
            if current:
                entries.append(current)
            current = {}
            title = stripped[4:].strip()
            if title and ":" not in title:
                current["id"] = title
            continue
        if current is None or not stripped.startswith("- ") or ":" not in stripped:
            continue
        key, value = stripped[2:].split(":", 1)
        normalized_key = key.strip().lower().replace(" ", "_").replace("-", "_")
        current[normalized_key] = value.strip()
    if current:
        entries.append(current)
    return entries


def validate_failure_catalog(path: Path) -> dict[str, Any]:
    if not path.is_file():
        return {
            "schema_version": "1.0",
            "status": "missing",
            "reason_code": "loop_failure_mode_catalog_missing",
            "path": str(path),
            "entries": [],
            "findings": [{"reason_code": "loop_failure_mode_catalog_missing", "message": "catalog is missing"}],
        }
    text = path.read_text(encoding="utf-8")
    entries = parse_failure_catalog(text)
    findings: list[dict[str, Any]] = []
    for index, entry in enumerate(entries):
        mode_id = str(entry.get("id") or "").strip()
        missing = sorted(field for field in REQUIRED_FIELDS if not str(entry.get(field) or "").strip())
        if missing:
            findings.append({"reason_code": "loop_failure_mode_required_field_missing", "index": index, "id": mode_id, "fields": missing})
        severity = str(entry.get("severity") or "").strip()
        if severity and severity not in ALLOWED_SEVERITIES:
            findings.append({"reason_code": "loop_failure_mode_invalid_severity", "id": mode_id, "severity": severity})
    ids = {str(entry.get("id") or "").strip() for entry in entries}
    missing_baseline = sorted(BASELINE_MODE_IDS - ids)
    if missing_baseline:
        findings.append({"reason_code": "loop_failure_mode_baseline_missing", "ids": missing_baseline})
    status = "pass" if not findings else "fail"
    return {
        "schema_version": "1.0",
        "status": status,
        "reason_code": str(findings[0].get("reason_code") or "") if findings else "",
        "path": str(path),
        "entry_count": len(entries),
        "entries": entries,
        "mode_ids": sorted(ids),
        "findings": findings,
    }
