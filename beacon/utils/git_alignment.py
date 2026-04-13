"""Shared git alignment and implementation branch guard helpers."""

from __future__ import annotations

import subprocess
from pathlib import Path
from typing import Any


def _branch_prefix_from_expected_branch(expected_branch: str, fallback: str) -> str:
    text = str(expected_branch or "").strip()
    if "/" in text:
        return text.split("/", 1)[0] + "/"
    return fallback


def git_output(project_root: Path, *args: str, timeout: float = 5) -> str:
    try:
        result = subprocess.run(
            ["git", *args],
            cwd=project_root,
            capture_output=True,
            text=True,
            timeout=timeout,
            check=False,
        )
    except Exception:  # noqa: BLE001
        return ""
    if result.returncode != 0:
        return ""
    return str(result.stdout or "").strip()


def git_repo_exists(project_root: Path) -> bool:
    return bool(git_output(project_root, "rev-parse", "--git-dir"))


def git_branch_exists(project_root: Path, branch: str) -> bool:
    try:
        result = subprocess.run(
            ["git", "show-ref", "--verify", "--quiet", f"refs/heads/{branch}"],
            cwd=project_root,
            capture_output=True,
            text=True,
            timeout=5,
            check=False,
        )
    except Exception:  # noqa: BLE001
        return False
    return result.returncode == 0


def git_has_dirty_worktree(project_root: Path) -> bool:
    try:
        result = subprocess.run(
            ["git", "status", "--porcelain"],
            cwd=project_root,
            capture_output=True,
            text=True,
            timeout=5,
            check=False,
        )
    except Exception:  # noqa: BLE001
        return False
    if result.returncode != 0:
        return False
    return bool(str(result.stdout or "").strip())


def collect_git_alignment(
    project_root: Path,
    version: str,
    *,
    allow_tag: bool = True,
    require_exact_branch: bool = False,
    branch_prefix: str = "beacon/",
    base_branch: str = "main",
    expected_branch: str = "",
) -> dict[str, Any]:
    current_branch = git_output(project_root, "rev-parse", "--abbrev-ref", "HEAD")
    current_commit = git_output(project_root, "rev-parse", "HEAD")
    repo_url = git_output(project_root, "remote", "get-url", "origin")
    current_tag = git_output(project_root, "describe", "--tags", "--exact-match")
    target_branch = str(expected_branch or f"{branch_prefix}{version}")
    branch_matches_target = bool(current_branch and current_branch == target_branch)
    branch_has_required_prefix = bool(current_branch and current_branch.startswith(branch_prefix))
    tag_matches_version = bool(current_tag and current_tag == version)
    version_ref_satisfied = branch_matches_target or (allow_tag and tag_matches_version)
    detached_head = current_branch == "HEAD"
    repo_detected = git_repo_exists(project_root)
    reason_codes: list[str] = []

    if not repo_detected:
        reason_codes.append("git_repo_missing")
    if detached_head:
        reason_codes.append("git_detached_head")
    if not branch_matches_target:
        reason_codes.append("git_branch_target_mismatch")
    if not branch_has_required_prefix:
        reason_codes.append("git_branch_prefix_mismatch")
    if not version_ref_satisfied:
        reason_codes.append("git_version_ref_not_satisfied")
    if require_exact_branch and not branch_matches_target:
        reason_codes.append("git_exact_branch_required")

    blocked = (
        (not repo_detected)
        or detached_head
        or (require_exact_branch and not branch_matches_target)
        or (not version_ref_satisfied)
    )

    return {
        "repo_url": repo_url,
        "base_branch": base_branch,
        "target_branch": target_branch,
        "current_branch": current_branch,
        "current_commit": current_commit,
        "current_tag": current_tag,
        "worktree_path": str(project_root),
        "version_ref": version,
        "allowed_refs": ["branch"] if not allow_tag else ["tag", "branch"],
        "enforce_branch_prefix": branch_prefix,
        "branch_matches_target": branch_matches_target,
        "branch_has_required_prefix": branch_has_required_prefix,
        "tag_matches_version": tag_matches_version,
        "version_ref_satisfied": version_ref_satisfied,
        "reason_codes": list(dict.fromkeys(reason_codes)),
        "blocked": blocked,
        "detached_head": detached_head,
        "repo_detected": repo_detected,
    }


def build_implement_branch_guard_payload(
    project_root: Path,
    version: str,
    *,
    require_clean_worktree_for_switch: bool = True,
    expected_branch: str = "",
    branch_prefix: str = "beacon/",
    base_branch: str = "main",
    git_roots: list[str] | None = None,
) -> dict[str, Any]:
    roots = [str(item).strip() for item in (git_roots or []) if str(item).strip()]
    if roots:
        alignments = []
        any_repo_detected = False
        blocked = False
        dirty_worktree = False
        for item in roots:
            repo_root = (project_root / item).resolve()
            resolved_prefix = _branch_prefix_from_expected_branch(expected_branch, branch_prefix)
            alignment = collect_git_alignment(
                repo_root,
                version,
                allow_tag=False,
                require_exact_branch=True,
                branch_prefix=resolved_prefix,
                base_branch=base_branch,
                expected_branch=expected_branch,
            )
            any_repo_detected = any_repo_detected or bool(alignment.get("repo_detected"))
            blocked = blocked or bool(alignment.get("blocked"))
            repo_dirty = git_has_dirty_worktree(repo_root) if alignment.get("repo_detected") else False
            dirty_worktree = dirty_worktree or repo_dirty
            alignments.append(
                {
                    "repo_root": str(repo_root),
                    "relative_root": item,
                    "dirty_worktree": repo_dirty,
                    **alignment,
                }
            )
        target_branch = str(expected_branch or (alignments[0].get("target_branch", "") if alignments else ""))
        current_branch = ",".join(sorted({str(item.get("current_branch", "") or "") for item in alignments if str(item.get("current_branch", "") or "")}))
        current_tag = ",".join(sorted({str(item.get("current_tag", "") or "") for item in alignments if str(item.get("current_tag", "") or "")}))
        branch_exists = all(git_branch_exists(Path(item["repo_root"]), target_branch) for item in alignments) if target_branch else False
        reason_codes: list[str] = []
        for item in alignments:
            reason_codes.extend(list(item.get("reason_codes", [])))
        summary = (
            f"implement branch preflight passed on workspace branch {target_branch}"
            if not blocked
            else f"implement branch preflight blocked: expected {target_branch}, workspace repos not aligned"
        )
        recommended_command = ""
        if blocked and target_branch:
            recommended_command = f"git -C <service-root> switch {target_branch}"
        return {
            "schema_version": "1.0",
            "status": "blocked" if blocked else "pass",
            "summary": summary,
            "blocked": blocked,
            "version": version,
            "expected_branch": target_branch,
            "current_branch": current_branch,
            "current_tag": current_tag,
            "branch_exists": branch_exists,
            "dirty_worktree": dirty_worktree,
            "require_clean_worktree_for_switch": require_clean_worktree_for_switch,
            "recommended_command": recommended_command,
            "reason_codes": list(dict.fromkeys(reason_codes)),
            "git_alignment": {
                "mode": "workspace",
                "repo_detected": any_repo_detected,
                "target_branch": target_branch,
                "worktree_path": str(project_root),
                "workspace_repos": alignments,
                "blocked": blocked,
                "reason_codes": list(dict.fromkeys(reason_codes)),
            },
        }

    resolved_prefix = _branch_prefix_from_expected_branch(expected_branch, branch_prefix)
    alignment = collect_git_alignment(
        project_root,
        version,
        allow_tag=False,
        require_exact_branch=True,
        branch_prefix=resolved_prefix,
        base_branch=base_branch,
        expected_branch=expected_branch,
    )
    expected_branch = str(alignment.get("target_branch", "") or "")
    current_branch = str(alignment.get("current_branch", "") or "")
    branch_exists = git_branch_exists(project_root, expected_branch) if expected_branch else False
    dirty_worktree = git_has_dirty_worktree(project_root) if alignment.get("repo_detected") else False

    if not alignment.get("repo_detected"):
        summary = "implement branch preflight blocked: git repository not detected"
        recommended_command = ""
    elif alignment.get("detached_head"):
        summary = "implement branch preflight blocked: detached HEAD is not allowed for implement"
        recommended_command = f"git switch {expected_branch}" if expected_branch else ""
    elif current_branch != expected_branch:
        summary = f"implement branch preflight blocked: expected {expected_branch}, current {current_branch or 'unknown'}"
        recommended_command = (
            f"git switch {expected_branch}"
            if branch_exists
            else f"git switch -c {expected_branch}"
        )
    else:
        summary = f"implement branch preflight passed on {expected_branch}"
        recommended_command = ""

    if dirty_worktree and require_clean_worktree_for_switch and current_branch != expected_branch:
        alignment["reason_codes"] = list(dict.fromkeys([*alignment.get("reason_codes", []), "implement_branch_switch_dirty_worktree"]))

    return {
        "schema_version": "1.0",
        "status": "blocked" if alignment.get("blocked") else "pass",
        "summary": summary,
        "blocked": bool(alignment.get("blocked")),
        "version": version,
        "expected_branch": expected_branch,
        "current_branch": current_branch,
        "current_tag": str(alignment.get("current_tag", "") or ""),
        "branch_exists": branch_exists,
        "dirty_worktree": dirty_worktree,
        "require_clean_worktree_for_switch": require_clean_worktree_for_switch,
        "recommended_command": recommended_command,
        "reason_codes": alignment.get("reason_codes", []),
        "git_alignment": alignment,
    }


def switch_to_expected_branch(
    project_root: Path,
    expected_branch: str,
    *,
    create_if_missing: bool = True,
    git_roots: list[str] | None = None,
) -> dict[str, Any]:
    roots = [str(item).strip() for item in (git_roots or []) if str(item).strip()]
    if roots:
        attempts = []
        statuses = []
        for item in roots:
            repo_root = (project_root / item).resolve()
            result = switch_to_expected_branch(repo_root, expected_branch, create_if_missing=create_if_missing)
            attempts.append({"repo_root": str(repo_root), **result})
            statuses.append(str(result.get("status", "")))
        overall = "switched" if all(status == "switched" for status in statuses) else "failed"
        return {
            "status": overall,
            "expected_branch": expected_branch,
            "attempts": attempts,
        }
    commands: list[list[str]] = [["git", "switch", expected_branch]]
    if create_if_missing:
        commands.append(["git", "switch", "-c", expected_branch])
    attempts: list[dict[str, Any]] = []
    for command in commands:
        try:
            result = subprocess.run(
                command,
                cwd=project_root,
                capture_output=True,
                text=True,
                timeout=10,
                check=False,
            )
        except Exception as exc:  # noqa: BLE001
            attempts.append({"command": command, "exit_code": None, "stderr": str(exc)})
            continue
        attempts.append(
            {
                "command": command,
                "exit_code": result.returncode,
                "stdout": str(result.stdout or "").strip(),
                "stderr": str(result.stderr or "").strip(),
            }
        )
        if result.returncode == 0:
            return {
                "status": "switched",
                "expected_branch": expected_branch,
                "attempts": attempts,
            }
    return {
        "status": "failed",
        "expected_branch": expected_branch,
        "attempts": attempts,
    }
