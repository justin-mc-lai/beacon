"""Implement-lane enforcement: block business commits on main + git hooks (UD-ENF).

Closes the hole where agents edit/commit beacon/** on main without workspace admit.
"""

from __future__ import annotations

import hashlib
import json
import os
import stat
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable

SCHEMA = "implement-lane-enforcement.v1"
REASON_MAIN_IMPLEMENT = "main_implement_forbidden"
REASON_EXCEPTION_OK = "main_implement_exception_allowed"
REASON_HOOK_MISSING = "git_hook_missing"
REASON_HOOK_MISMATCH = "git_hook_mismatch"

CANONICAL_BRANCHES = frozenset({"main", "master"})

# Paths that must NOT be committed directly on main (implement business)
BUSINESS_PREFIXES = (
    "beacon/",
    "packages/",
)
BUSINESS_FILE_GLOBS_PREFIX = (
    "tests/test_",
)

# Always allowed on main (truth/docs/skills authoring)
ALLOW_PREFIXES = (
    "docs/",
    "skills/",
    ".claude/",
    ".agents/",
    ".codex/",
)

EXCEPTION_ENV = "BEACON_ALLOW_MAIN_IMPLEMENT"
EXCEPTION_EVIDENCE_REL = ".beacon/evidence/main-implement-exception.json"

HOOK_MARKER = "# BEACON_IMPLEMENT_LANE_ENFORCEMENT_V1"
PRE_COMMIT_NAME = "pre-commit"
PRE_PUSH_NAME = "pre-push"


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _run_git(project_root: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", *args],
        cwd=str(project_root),
        capture_output=True,
        text=True,
        check=False,
    )


def current_branch(project_root: Path | str) -> str:
    root = Path(project_root).expanduser().resolve()
    proc = _run_git(root, "rev-parse", "--abbrev-ref", "HEAD")
    if proc.returncode != 0:
        return ""
    return (proc.stdout or "").strip()


def is_canonical_branch(branch: str) -> bool:
    return branch in CANONICAL_BRANCHES


def normalize_rel(path: str) -> str:
    text = path.replace("\\", "/").strip()
    while text.startswith("./"):
        text = text[2:]
    return text


def is_allowlisted(rel: str) -> bool:
    rel = normalize_rel(rel)
    for p in ALLOW_PREFIXES:
        if rel == p.rstrip("/") or rel.startswith(p):
            return True
    # top-level markdown / config often OK
    if "/" not in rel.rstrip("/"):
        if rel.endswith(".md") or rel in {
            "pyproject.toml",
            "Cargo.toml",
            "Cargo.lock",
            ".gitignore",
            "Makefile",
            "README.md",
            "AGENTS.md",
            "CLAUDE.md",
        }:
            return True
    return False


def is_business_path(rel: str) -> bool:
    rel = normalize_rel(rel)
    if is_allowlisted(rel):
        # docs under docs/ ok; but docs is allow — never business
        return False
    for p in BUSINESS_PREFIXES:
        if rel == p.rstrip("/") or rel.startswith(p):
            return True
    # tests/test_*.py business unit tests
    name = Path(rel).name
    if rel.startswith("tests/") and name.startswith("test_") and name.endswith(".py"):
        return True
    return False


def staged_files(project_root: Path | str) -> list[str]:
    root = Path(project_root).expanduser().resolve()
    proc = _run_git(root, "diff", "--cached", "--name-only", "--diff-filter=ACMR")
    if proc.returncode != 0:
        return []
    return [normalize_rel(line) for line in (proc.stdout or "").splitlines() if line.strip()]


def exception_allowed(project_root: Path | str) -> dict[str, Any]:
    root = Path(project_root).expanduser().resolve()
    env_on = str(os.environ.get(EXCEPTION_ENV, "")).strip().lower() in {"1", "true", "yes", "on"}
    evidence = root / EXCEPTION_EVIDENCE_REL
    evidence_ok = evidence.is_file()
    payload: dict[str, Any] = {}
    if evidence_ok:
        try:
            payload = json.loads(evidence.read_text(encoding="utf-8"))
        except Exception:  # noqa: BLE001
            payload = {"parse_error": True}
    ok = env_on and evidence_ok and not payload.get("parse_error")
    return {
        "allowed": ok,
        "env_on": env_on,
        "evidence_path": str(evidence),
        "evidence_exists": evidence_ok,
        "evidence": payload if evidence_ok else {},
    }


def write_exception_evidence(
    project_root: Path | str,
    *,
    reason: str,
    feature: str = "",
    actor: str = "operator",
) -> Path:
    root = Path(project_root).expanduser().resolve()
    path = root / EXCEPTION_EVIDENCE_REL
    path.parent.mkdir(parents=True, exist_ok=True)
    body = {
        "schema": "main-implement-exception.v1",
        "reason": reason,
        "feature": feature,
        "actor": actor,
        "created_at": _now_iso(),
        "env_required": EXCEPTION_ENV,
    }
    path.write_text(json.dumps(body, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return path


def check_main_implement_commit(
    project_root: Path | str,
    *,
    files: Iterable[str] | None = None,
    branch: str | None = None,
) -> dict[str, Any]:
    """Return pass/blocked for committing listed (or staged) files on current branch."""
    root = Path(project_root).expanduser().resolve()
    br = branch if branch is not None else current_branch(root)
    paths = list(files) if files is not None else staged_files(root)
    business = [p for p in paths if is_business_path(p)]
    result: dict[str, Any] = {
        "schema": SCHEMA,
        "status": "pass",
        "blocked": False,
        "reason_code": "",
        "branch": br,
        "canonical": is_canonical_branch(br),
        "files_checked": paths,
        "business_files": business,
        "exception": exception_allowed(root),
    }
    if not is_canonical_branch(br):
        result["status"] = "pass"
        result["note"] = "non_canonical_branch_ok"
        return result
    if not business:
        result["status"] = "pass"
        result["note"] = "no_business_paths"
        return result
    exc = result["exception"]
    if exc.get("allowed"):
        result["status"] = "pass"
        result["reason_code"] = REASON_EXCEPTION_OK
        result["note"] = "emergency_exception"
        return result
    result["status"] = "blocked"
    result["blocked"] = True
    result["reason_code"] = REASON_MAIN_IMPLEMENT
    result["message"] = (
        "Refusing to commit business implement paths on main/master. "
        "Use: beacon workspace admit -v <ver> --feature <slug> then implement in worktree_path. "
        f"Emergency: {EXCEPTION_ENV}=1 and write {EXCEPTION_EVIDENCE_REL}."
    )
    result["repair"] = [
        "beacon workspace admit -p . -v <version> --feature <slug> --json",
        "cd <worktree_path>  # from admit cwd",
        "implement + commit on leaf branch",
        "git checkout main && git merge <leaf>",
    ]
    return result


def check_working_tree_lane(project_root: Path | str) -> dict[str, Any]:
    """Doctor: warn if on main with dirty business paths (even unstaged)."""
    root = Path(project_root).expanduser().resolve()
    br = current_branch(root)
    proc = _run_git(root, "status", "--porcelain")
    dirty: list[str] = []
    for line in (proc.stdout or "").splitlines():
        if len(line) < 4:
            continue
        path = normalize_rel(line[3:].strip().split(" -> ")[-1])
        if path:
            dirty.append(path)
    business_dirty = [p for p in dirty if is_business_path(p)]
    in_worktree = "/.beacon/worktrees/" in str(root).replace("\\", "/") or any(
        "/.beacon/worktrees/" in str(Path(root).resolve()) for _ in [0]
    )
    # also detect if cwd path contains worktrees
    cwd_is_worktree = ".beacon/worktrees" in Path.cwd().as_posix()
    blocked = is_canonical_branch(br) and bool(business_dirty) and not cwd_is_worktree
    return {
        "schema": SCHEMA,
        "check": "verify_implement_lane",
        "status": "blocked" if blocked else ("warn" if business_dirty and is_canonical_branch(br) else "pass"),
        "blocked": blocked,
        "reason_code": REASON_MAIN_IMPLEMENT if blocked else "",
        "branch": br,
        "cwd": str(Path.cwd()),
        "cwd_looks_like_worktree": cwd_is_worktree,
        "dirty_business_files": business_dirty,
        "message": (
            "Main checkout has dirty business paths — move implement to admitted worktree."
            if blocked
            else ""
        ),
    }


def _hook_script_body(*, hook_kind: str) -> str:
    # Portable: monorepo source first, then installed `beacon` package (consumer repos).
    return f"""#!/usr/bin/env bash
{HOOK_MARKER}
# Auto-generated by beacon doctor setup-git-hooks — do not hand-edit marker line.
set -euo pipefail
ROOT="$(git rev-parse --show-toplevel 2>/dev/null || true)"
if [[ -z "${{ROOT}}" ]]; then
  exit 0
fi
export BEACON_GIT_HOOK_KIND="{hook_kind}"
# 1) Beacon monorepo checkout: import from repo tree
if [[ -f "${{ROOT}}/beacon/utils/implement_lane_enforcement.py" ]]; then
  cd "${{ROOT}}"
  exec python3 -c "from beacon.utils.implement_lane_enforcement import hook_main; raise SystemExit(hook_main())"
fi
# 2) Consumer / product repos: use installed beacon package on PYTHONPATH
if python3 -c "import beacon.utils.implement_lane_enforcement" >/dev/null 2>&1; then
  exec python3 -c "from beacon.utils.implement_lane_enforcement import hook_main; raise SystemExit(hook_main())"
fi
# 3) Soft skip only when beacon is not available at all
exit 0
"""


def hook_main() -> int:
    """Entry for pre-commit / pre-push installed hooks."""
    kind = str(os.environ.get("BEACON_GIT_HOOK_KIND") or "pre-commit").strip()
    # resolve repo root
    proc = subprocess.run(
        ["git", "rev-parse", "--show-toplevel"],
        capture_output=True,
        text=True,
        check=False,
    )
    if proc.returncode != 0:
        return 0
    root = Path((proc.stdout or "").strip()).resolve()
    if kind == "pre-push":
        # Only block if index still has business paths staged on main.
        # Do NOT re-scan HEAD~1..HEAD: legitimate leaf merges (incl. ff-only)
        # already contain business paths and would false-positive.
        result = check_main_implement_commit(root)
        if result.get("blocked"):
            print(result.get("message") or REASON_MAIN_IMPLEMENT, flush=True)
            for pth in result.get("business_files") or []:
                print(f"  blocked: {pth}", flush=True)
            return 1
        return 0

    # pre-commit
    result = check_main_implement_commit(root)
    if result.get("blocked"):
        print(result.get("message") or REASON_MAIN_IMPLEMENT, flush=True)
        for p in result.get("business_files") or []:
            print(f"  blocked: {p}", flush=True)
        print("repair:", flush=True)
        for line in result.get("repair") or []:
            print(f"  {line}", flush=True)
        return 1
    return 0


def hooks_dir(project_root: Path | str) -> Path:
    root = Path(project_root).expanduser().resolve()
    proc = _run_git(root, "rev-parse", "--git-path", "hooks")
    if proc.returncode == 0 and (proc.stdout or "").strip():
        p = Path((proc.stdout or "").strip())
        if not p.is_absolute():
            p = root / p
        return p
    return root / ".git" / "hooks"


def setup_git_hooks(project_root: Path | str, *, force: bool = True) -> dict[str, Any]:
    root = Path(project_root).expanduser().resolve()
    hdir = hooks_dir(root)
    hdir.mkdir(parents=True, exist_ok=True)
    written: list[dict[str, str]] = []
    for name, kind in ((PRE_COMMIT_NAME, "pre-commit"), (PRE_PUSH_NAME, "pre-push")):
        path = hdir / name
        body = _hook_script_body(hook_kind=kind)
        if path.exists() and not force:
            text = path.read_text(encoding="utf-8", errors="replace")
            if HOOK_MARKER not in text:
                written.append({"path": str(path), "action": "skipped_unmanaged"})
                continue
        path.write_text(body, encoding="utf-8")
        mode = path.stat().st_mode
        path.chmod(mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)
        written.append({"path": str(path), "action": "written", "sha256": hashlib.sha256(body.encode()).hexdigest()[:16]})
    return {
        "schema": SCHEMA,
        "status": "ok",
        "hooks_dir": str(hdir),
        "written": written,
        "marker": HOOK_MARKER,
    }


def verify_git_hooks(project_root: Path | str) -> dict[str, Any]:
    root = Path(project_root).expanduser().resolve()
    hdir = hooks_dir(root)
    checks: list[dict[str, Any]] = []
    ok = True
    for name in (PRE_COMMIT_NAME, PRE_PUSH_NAME):
        path = hdir / name
        if not path.is_file():
            ok = False
            checks.append({"hook": name, "status": "fail", "reason_code": REASON_HOOK_MISSING, "path": str(path)})
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        if HOOK_MARKER not in text:
            ok = False
            checks.append({"hook": name, "status": "fail", "reason_code": REASON_HOOK_MISMATCH, "path": str(path)})
            continue
        if not os.access(path, os.X_OK):
            ok = False
            checks.append({"hook": name, "status": "fail", "reason_code": "git_hook_not_executable", "path": str(path)})
            continue
        checks.append({"hook": name, "status": "pass", "path": str(path)})
    return {
        "schema": SCHEMA,
        "status": "pass" if ok else "fail",
        "ok": ok,
        "hooks_dir": str(hdir),
        "checks": checks,
    }


def release_implement_lane_advisory(project_root: Path | str, *, version: str = "") -> dict[str, Any]:
    """Non-fatal WARN for release check (UD-ENF-005)."""
    root = Path(project_root).expanduser().resolve()
    hooks = verify_git_hooks(root)
    lane = check_working_tree_lane(root)
    warns: list[str] = []
    if hooks.get("status") != "pass":
        warns.append("git_hooks_not_verified")
    if lane.get("status") in {"blocked", "warn"}:
        warns.append("implement_lane_dirty_or_main_business")
    # pool presence advisory for version
    pool = root / ".beacon" / "state" / "workspace-pool" / (version or "unknown") / "pool.json"
    if version and not pool.is_file():
        # also search any pool
        any_pool = list((root / ".beacon" / "state" / "workspace-pool").glob("*/pool.json")) if (root / ".beacon" / "state" / "workspace-pool").exists() else []
        if not any_pool:
            warns.append("workspace_pool_missing_advisory")
    return {
        "schema": SCHEMA,
        "check": "release_implement_lane_advisory",
        "status": "warn" if warns else "pass",
        "blocking": False,
        "warnings": warns,
        "hooks": hooks,
        "lane": lane,
        "version": version,
        "message": "Implement-lane advisory (non-fatal): " + ",".join(warns) if warns else "ok",
    }


def goal_require_admission_hint(admission: dict[str, Any] | None) -> dict[str, Any]:
    """Helper for goal path: empty admission → blocked payload."""
    if admission and not admission.get("blocked") and str(admission.get("status") or "").lower() in {
        "pass",
        "ok",
        "switched",
        "issued",
    }:
        return {"status": "pass", "blocked": False}
    # also accept allow_implement true
    if admission and admission.get("allow_implement") is True:
        return {"status": "pass", "blocked": False}
    if admission and admission.get("worktree_path") and not admission.get("blocked"):
        return {"status": "pass", "blocked": False, "note": "worktree_path_present"}
    return {
        "status": "blocked",
        "blocked": True,
        "reason_code": "goal_implement_admission_required",
        "message": "goal implement requires workspace admission / worktree_path (UD-ENF-003)",
    }
