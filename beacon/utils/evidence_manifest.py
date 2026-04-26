"""Evidence manifest validation helpers for release-facing surfaces."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any


_ROLLING_POINTER_PREFIXES = (
    ".beacon/state/spec-fingerprints/",
    ".beacon/state/baselines/",
)


def _issue(reason_code: str, message: str, *, blocked: bool, severity: str) -> dict[str, Any]:
    return {
        "reason_code": reason_code,
        "severity": severity,
        "message": message,
        "blocked": blocked,
    }


def validate_evidence_manifest(project_root: Path) -> dict[str, Any]:
    """Validate `.beacon/evidence-manifest.json` against the current worktree."""
    manifest_path = project_root / ".beacon" / "evidence-manifest.json"
    if not manifest_path.exists():
        issues = [
            _issue(
                "evidence_sha256_manifest_missing",
                f"evidence-manifest not found at {manifest_path}",
                blocked=True,
                severity="critical",
            )
        ]
        return {
            "status": "blocked",
            "blocked": True,
            "blocked_count": 1,
            "entry_count": 0,
            "issues": issues,
        }

    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    except Exception as exc:  # noqa: BLE001
        issues = [
            _issue(
                "evidence_sha256_manifest_invalid",
                f"evidence-manifest is not valid JSON: {exc}",
                blocked=True,
                severity="critical",
            )
        ]
        return {
            "status": "blocked",
            "blocked": True,
            "blocked_count": 1,
            "entry_count": 0,
            "issues": issues,
        }

    entries = manifest.get("entries")
    if entries is None:
        entries = manifest.get("items")
    if not isinstance(entries, list):
        issues = [
            _issue(
                "evidence_sha256_manifest_invalid",
                "evidence-manifest missing list field: entries/items",
                blocked=True,
                severity="critical",
            )
        ]
        return {
            "status": "blocked",
            "blocked": True,
            "blocked_count": 1,
            "entry_count": 0,
            "issues": issues,
        }

    issues: list[dict[str, Any]] = []
    for entry in entries:
        if not isinstance(entry, dict):
            issues.append(
                _issue(
                    "evidence_sha256_manifest_incomplete",
                    f"evidence-manifest entry is not object: {entry}",
                    blocked=False,
                    severity="medium",
                )
            )
            continue

        rel_path = str(entry.get("path", "")).strip()
        sha256 = str(entry.get("sha256", "")).strip()
        if not rel_path or not sha256:
            issues.append(
                _issue(
                    "evidence_sha256_manifest_incomplete",
                    f"evidence-manifest entry missing sha256 or path: {entry}",
                    blocked=False,
                    severity="medium",
                )
            )
            continue

        if rel_path.startswith("/") or "\\" in rel_path:
            issues.append(
                _issue(
                    "evidence_ref_path_style_inconsistent",
                    f"evidence path should be project-relative POSIX style: {rel_path}",
                    blocked=False,
                    severity="medium",
                )
            )
            continue

        if rel_path.endswith("/latest.json") and rel_path.startswith(_ROLLING_POINTER_PREFIXES):
            continue

        file_path = project_root / rel_path
        if not file_path.exists():
            issues.append(
                _issue(
                    "evidence_sha256_manifest_mismatch",
                    f"evidence file missing: {rel_path}",
                    blocked=True,
                    severity="critical",
                )
            )
            continue

        file_hash = hashlib.sha256(file_path.read_bytes()).hexdigest()
        if file_hash != sha256:
            issues.append(
                _issue(
                    "evidence_sha256_manifest_mismatch",
                    f"Hash mismatch for {rel_path}",
                    blocked=True,
                    severity="critical",
                )
            )

    blocked_count = len([item for item in issues if bool(item.get("blocked"))])
    status = "blocked" if blocked_count else ("warn" if issues else "pass")
    return {
        "status": status,
        "blocked": blocked_count > 0,
        "blocked_count": blocked_count,
        "entry_count": len(entries),
        "issues": issues,
    }
