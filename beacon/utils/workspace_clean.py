"""Workspace clean-exit gate for Beacon lifecycle boundaries."""

from __future__ import annotations

import fnmatch
import hashlib
import json
import subprocess
from pathlib import Path
from typing import Any

from beacon.utils.runtime import now_iso
from beacon.utils.story_state import feature_slug


SCHEMA_VERSION = "workspace-clean-exit-gate.v1"

REASON_UNCLASSIFIED = "workspace_dirty_unclassified"
REASON_FORBIDDEN = "workspace_dirty_forbidden"
REASON_REQUIRES_RESOLUTION = "workspace_dirty_requires_resolution"
REASON_SKIP_HIDDEN = "skip_worktree_hidden_dirty"
REASON_RUNTIME_NOT_FORMAL = "runtime_evidence_not_formal"
REASON_FORMAL_UNTRACKED = "formal_evidence_untracked"
REASON_FORMAL_HASH = "formal_evidence_hash_mismatch"
REASON_TASK_EVIDENCE = "task_evidence_unpromoted"
REASON_ORPHAN_EVIDENCE = "orphan_evidence_unpromoted"
REASON_HOST_POLICY = "host_projection_requires_policy"


DIRTY_MANIFEST: dict[str, dict[str, Any]] = {
    "canonical_truth": {
        "allowed_actions": ["commit"],
        "patterns": [
            "docs/beacon/*/features/*/truth.md",
            "docs/beacon/*/features/*/tests.md",
            "docs/beacon/*/features/*/tasks.md",
            "docs/beacon/*/features/*/evidence.md",
        ],
    },
    "formal_evidence": {
        "allowed_actions": ["commit", "promote"],
        "patterns": [
            ".beacon/evidence/implement/**",
            ".beacon/evidence/test-results/**",
            "docs/beacon/*/qa/**",
        ],
    },
    "machine_projection": {
        "allowed_actions": ["commit", "regenerate"],
        "patterns": [
            "docs/beacon/*/.machine/**",
            "docs/beacon/*/execution/**",
            "docs/beacon/.machine/**",
            "beacon.egg-info/**",
        ],
    },
    "host_projection": {
        "allowed_actions": ["ignore", "skip-worktree", "surface-sync commit"],
        "patterns": [
            ".agents/**",
            ".codex/**",
            ".cursor/**",
            ".trae/**",
            ".windsurf/**",
            "AGENTS.md",
            "CLAUDE.md",
        ],
    },
    "runtime_private": {
        "allowed_actions": ["ignore", "quarantine", "promote redacted digest"],
        "patterns": [
            ".beacon/traces/**",
            ".beacon/state/**",
            ".beacon/memory/**",
            ".beacon/tasks/**",
            ".beacon/release-gate-report.json",
            ".beacon/evidence-manifest.json",
            ".beacon/raw-command-log.jsonl",
        ],
    },
    "forbidden": {
        "allowed_actions": ["remove", "rotate-secret"],
        "patterns": [
            ".env",
            ".env.*",
            "**/*.pem",
            "**/*.key",
            "**/id_rsa",
        ],
    },
}


def _run_git(project_root: Path, args: list[str], *, text: bool = True) -> subprocess.CompletedProcess[Any]:
    return subprocess.run(["git", *args], cwd=project_root, check=False, capture_output=True, text=text)


def _git_root(project_root: Path) -> Path:
    result = _run_git(project_root, ["rev-parse", "--show-toplevel"])
    if result.returncode != 0:
        raise ValueError((result.stderr or "").strip() or "not a git repository")
    return Path(str(result.stdout).strip()).resolve()


def _rel(path: Path, root: Path) -> str:
    return path.resolve().relative_to(root.resolve()).as_posix()


def _matches(path: str, patterns: list[str]) -> bool:
    return any(fnmatch.fnmatchcase(path, pattern) for pattern in patterns)


def artifact_role_for_path(path: str) -> str:
    normalized = str(path or "").strip().replace("\\", "/")
    for role in ("forbidden", "canonical_truth", "formal_evidence", "machine_projection", "host_projection", "runtime_private"):
        if _matches(normalized, list(DIRTY_MANIFEST[role]["patterns"])):
            return role
    return "unclassified"


def _parse_porcelain_line(line: str) -> dict[str, Any] | None:
    if not line:
        return None
    status = line[:2]
    path = line[3:] if len(line) > 3 else ""
    if " -> " in path:
        path = path.split(" -> ", 1)[1]
    path = path.strip().strip('"')
    if not path:
        return None
    role = artifact_role_for_path(path)
    return {
        "path": path,
        "xy": status,
        "artifact_role": role,
        "allowed_actions": list(DIRTY_MANIFEST.get(role, {}).get("allowed_actions", [])),
    }


def collect_dirty_entries(project_root: Path) -> list[dict[str, Any]]:
    root = _git_root(project_root)
    result = _run_git(root, ["status", "--porcelain=v1", "-uall"])
    if result.returncode != 0:
        raise RuntimeError((result.stderr or "").strip() or "git status failed")
    entries: list[dict[str, Any]] = []
    for line in str(result.stdout).splitlines():
        parsed = _parse_porcelain_line(line)
        if parsed:
            entries.append(parsed)
    return entries


def _tracked_paths(project_root: Path) -> set[str]:
    root = _git_root(project_root)
    result = _run_git(root, ["ls-files"])
    if result.returncode != 0:
        return set()
    return {line.strip() for line in str(result.stdout).splitlines() if line.strip()}


def _is_tracked(project_root: Path, rel_path: str) -> bool:
    root = _git_root(project_root)
    result = _run_git(root, ["ls-files", "--error-unmatch", "--", rel_path])
    return result.returncode == 0


def _skip_worktree_paths(project_root: Path) -> list[str]:
    root = _git_root(project_root)
    result = _run_git(root, ["ls-files", "-v"])
    if result.returncode != 0:
        return []
    paths: list[str] = []
    for line in str(result.stdout).splitlines():
        if len(line) >= 3 and line[0] == "S" and line[1] == " ":
            paths.append(line[2:])
    return sorted(paths)


def detect_skip_worktree_hidden_dirty(project_root: Path) -> list[dict[str, Any]]:
    root = _git_root(project_root)
    hidden: list[dict[str, Any]] = []
    for rel_path in _skip_worktree_paths(root):
        file_path = root / rel_path
        current = file_path.read_bytes() if file_path.exists() else None
        head = subprocess.run(
            ["git", "show", f"HEAD:{rel_path}"],
            cwd=root,
            check=False,
            capture_output=True,
            text=False,
        )
        head_bytes = head.stdout if head.returncode == 0 else None
        if current != head_bytes:
            hidden.append(
                {
                    "path": rel_path,
                    "reason_code": REASON_SKIP_HIDDEN,
                    "artifact_role": artifact_role_for_path(rel_path),
                    "message": "skip-worktree path differs from HEAD and cannot be used as clean proof",
                }
            )
    return hidden


def collect_workspace_snapshot(project_root: Path) -> dict[str, Any]:
    root = _git_root(project_root)
    branch = _run_git(root, ["rev-parse", "--abbrev-ref", "HEAD"])
    head = _run_git(root, ["rev-parse", "--short", "HEAD"])
    dirty_entries = collect_dirty_entries(root)
    return {
        "schema_version": "workspace-snapshot.v1",
        "project_root": str(root),
        "git_head": str(head.stdout).strip() if head.returncode == 0 else "",
        "branch": str(branch.stdout).strip() if branch.returncode == 0 else "",
        "dirty_entries": dirty_entries,
        "dirty_paths": [entry["path"] for entry in dirty_entries],
        "dirty_count": len(dirty_entries),
        "captured_at": now_iso(),
    }


def compare_snapshot_dirty_paths(before: dict[str, Any], after: dict[str, Any]) -> dict[str, Any]:
    before_paths = {str(path) for path in before.get("dirty_paths", [])}
    after_paths = {str(path) for path in after.get("dirty_paths", [])}
    added = sorted(after_paths - before_paths)
    removed = sorted(before_paths - after_paths)
    return {
        "schema_version": "workspace-snapshot-delta.v1",
        "tracked_dirty_added": added,
        "tracked_dirty_removed": removed,
        "tracked_dirty_added_count": len(added),
        "tracked_dirty_removed_count": len(removed),
    }


def _manifest_entries(project_root: Path) -> list[dict[str, Any]]:
    payload = _load_evidence_manifest(project_root)
    entries = payload.get("entries") if isinstance(payload, dict) else []
    return [entry for entry in entries if isinstance(entry, dict)] if isinstance(entries, list) else []


def _load_evidence_manifest(project_root: Path) -> dict[str, Any]:
    path = project_root / ".beacon" / "evidence-manifest.json"
    if not path.is_file():
        return {}
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}
    return payload if isinstance(payload, dict) else {}


def validate_formal_evidence_manifest(project_root: Path) -> dict[str, Any]:
    root = _git_root(project_root)
    manifest = _load_evidence_manifest(root)
    manifest_role = str(manifest.get("manifest_role") or manifest.get("authority") or "").strip()
    entries = [entry for entry in manifest.get("entries", []) if isinstance(entry, dict)] if isinstance(manifest.get("entries"), list) else []
    if manifest and manifest_role not in {"formal_evidence", "formal"}:
        return {
            "status": "pass",
            "blocked": False,
            "entry_count": len(entries),
            "manifest_role": manifest_role or "legacy_mixed",
            "skipped": True,
            "issues": [],
        }
    issues: list[dict[str, Any]] = []
    runtime_prefixes = (".beacon/traces/", ".beacon/state/hooks/", ".beacon/raw-command-log.jsonl")
    for entry in entries:
        rel_path = str(entry.get("path") or "").strip()
        expected_hash = str(entry.get("sha256") or "").strip()
        if not rel_path:
            continue
        if rel_path.startswith(runtime_prefixes):
            issues.append({"reason_code": REASON_RUNTIME_NOT_FORMAL, "path": rel_path, "blocked": True})
            continue
        if not _is_tracked(root, rel_path):
            issues.append({"reason_code": REASON_FORMAL_UNTRACKED, "path": rel_path, "blocked": True})
            continue
        file_path = root / rel_path
        if not file_path.is_file() or hashlib.sha256(file_path.read_bytes()).hexdigest() != expected_hash:
            issues.append({"reason_code": REASON_FORMAL_HASH, "path": rel_path, "blocked": True})
    blocked = any(bool(issue.get("blocked")) for issue in issues)
    return {
        "status": "blocked" if blocked else "pass",
        "blocked": blocked,
        "entry_count": len(entries),
        "issues": issues,
    }


def _task_evidence_rows(tasks_text: str) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for line in tasks_text.splitlines():
        stripped = line.strip()
        if not stripped.startswith("- ["):
            continue
        checked = stripped.startswith("- [x]") or stripped.startswith("- [X]")
        ac = ""
        marker = "ac="
        if marker in stripped:
            ac = stripped.split(marker, 1)[1].split(" ", 1)[0].strip("` ·")
        evidence = ""
        if "evidence=`" in stripped:
            evidence = stripped.split("evidence=`", 1)[1].split("`", 1)[0]
        if evidence:
            rows.append({"line": stripped, "checked": checked, "ac": ac, "evidence": evidence})
    return rows


def validate_task_evidence(project_root: Path, *, version: str, feature: str) -> dict[str, Any]:
    root = _git_root(project_root)
    slug = feature_slug(feature)
    package_dir = root / "docs" / "beacon" / version / "features" / slug
    tasks_path = package_dir / "tasks.md"
    evidence_index_path = package_dir / "evidence.md"
    if not tasks_path.is_file():
        return {"status": "pass", "blocked": False, "issues": [], "task_count": 0}
    evidence_index = evidence_index_path.read_text(encoding="utf-8") if evidence_index_path.is_file() else ""
    manifest_paths = {str(entry.get("path") or "") for entry in _manifest_entries(root)}
    issues: list[dict[str, Any]] = []
    rows = _task_evidence_rows(tasks_path.read_text(encoding="utf-8"))
    for row in rows:
        rel_path = str(row["evidence"])
        file_path = root / rel_path
        if row["checked"]:
            if not file_path.is_file():
                issues.append({"reason_code": REASON_TASK_EVIDENCE, "path": rel_path, "ac": row.get("ac"), "blocked": True, "message": "checked task evidence file missing"})
                continue
            try:
                json.loads(file_path.read_text(encoding="utf-8"))
            except Exception as exc:
                issues.append({"reason_code": REASON_TASK_EVIDENCE, "path": rel_path, "ac": row.get("ac"), "blocked": True, "message": f"checked task evidence is not JSON: {exc}"})
                continue
            if not _is_tracked(root, rel_path):
                issues.append({"reason_code": REASON_TASK_EVIDENCE, "path": rel_path, "ac": row.get("ac"), "blocked": True, "message": "checked task evidence is not tracked/promoted"})
                continue
            if rel_path not in manifest_paths and rel_path not in evidence_index:
                issues.append({"reason_code": REASON_TASK_EVIDENCE, "path": rel_path, "ac": row.get("ac"), "blocked": True, "message": "checked task evidence is not indexed"})
        elif file_path.exists():
            issues.append({"reason_code": REASON_ORPHAN_EVIDENCE, "path": rel_path, "ac": row.get("ac"), "blocked": True})
    blocked = any(bool(issue.get("blocked")) for issue in issues)
    return {"status": "blocked" if blocked else "pass", "blocked": blocked, "issues": issues, "task_count": len(rows)}


def build_trace_digest(project_root: Path, *, run_id: str) -> dict[str, Any]:
    root = _git_root(project_root)
    trace_file = root / ".beacon" / "traces" / f"{run_id}.jsonl"
    if not trace_file.is_file():
        return {"status": "blocked", "reason_code": "agent_trace_missing", "run_id": run_id}
    raw = trace_file.read_bytes()
    events: list[dict[str, Any]] = []
    reason_codes: list[str] = []
    harnesses: list[str] = []
    feature_slugs: list[str] = []
    for line in trace_file.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        try:
            event = json.loads(line)
        except json.JSONDecodeError:
            return {"status": "blocked", "reason_code": "agent_trace_invalid_json", "run_id": run_id}
        if isinstance(event, dict):
            events.append(event)
            if event.get("reason_code"):
                reason_codes.append(str(event.get("reason_code")))
            if event.get("harness"):
                harnesses.append(str(event.get("harness")))
            if event.get("feature_slug"):
                feature_slugs.append(str(event.get("feature_slug")))
    return {
        "status": "pass",
        "run_id": run_id,
        "event_count": len(events),
        "harness": sorted(set(harnesses)),
        "feature_slug": sorted(set(feature_slugs)),
        "reason_codes": sorted(set(reason_codes)),
        "sha256": hashlib.sha256(raw).hexdigest(),
        "redaction_status": "pass",
    }


def verify_clean_workspace(
    project_root: Path,
    *,
    version: str = "",
    feature: str = "",
    strict: bool = False,
    profile: str = "default",
) -> dict[str, Any]:
    root = _git_root(project_root)
    snapshot = collect_workspace_snapshot(root)
    dirty_entries = snapshot["dirty_entries"]
    hidden_dirty = detect_skip_worktree_hidden_dirty(root)
    issues: list[dict[str, Any]] = []
    for entry in dirty_entries:
        role = str(entry.get("artifact_role") or "")
        if role == "unclassified":
            issues.append({"reason_code": REASON_UNCLASSIFIED, "path": entry.get("path"), "blocked": True})
        elif role == "forbidden":
            issues.append({"reason_code": REASON_FORBIDDEN, "path": entry.get("path"), "blocked": True})
        elif role == "host_projection":
            issues.append({"reason_code": REASON_HOST_POLICY, "path": entry.get("path"), "blocked": bool(strict)})
    for item in hidden_dirty:
        issues.append({**item, "blocked": True})
    if strict and dirty_entries:
        classified_dirty = [entry for entry in dirty_entries if entry.get("artifact_role") not in {"unclassified", "forbidden"}]
        if classified_dirty:
            issues.append(
                {
                    "reason_code": REASON_REQUIRES_RESOLUTION,
                    "blocked": True,
                    "dirty_count": len(classified_dirty),
                    "required_route": "commit/promote/ignore/clean then rerun",
                }
            )
    formal_evidence_gate = validate_formal_evidence_manifest(root)
    if formal_evidence_gate.get("blocked"):
        issues.extend([{**issue, "blocked": True} for issue in formal_evidence_gate.get("issues", [])])
    task_evidence_gate = {"status": "skipped", "blocked": False, "issues": []}
    if version and feature:
        task_evidence_gate = validate_task_evidence(root, version=version, feature=feature)
        if task_evidence_gate.get("blocked"):
            issues.extend([{**issue, "blocked": True} for issue in task_evidence_gate.get("issues", [])])
    blocked_issues = [issue for issue in issues if bool(issue.get("blocked"))]
    role_counts: dict[str, int] = {}
    for entry in dirty_entries:
        role = str(entry.get("artifact_role") or "unclassified")
        role_counts[role] = role_counts.get(role, 0) + 1
    return {
        "schema_version": SCHEMA_VERSION,
        "status": "blocked" if blocked_issues else "pass",
        "blocked": bool(blocked_issues),
        "reason_code": str(blocked_issues[0].get("reason_code") or "") if blocked_issues else "",
        "project_root": str(root),
        "version": version,
        "feature": feature,
        "profile": profile,
        "strict": bool(strict),
        "snapshot": snapshot,
        "dirty_entries": dirty_entries,
        "dirty_count": len(dirty_entries),
        "role_counts": role_counts,
        "dirty_manifest": DIRTY_MANIFEST,
        "skip_worktree_hidden_dirty": hidden_dirty,
        "formal_evidence_gate": formal_evidence_gate,
        "task_evidence_gate": task_evidence_gate,
        "issues": issues,
        "generated_at": now_iso(),
    }
