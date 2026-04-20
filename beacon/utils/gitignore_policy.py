"""Beacon-managed .gitignore policy for local runtime/cache noise."""

from __future__ import annotations

import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Literal, TypedDict

GITIGNORE_MANAGED_START = "# BEACON:GITIGNORE:START"
GITIGNORE_MANAGED_END = "# BEACON:GITIGNORE:END"
GITIGNORE_VERSION_MARKER_FORMAT = "# BEACON:GITIGNORE:VERSION:{version}"

_VERSION_PATTERN = re.compile(r"^#\s*BEACON:GITIGNORE:VERSION:(.+?)\s*$", re.MULTILINE)

_MARKER_OK = "ok"
_MARKER_MISSING = "missing"
_MARKER_CORRUPTED = "corrupted"

STANDARD_BEACON_GITIGNORE_LINES = (
    "# Local orchestration scratch state",
    ".omx/",
    ".omc/",
    "",
    "# Beacon runtime scratch state that should not be committed by default",
    ".beacon/analysis/",
    ".beacon/debug/ideas/",
    ".beacon/debug/issues/",
    ".beacon/debug/runs/",
    ".beacon/iteration-governance/",
    ".beacon/ralph/",
    ".beacon/team/",
    ".beacon/handoffs/",
    ".beacon/state/checkpoints/",
    ".beacon/state/debug-feedback/",
    ".beacon/state/hud-hook/",
    ".beacon/state/input-audit/",
    ".beacon/state/skill-discovery/",
    ".beacon/state/team-hud/",
    ".beacon/state/workflow-hud/",
    ".beacon/validation/",
    "",
    "# Timestamped transient workflow runs",
    ".beacon/runs/run-20*/",
    "",
    "# Timestamped transient change-impact snapshots",
    ".beacon/state/change-impact/run-20*.json",
    "",
    "# Timestamped transient rolling baselines/spec fingerprints",
    ".beacon/state/baselines/v*/bl-run-20*.json",
    ".beacon/state/spec-fingerprints/v*/run-20*.json",
    "",
    "# Timestamped transient auto-test evidence, implement runs, and workflow memory snapshots",
    ".beacon/evidence/auto-test/run-20*/",
    ".beacon/implement/run-20*/",
    ".beacon/state/workflow-memory/run-20*/",
    ".beacon/evidence/qa-feature/*/tc-*/run-20*.json",
    ".beacon/handoffs/implement-to-qa/*/run-20*.json",
    "",
    "# Rolling local runtime state and evo experiment scratch",
    ".beacon/flaky-history.json",
    ".beacon/state/evo/experiments/evo-20*.json",
    ".beacon/state/evo/ledger.jsonl",
    ".beacon/state/requirement-clarity-*.json",
    ".beacon/state/technical-review-contract-*.json",
    ".beacon/state/exhaustion.json",
    "",
    "# Only explicitly promoted canonical QA and test-result surfaces stay tracked",
    ".beacon/evidence/test-results/*",
    "!.beacon/evidence/test-results/beacon-prototype-frontend-route-closure/",
    "!.beacon/evidence/test-results/beacon-prototype-frontend-route-closure/**",
    "!.beacon/evidence/test-results/beacon-qa-confidence-autoresearch-closure/",
    "!.beacon/evidence/test-results/beacon-qa-confidence-autoresearch-closure/**",
    "!.beacon/evidence/test-results/beacon-source-architecture-sync/",
    "!.beacon/evidence/test-results/beacon-source-architecture-sync/**",
    ".beacon/qa/features/*",
    "!.beacon/qa/features/beacon-qa-confidence-autoresearch-closure/",
    "!.beacon/qa/features/beacon-qa-confidence-autoresearch-closure/**",
    "",
    "# Local temp scratch",
    ".tmp/",
    "",
    "# Python cache noise",
    "__pycache__/",
    "*.py[cod]",
)


class MergeResult(TypedDict):
    content: str
    mode: Literal["created", "replaced", "prepended", "recovered"]


class GitignoreWriteResult(TypedDict):
    action: Literal["created", "updated", "unchanged", "planned"]
    changed: bool
    backup_path: str | None


class GitignoreCheck(TypedDict):
    name: Literal["beacon_gitignore_policy"]
    status: Literal["pass", "warn", "fail"]
    details: dict[str, object]


def _now_stamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S")


def beacon_gitignore_path(project_root: Path | str) -> Path:
    return Path(project_root) / ".gitignore"


def build_standard_beacon_gitignore_body() -> str:
    return "\n".join(STANDARD_BEACON_GITIGNORE_LINES).rstrip("\n")


def build_beacon_gitignore_block(runtime_version: str) -> str:
    body = build_standard_beacon_gitignore_body()
    return (
        f"{GITIGNORE_MANAGED_START}\n"
        f"{GITIGNORE_VERSION_MARKER_FORMAT.format(version=runtime_version)}\n"
        f"{body}\n"
        f"{GITIGNORE_MANAGED_END}\n"
    )


def _marker_integrity(content: str) -> Literal["ok", "missing", "corrupted"]:
    start_count = content.count(GITIGNORE_MANAGED_START)
    end_count = content.count(GITIGNORE_MANAGED_END)
    if start_count == 0 and end_count == 0:
        return _MARKER_MISSING
    if start_count == 1 and end_count == 1:
        start_idx = content.find(GITIGNORE_MANAGED_START)
        end_idx = content.find(GITIGNORE_MANAGED_END)
        if start_idx != -1 and end_idx != -1 and start_idx < end_idx:
            return _MARKER_OK
    return _MARKER_CORRUPTED


def _extract_version_marker(content: str) -> str | None:
    match = _VERSION_PATTERN.search(content)
    if not match:
        return None
    value = match.group(1).strip()
    return value or None


def _extract_managed_block_content(content: str) -> str:
    start_idx = content.find(GITIGNORE_MANAGED_START)
    end_idx = content.find(GITIGNORE_MANAGED_END)
    if start_idx == -1 or end_idx == -1 or end_idx < start_idx:
        return ""
    end_idx += len(GITIGNORE_MANAGED_END)
    return content[start_idx:end_idx].strip()


def merge_beacon_gitignore(existing_content: str, managed_block: str) -> MergeResult:
    current = existing_content or ""
    if not current.strip():
        return {"content": managed_block, "mode": "created"}

    integrity = _marker_integrity(current)
    if integrity == _MARKER_OK:
        start_idx = current.find(GITIGNORE_MANAGED_START)
        end_idx = current.find(GITIGNORE_MANAGED_END) + len(GITIGNORE_MANAGED_END)
        prefix = current[:start_idx]
        suffix = current[end_idx:]
        merged = f"{prefix}{managed_block}{suffix}".strip("\n") + "\n"
        return {"content": merged, "mode": "replaced"}

    merged = f"{managed_block.rstrip()}\n\n{current.strip()}\n"
    if integrity == _MARKER_MISSING:
        return {"content": merged, "mode": "prepended"}
    return {"content": merged, "mode": "recovered"}


def _write_gitignore(path: Path, content: str, *, dry_run: bool = False) -> GitignoreWriteResult:
    exists = path.exists()
    current = path.read_text(encoding="utf-8") if exists else ""
    if current == content:
        return {"action": "unchanged", "changed": False, "backup_path": None}
    if dry_run:
        return {"action": "planned", "changed": True, "backup_path": None}

    path.parent.mkdir(parents=True, exist_ok=True)
    backup_path: str | None = None
    if exists:
        backup = path.with_name(f"{path.name}.bak-{_now_stamp()}")
        backup.write_text(current, encoding="utf-8")
        backup_path = str(backup)
    path.write_text(content, encoding="utf-8")
    return {
        "action": "updated" if exists else "created",
        "changed": True,
        "backup_path": backup_path,
    }


def setup_beacon_gitignore(
    project_root: Path | str,
    *,
    runtime_version: str,
    dry_run: bool = False,
) -> dict[str, object]:
    root = Path(project_root)
    path = beacon_gitignore_path(root)
    current = path.read_text(encoding="utf-8") if path.exists() else ""
    managed_block = build_beacon_gitignore_block(runtime_version)
    merge_result = merge_beacon_gitignore(current, managed_block)
    write_result = _write_gitignore(path, merge_result["content"], dry_run=dry_run)
    return {
        "path": str(path),
        "runtime_version": runtime_version,
        "merge_mode": merge_result["mode"],
        **write_result,
    }


def verify_beacon_gitignore(
    project_root: Path | str,
    *,
    runtime_version: str,
) -> GitignoreCheck:
    root = Path(project_root)
    path = beacon_gitignore_path(root)
    if not path.exists():
        return {
            "name": "beacon_gitignore_policy",
            "status": "warn",
            "details": {
                "path": str(path),
                "exists": False,
                "marker_integrity": _MARKER_MISSING,
                "managed_version": None,
                "version_drift": None,
                "block_matches_standard": False,
                "recommended_command": "beacon doctor sync-gitignore --project-root .",
            },
        }

    content = path.read_text(encoding="utf-8")
    integrity = _marker_integrity(content)
    managed_version = _extract_version_marker(content)
    version_drift = None if managed_version is None else managed_version != runtime_version
    current_block = _extract_managed_block_content(content)
    expected_block = build_beacon_gitignore_block(runtime_version).strip()
    block_matches = current_block == expected_block

    status: Literal["pass", "warn", "fail"] = "pass"
    if integrity == _MARKER_CORRUPTED or (integrity == _MARKER_OK and not block_matches):
        status = "fail"
    elif integrity != _MARKER_OK or version_drift:
        status = "warn"

    return {
        "name": "beacon_gitignore_policy",
        "status": status,
        "details": {
            "path": str(path),
            "exists": True,
            "marker_integrity": integrity,
            "managed_version": managed_version,
            "version_drift": version_drift,
            "block_matches_standard": block_matches,
            "recommended_command": "beacon doctor sync-gitignore --project-root .",
        },
    }
