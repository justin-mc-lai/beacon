"""Skill drift checks for repo vs local Claude/Codex installs."""

from __future__ import annotations

import hashlib
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _file_check(name: str, expected: Path, actual: Path) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "name": name,
        "kind": "file",
        "expected_path": str(expected),
        "actual_path": str(actual),
    }
    if not expected.exists():
        payload["status"] = "missing_source"
        return payload
    payload["expected_sha256"] = _sha256(expected)
    if not actual.exists():
        payload["status"] = "missing_target"
        return payload
    payload["actual_sha256"] = _sha256(actual)
    payload["status"] = "match" if payload["expected_sha256"] == payload["actual_sha256"] else "drift"
    return payload


def _dir_manifest(root: Path) -> dict[str, str]:
    manifest: dict[str, str] = {}
    if not root.exists():
        return manifest
    for path in sorted(root.rglob("*")):
        if not path.is_file():
            continue
        if "__pycache__" in path.parts:
            continue
        manifest[str(path.relative_to(root))] = _sha256(path)
    return manifest


def _dir_check(name: str, expected: Path, actual: Path) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "name": name,
        "kind": "directory",
        "expected_path": str(expected),
        "actual_path": str(actual),
    }
    if not expected.exists():
        payload["status"] = "missing_source"
        return payload
    if not actual.exists():
        payload["status"] = "missing_target"
        return payload
    expected_manifest = _dir_manifest(expected)
    actual_manifest = _dir_manifest(actual)
    missing = sorted(path for path in expected_manifest if path not in actual_manifest)
    unexpected = sorted(path for path in actual_manifest if path not in expected_manifest)
    drift = sorted(
        path
        for path, digest in expected_manifest.items()
        if path in actual_manifest and actual_manifest[path] != digest
    )
    payload["expected_file_count"] = len(expected_manifest)
    payload["actual_file_count"] = len(actual_manifest)
    payload["missing_files"] = missing
    payload["unexpected_files"] = unexpected
    payload["drift_files"] = drift
    payload["status"] = "match" if not missing and not unexpected and not drift else "drift"
    return payload


def build_skill_drift_report(project_root: Path, *, home: Path | None = None) -> dict[str, Any]:
    root = project_root.resolve()
    user_home = (home or Path.home()).resolve()
    checks = [
        _file_check(
            "repo_root_vs_claude_root",
            root / "SKILL.md",
            user_home / ".claude" / "skills" / "beacon" / "SKILL.md",
        ),
        _dir_check(
            "repo_packaged_vs_claude_packaged",
            root / "skills" / "beacon",
            user_home / ".claude" / "skills" / "beacon" / "skills" / "beacon",
        ),
        _dir_check(
            "repo_packaged_vs_codex_packaged",
            root / "skills" / "beacon",
            user_home / ".codex" / "skills" / "beacon",
        ),
    ]
    drift_count = len([item for item in checks if str(item.get("status")) == "drift"])
    missing_count = len([item for item in checks if str(item.get("status", "")).startswith("missing_")])
    return {
        "schema_version": "1.0",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "project_root": str(root),
        "home": str(user_home),
        "status": "pass" if drift_count == 0 and missing_count == 0 else "fail",
        "drift_count": drift_count,
        "missing_count": missing_count,
        "checks": checks,
    }
