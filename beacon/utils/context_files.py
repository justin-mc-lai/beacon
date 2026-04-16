"""Managed context file helpers for Beacon."""

from __future__ import annotations

import re
from datetime import datetime
from pathlib import Path
from typing import Literal, TypedDict

MANAGED_BLOCK_START = "<!-- BEACON:START -->"
MANAGED_BLOCK_END = "<!-- BEACON:END -->"
MANAGED_VERSION_MARKER_FORMAT = "<!-- BEACON:VERSION:{version} -->"

_MARKER_VERSION_PATTERN = re.compile(r"<!--\s*BEACON:VERSION:([^>\s]+)\s*-->")

_MARKER_OK = "ok"
_MARKER_MISSING = "missing"
_MARKER_CORRUPTED = "corrupted"

_USER_CUSTOMIZATION_HEADER = "## User Customization (preserved by Beacon)"


class MergeResult(TypedDict):
    content: str
    mode: Literal["created", "replaced", "prepended", "recovered"]


class WriteActionInfo(TypedDict):
    action: Literal["created", "updated", "unchanged", "planned"]
    changed: bool
    backup_path: str | None


class ContextFileInspection(TypedDict):
    path: str
    exists: bool
    marker_integrity: Literal["ok", "missing", "corrupted"]
    managed_version: str | None
    version_drift: bool | None


class VerificationCheck(TypedDict):
    name: Literal[
        "context_files_presence",
        "managed_block_integrity",
        "managed_block_version_drift",
        "global_boundaries_presence",
        "global_boundaries_inheritance",
    ]
    status: Literal["pass", "warn", "fail"]
    details: dict[str, object]


def build_claude_guidance_body(runtime_version: str) -> str:
    """Build managed CLAUDE.md guidance body."""
    return (
        "# CLAUDE.md\n\n"
        "This file is Beacon-managed runtime guidance.\n\n"
        "## Beacon usage\n"
        "- Use Beacon commands for product workflow execution.\n"
        "- Keep outputs evidence-first and machine-readable when possible.\n"
        "- Prefer `beacon <subcommand>` form for cross-environment stability.\n\n"
        "## Key commands\n"
        "- `beacon init --apply`\n"
        "- `beacon doctor setup-context --project-root .`\n"
        "- `beacon doctor verify-context --project-root . --strict`\n"
        "- `beacon doctor sync-materials --project-root . --version <version> --all-features`\n"
        "- `beacon workflow start \"<feature>\" --version <version> --project-root .`\n"
        "- `beacon skill list`\n"
        "- `beacon implement list-runners --json`\n"
        "- `beacon implement run \"<feature>\" --version <version> --runner <runner>`\n"
        "- `beacon workflow --help`\n"
        "- `beacon status --verbose`\n\n"
        "## Requirement materials and docs paths\n"
        f"- Runtime target version: `{runtime_version}`\n"
        "- `docs/beacon/global-boundaries.md` is the canonical cross-version global constraint source.\n"
        "- `docs/beacon/<version>/` is the canonical source of truth.\n"
        "- `docs/beacon/<version>/SUMMARY.md`\n"
        "- `docs/beacon/<version>/prd/`\n"
        "- `docs/beacon/<version>/user-story/`\n"
        "- `docs/beacon/<version>/qa/test-cases/`\n"
        "- `docs/beacon/<version>/execution/`\n"
    )


def build_agents_guidance_body(runtime_version: str) -> str:
    """Build managed AGENTS.md guidance body."""
    return (
        "# AGENTS.md\n\n"
        "This file is Beacon-managed agent operation guidance.\n\n"
        "## Agent behavior\n"
        "- Keep scope tight and implement the smallest correct change.\n"
        "- Verify diagnostics/tests before claiming completion.\n"
        "- Preserve user-authored sections outside Beacon managed blocks.\n\n"
        "## Beacon requirement-material usage\n"
        f"- Runtime target version: `{runtime_version}`\n"
        "- Use `docs/beacon/global-boundaries.md` as the canonical Beacon-wide global constraint source.\n"
        "- Use `docs/beacon/<version>/` as the canonical delivery tree.\n"
        "- Read progressively in this order:\n"
        "  1. `docs/beacon/global-boundaries.md`\n"
        "  2. `docs/beacon/<version>/SUMMARY.md`\n"
        "  3. `docs/beacon/<version>/execution/index.md`\n"
        "  4. `docs/beacon/<version>/execution/architecture-blueprint.md`\n"
        "  5. `docs/beacon/<version>/prd/`, `user-story/`, `qa/test-cases/`\n"
        "  6. `docs/beacon/<version>/.machine/`\n"
        "- For greenfield projects: start with architecture blueprint, then enter think → user-story → prd.\n"
        "- For takeover projects: document current-state architecture, service map, constraints, and version timeline before new implementation.\n"
        "- If context blocks are missing/corrupted, run:\n"
        "  - `beacon doctor setup-context --project-root .`\n"
        "  - `beacon doctor verify-context --project-root . --strict`\n"
        "- After runtime/version upgrades on a real project, sync machine requirement materials before QA:\n"
        "  - `beacon doctor sync-materials --project-root . --version <version> --all-features`\n"
    )


def build_managed_block(body: str, runtime_version: str) -> str:
    """Build a full managed block for insertion/merge."""
    body_text = body.rstrip("\n")
    return (
        f"{MANAGED_BLOCK_START}\n"
        f"{MANAGED_VERSION_MARKER_FORMAT.format(version=runtime_version)}\n"
        f"{body_text}\n"
        f"{MANAGED_BLOCK_END}\n"
    )


def build_default_claude_managed_block(runtime_version: str) -> str:
    return build_managed_block(build_claude_guidance_body(runtime_version), runtime_version)


def build_default_agents_managed_block(runtime_version: str) -> str:
    return build_managed_block(build_agents_guidance_body(runtime_version), runtime_version)


def _marker_integrity(content: str) -> Literal["ok", "missing", "corrupted"]:
    start_count = content.count(MANAGED_BLOCK_START)
    end_count = content.count(MANAGED_BLOCK_END)

    if start_count == 0 and end_count == 0:
        return _MARKER_MISSING

    if start_count == 1 and end_count == 1:
        start_idx = content.find(MANAGED_BLOCK_START)
        end_idx = content.find(MANAGED_BLOCK_END)
        if start_idx != -1 and end_idx != -1 and start_idx < end_idx:
            return _MARKER_OK

    return _MARKER_CORRUPTED


def _extract_version_marker(content: str) -> str | None:
    match = _MARKER_VERSION_PATTERN.search(content)
    if not match:
        return None
    return match.group(1).strip() or None


def _build_user_customization_section(content: str) -> str:
    preserved = content.strip("\n")
    if not preserved:
        return ""
    return f"\n{_USER_CUSTOMIZATION_HEADER}\n\n{preserved}\n"


def merge_managed_block(existing_content: str, managed_block: str) -> MergeResult:
    """Merge a managed block into existing content with idempotent behavior."""
    current = existing_content or ""
    if not current.strip():
        return {"content": managed_block, "mode": "created"}

    integrity = _marker_integrity(current)
    if integrity == _MARKER_OK:
        start_idx = current.find(MANAGED_BLOCK_START)
        end_idx = current.find(MANAGED_BLOCK_END) + len(MANAGED_BLOCK_END)
        prefix = current[:start_idx]
        suffix = current[end_idx:]
        merged = f"{prefix}{managed_block}{suffix}"
        return {"content": merged, "mode": "replaced"}

    if integrity == _MARKER_MISSING:
        merged = f"{managed_block}{_build_user_customization_section(current)}"
        return {"content": merged, "mode": "prepended"}

    merged = f"{managed_block}{_build_user_customization_section(current)}"
    return {"content": merged, "mode": "recovered"}


def write_context_file(
    path: Path,
    content: str,
    *,
    dry_run: bool = False,
) -> WriteActionInfo:
    """Write managed content with timestamp backup when updates are needed."""
    exists = path.exists()
    current = path.read_text(encoding="utf-8") if exists else ""

    if current == content:
        return {"action": "unchanged", "changed": False, "backup_path": None}

    if dry_run:
        return {"action": "planned", "changed": True, "backup_path": None}

    path.parent.mkdir(parents=True, exist_ok=True)

    backup_path: str | None = None
    if exists:
        timestamp = datetime.utcnow().strftime("%Y%m%d%H%M%S")
        backup = path.with_name(f"{path.name}.bak-{timestamp}")
        backup.write_text(current, encoding="utf-8")
        backup_path = str(backup)

    path.write_text(content, encoding="utf-8")
    action: Literal["created", "updated"] = "updated" if exists else "created"
    return {"action": action, "changed": True, "backup_path": backup_path}


def inspect_context_file(path: Path, runtime_version: str) -> ContextFileInspection:
    """Inspect file presence, marker integrity, version marker and drift."""
    exists = path.exists()
    if not exists:
        return {
            "path": str(path),
            "exists": False,
            "marker_integrity": _MARKER_MISSING,
            "managed_version": None,
            "version_drift": None,
        }

    content = path.read_text(encoding="utf-8")
    integrity = _marker_integrity(content)
    managed_version = _extract_version_marker(content)
    version_drift = None if managed_version is None else (managed_version != runtime_version)

    return {
        "path": str(path),
        "exists": True,
        "marker_integrity": integrity,
        "managed_version": managed_version,
        "version_drift": version_drift,
    }


def setup_context_files(
    project_root: Path | str,
    runtime_version: str,
    dry_run: bool,
    force: bool,
    with_claude: bool,
    with_agents: bool,
) -> dict[str, object]:
    """Setup or update CLAUDE.md / AGENTS.md managed blocks."""
    root = Path(project_root)
    actions: list[dict[str, object]] = []
    from beacon.utils.global_boundaries import GLOBAL_BOUNDARIES_RELATIVE_PATH, sync_project_global_boundaries

    targets: list[tuple[str, Path, str]] = []
    if with_claude:
        targets.append(("CLAUDE.md", root / "CLAUDE.md", build_default_claude_managed_block(runtime_version)))
    if with_agents:
        targets.append(("AGENTS.md", root / "AGENTS.md", build_default_agents_managed_block(runtime_version)))

    for file_name, file_path, managed_block in targets:
        current = file_path.read_text(encoding="utf-8") if file_path.exists() else ""
        merge_result = merge_managed_block(current, managed_block)
        write_result = write_context_file(file_path, merge_result["content"], dry_run=dry_run)
        actions.append(
            {
                "file": file_name,
                "path": str(file_path),
                "force": force,
                "merge_mode": merge_result["mode"],
                **write_result,
            }
        )

    global_boundaries_result = sync_project_global_boundaries(root, dry_run=dry_run)
    actions.append(
        {
            "file": GLOBAL_BOUNDARIES_RELATIVE_PATH.name,
            "path": str(global_boundaries_result.get("path", "")),
            "force": False,
            "merge_mode": "copied",
            "action": str(global_boundaries_result.get("action", "updated")),
            "changed": bool(global_boundaries_result.get("changed", False)),
            "backup_path": global_boundaries_result.get("backup_path"),
        }
    )

    return {
        "project_root": str(root),
        "runtime_version": runtime_version,
        "dry_run": dry_run,
        "force": force,
        "actions": actions,
    }


def verify_context_files(
    project_root: Path | str,
    runtime_version: str,
    strict: bool,
) -> dict[str, object]:
    """Verify context files presence, marker integrity and version drift."""
    root = Path(project_root)
    from beacon.utils.global_boundaries import path_mentions_global_boundaries, project_global_boundaries_path
    inspections = {
        "CLAUDE.md": inspect_context_file(root / "CLAUDE.md", runtime_version),
        "AGENTS.md": inspect_context_file(root / "AGENTS.md", runtime_version),
    }
    global_boundaries_path = project_global_boundaries_path(root)

    missing_files = [name for name, info in inspections.items() if not info["exists"]]
    integrity_issues = [name for name, info in inspections.items() if info["marker_integrity"] != _MARKER_OK]
    drift_files = [name for name, info in inspections.items() if info["version_drift"] is True]
    unknown_drift = [name for name, info in inspections.items() if info["version_drift"] is None]
    missing_global_boundaries_refs = [
        name for name in ("CLAUDE.md", "AGENTS.md") if inspections.get(name, {}).get("exists") and not path_mentions_global_boundaries(root / name, project_root=root)
    ]

    drift_status: Literal["pass", "warn", "fail"] = "pass"
    if drift_files:
        drift_status = "fail" if strict else "warn"
    elif unknown_drift:
        drift_status = "fail" if strict else "warn"

    checks: list[VerificationCheck] = [
        {
            "name": "context_files_presence",
            "status": "pass" if not missing_files else "fail",
            "details": {"missing": missing_files},
        },
        {
            "name": "managed_block_integrity",
            "status": "pass" if not integrity_issues else "fail",
            "details": {"issues": integrity_issues},
        },
        {
            "name": "managed_block_version_drift",
            "status": drift_status,
            "details": {
                "drifted": drift_files,
                "unknown": unknown_drift,
            },
        },
        {
            "name": "global_boundaries_presence",
            "status": "pass" if global_boundaries_path.exists() else "fail",
            "details": {"path": str(global_boundaries_path), "exists": global_boundaries_path.exists()},
        },
        {
            "name": "global_boundaries_inheritance",
            "status": "pass" if not missing_global_boundaries_refs else ("fail" if strict else "warn"),
            "details": {"missing_references": missing_global_boundaries_refs},
        },
    ]

    overall_status: Literal["pass", "warn", "fail"] = "pass"
    if any(check["status"] == "fail" for check in checks):
        overall_status = "fail"
    elif any(check["status"] == "warn" for check in checks):
        overall_status = "warn"

    return {
        "project_root": str(root),
        "runtime_version": runtime_version,
        "strict": strict,
        "status": overall_status,
        "ok": overall_status != "fail",
        "checks": checks,
        "files": inspections,
    }
