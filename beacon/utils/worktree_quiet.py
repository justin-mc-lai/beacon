"""Local quieting helpers for Beacon runtime-heavy worktrees."""

from __future__ import annotations

import fnmatch
import subprocess
from pathlib import Path
from typing import Any


MANAGED_EXCLUDE_START = "# BEACON-QUIET-WORKTREE:START"
MANAGED_EXCLUDE_END = "# BEACON-QUIET-WORKTREE:END"

QUIET_SKIP_PATTERNS = (
    ".beacon/auto-test-status.json",
    ".beacon/coverage-summary.json",
    ".beacon/evidence-manifest.json",
    ".beacon/evidence-signature-chain.json",
    ".beacon/gate-report.json",
    ".beacon/memory/*.json",
    ".beacon/qa/status.json",
    ".beacon/raw-command-log.jsonl",
    ".beacon/state/eval-lab/*",
    ".beacon/state/learning/*.json",
    "docs/beacon/*/.machine/execution/change-impact.json",
    "docs/beacon/*/.machine/execution/config.json",
    "docs/beacon/*/.machine/execution/delivery-manifest.json",
    "docs/beacon/*/.machine/execution/git-alignment.json",
    "docs/beacon/*/.machine/execution/source.json",
)

QUIET_EXCLUDE_PATTERNS = (
    ".beacon/state/artifact-update-obligations/*.json",
    ".beacon/state/baselines/v*/",
    ".beacon/state/evo/",
    ".beacon/state/implementation-*.json",
    ".beacon/state/qa-calibration/",
    ".beacon/state/spec-fingerprints/v*/",
)


def _run_git(repo_root: Path, args: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", *args],
        cwd=repo_root,
        check=False,
        capture_output=True,
        text=True,
    )


def _resolve_git_root(project_root: Path) -> Path:
    result = _run_git(project_root, ["rev-parse", "--show-toplevel"])
    if result.returncode != 0:
        stderr = (result.stderr or "").strip() or "not a git repository"
        raise ValueError(stderr)
    return Path(result.stdout.strip()).resolve()


def _resolve_git_path(repo_root: Path, pathspec: str) -> Path:
    result = _run_git(repo_root, ["rev-parse", "--git-path", pathspec])
    if result.returncode != 0:
        stderr = (result.stderr or "").strip() or f"unable to resolve git path: {pathspec}"
        raise RuntimeError(stderr)
    raw_path = Path(result.stdout.strip())
    if raw_path.is_absolute():
        return raw_path
    return (repo_root / raw_path).resolve()


def _tracked_quiet_paths(repo_root: Path) -> list[str]:
    result = _run_git(repo_root, ["ls-files", "-z"])
    if result.returncode != 0:
        stderr = (result.stderr or "").strip() or "unable to list tracked files"
        raise RuntimeError(stderr)
    tracked = [item for item in result.stdout.split("\0") if item]
    quiet = [path for path in tracked if any(fnmatch.fnmatchcase(path, pattern) for pattern in QUIET_SKIP_PATTERNS)]
    return sorted(dict.fromkeys(quiet))


def _skip_state(repo_root: Path, paths: list[str]) -> dict[str, str]:
    if not paths:
        return {}
    result = _run_git(repo_root, ["ls-files", "-v", "--", *paths])
    if result.returncode != 0:
        stderr = (result.stderr or "").strip() or "unable to inspect skip-worktree state"
        raise RuntimeError(stderr)
    mapping: dict[str, str] = {}
    for line in result.stdout.splitlines():
        if not line:
            continue
        if len(line) >= 3 and line[1] == " ":
            mapping[line[2:]] = line[0]
            continue
        parts = line.split(maxsplit=1)
        if len(parts) == 2:
            mapping[parts[1]] = parts[0]
    return mapping


def _strip_managed_exclude_block(text: str) -> tuple[str, bool]:
    lines = text.splitlines()
    kept: list[str] = []
    inside = False
    removed = False
    for line in lines:
        if line == MANAGED_EXCLUDE_START:
            inside = True
            removed = True
            continue
        if inside:
            if line == MANAGED_EXCLUDE_END:
                inside = False
            continue
        kept.append(line)
    cleaned = "\n".join(kept).strip("\n")
    return (f"{cleaned}\n" if cleaned else ""), removed


def _write_exclude_block(exclude_path: Path) -> bool:
    existing = exclude_path.read_text(encoding="utf-8") if exclude_path.exists() else ""
    base_text, removed = _strip_managed_exclude_block(existing)
    block = "\n".join(
        [
            MANAGED_EXCLUDE_START,
            "# Managed by `beacon doctor quiet-worktree apply`.",
            *QUIET_EXCLUDE_PATTERNS,
            MANAGED_EXCLUDE_END,
        ]
    )
    pieces = [chunk for chunk in (base_text.strip("\n"), block) if chunk]
    new_text = "\n\n".join(pieces).rstrip("\n") + "\n"
    exclude_path.parent.mkdir(parents=True, exist_ok=True)
    exclude_path.write_text(new_text, encoding="utf-8")
    return not removed


def _remove_exclude_block(exclude_path: Path) -> bool:
    if not exclude_path.exists():
        return False
    existing = exclude_path.read_text(encoding="utf-8")
    cleaned, removed = _strip_managed_exclude_block(existing)
    if removed:
        exclude_path.write_text(cleaned, encoding="utf-8")
    return removed


def quiet_worktree_status(project_root: Path) -> dict[str, Any]:
    repo_root = _resolve_git_root(project_root)
    exclude_path = _resolve_git_path(repo_root, "info/exclude")
    tracked_paths = _tracked_quiet_paths(repo_root)
    flags = _skip_state(repo_root, tracked_paths)
    skipped_paths = [path for path in tracked_paths if flags.get(path) == "S"]
    exclude_text = exclude_path.read_text(encoding="utf-8") if exclude_path.exists() else ""
    exclude_block_present = MANAGED_EXCLUDE_START in exclude_text and MANAGED_EXCLUDE_END in exclude_text
    return {
        "project_root": str(project_root.resolve()),
        "git_root": str(repo_root),
        "exclude_path": str(exclude_path),
        "exclude_block_present": exclude_block_present,
        "exclude_patterns": list(QUIET_EXCLUDE_PATTERNS),
        "tracked_candidates": tracked_paths,
        "tracked_candidate_count": len(tracked_paths),
        "skip_worktree_paths": skipped_paths,
        "skip_worktree_count": len(skipped_paths),
        "skip_patterns": list(QUIET_SKIP_PATTERNS),
    }


def apply_quiet_worktree(project_root: Path) -> dict[str, Any]:
    status = quiet_worktree_status(project_root)
    repo_root = Path(status["git_root"])
    exclude_path = Path(status["exclude_path"])
    created_block = _write_exclude_block(exclude_path)
    tracked_paths = list(status["tracked_candidates"])
    if tracked_paths:
        result = _run_git(repo_root, ["update-index", "--skip-worktree", "--", *tracked_paths])
        if result.returncode != 0:
            stderr = (result.stderr or "").strip() or "unable to apply skip-worktree"
            raise RuntimeError(stderr)
    refreshed = quiet_worktree_status(project_root)
    refreshed.update(
        {
            "mode": "apply",
            "exclude_block_written": True,
            "exclude_block_created": created_block,
        }
    )
    return refreshed


def restore_quiet_worktree(project_root: Path) -> dict[str, Any]:
    status = quiet_worktree_status(project_root)
    repo_root = Path(status["git_root"])
    skipped_paths = list(status["skip_worktree_paths"])
    if skipped_paths:
        result = _run_git(repo_root, ["update-index", "--no-skip-worktree", "--", *skipped_paths])
        if result.returncode != 0:
            stderr = (result.stderr or "").strip() or "unable to restore skip-worktree state"
            raise RuntimeError(stderr)
    exclude_removed = _remove_exclude_block(Path(status["exclude_path"]))
    refreshed = quiet_worktree_status(project_root)
    refreshed.update(
        {
            "mode": "restore",
            "exclude_block_removed": exclude_removed,
        }
    )
    return refreshed
