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


def _normalize_service_map(values: Any) -> dict[str, str]:
    if not isinstance(values, dict):
        return {}
    out: dict[str, str] = {}
    for key, value in values.items():
        service = str(key or "").strip()
        text = str(value or "").strip()
        if service and text:
            out[service] = text
    return out


def _resolve_service_root(project_root: Path, root_value: str, service: str) -> Path:
    text = str(root_value or "").strip()
    if not text:
        text = service
    path = Path(text).expanduser()
    if not path.is_absolute():
        path = project_root / path
    return path.resolve()


def _service_root_for_worktree(project_root: Path, service: str, worktree_value: str, root_value: str) -> Path:
    text = str(worktree_value or "").strip()
    if not text:
        return _resolve_service_root(project_root, root_value, service)
    path = Path(text).expanduser()
    if not path.is_absolute():
        path = project_root / path
    return path.resolve()


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
    direct_delivery_services: list[str] | None = None,
    service_branch_map: dict[str, str] | None = None,
    service_worktree_map: dict[str, str] | None = None,
) -> dict[str, Any]:
    roots = [str(item).strip() for item in (git_roots or []) if str(item).strip()]
    delivery_services = [str(item).strip() for item in (direct_delivery_services or []) if str(item).strip()]
    branch_map = _normalize_service_map(service_branch_map)
    worktree_map = _normalize_service_map(service_worktree_map)
    if str(expected_branch or "").strip() == "per-service":
        services = delivery_services or list(branch_map) or [Path(item).name for item in roots]
        root_by_service = {Path(item).name: item for item in roots}
        root_by_service.update({item: item for item in roots})
        for item in roots:
            root_text = str(item or "").strip()
            if not root_text:
                continue
            parts = Path(root_text).parts
            if parts:
                root_by_service.setdefault(parts[0], root_text)
            for service_name in branch_map:
                if root_text == service_name or root_text.startswith(f"{service_name}/"):
                    root_by_service[service_name] = root_text
        alignments = []
        any_repo_detected = False
        blocked = False
        dirty_worktree = False
        reason_codes: list[str] = []
        recommended_commands: list[str] = []
        unresolved_services: list[str] = []
        missing_map_services: list[str] = []
        for service in services:
            service_key = str(service or "").strip()
            if not service_key:
                continue
            service_branch = str(branch_map.get(service_key) or "").strip()
            service_worktree = str(worktree_map.get(service_key) or "").strip()
            root_value = root_by_service.get(service_key, service_key)
            if not service_branch or not service_worktree:
                blocked = True
                missing_map_services.append(service_key)
                reason_codes.append("explicit_version_per_service_map_missing")
                continue
            repo_root = _resolve_service_root(project_root, root_value, service_key)
            expected_root = str(_service_root_for_worktree(project_root, service_key, service_worktree, root_value))
            resolved_prefix = _branch_prefix_from_expected_branch(service_branch, branch_prefix)
            alignment = collect_git_alignment(
                repo_root,
                version,
                allow_tag=False,
                require_exact_branch=True,
                branch_prefix=resolved_prefix,
                base_branch=base_branch,
                expected_branch=service_branch,
            )
            repo_dirty = git_has_dirty_worktree(repo_root) if alignment.get("repo_detected") else False
            any_repo_detected = any_repo_detected or bool(alignment.get("repo_detected"))
            dirty_worktree = dirty_worktree or repo_dirty
            service_blocked = bool(alignment.get("blocked"))
            if repo_dirty and require_clean_worktree_for_switch and not alignment.get("branch_matches_target"):
                service_blocked = True
                alignment["reason_codes"] = list(
                    dict.fromkeys([*alignment.get("reason_codes", []), "implement_branch_switch_dirty_worktree"])
                )
            actual_root = str(repo_root)
            worktree_matches = actual_root == expected_root
            if not worktree_matches:
                service_blocked = True
                alignment["reason_codes"] = list(
                    dict.fromkeys([*alignment.get("reason_codes", []), "explicit_version_canonical_worktree_mismatch"])
                )
            if service_blocked:
                blocked = True
                reason_codes.append("explicit_version_canonical_branch_mismatch")
                if not worktree_matches:
                    recommended_commands.append(f"cd {expected_root} && git switch {service_branch}")
                elif repo_dirty and require_clean_worktree_for_switch and not alignment.get("branch_matches_target"):
                    recommended_commands.append(
                        f"git -C {repo_root} stash push -u && git -C {repo_root} switch {service_branch}"
                    )
                else:
                    recommended_commands.append(f"cd {repo_root} && git switch {service_branch}")
            reason_codes.extend(list(alignment.get("reason_codes", [])))
            alignments.append(
                {
                    "service": service_key,
                    "expected_branch": service_branch,
                    "expected_worktree": expected_root,
                    "repo_root": actual_root,
                    "relative_root": str(root_value),
                    "dirty_worktree": repo_dirty,
                    "worktree_matches_expected": worktree_matches,
                    **alignment,
                }
            )
        root_aliases = set(roots) | {Path(item).name for item in roots}
        for service in services:
            if service not in branch_map and service not in root_aliases and not roots:
                unresolved_services.append(service)
        if unresolved_services:
            blocked = True
            reason_codes.append("implement_direct_delivery_service_scope_unresolved")
        current_branch = ",".join(sorted({str(item.get("current_branch", "") or "") for item in alignments if str(item.get("current_branch", "") or "")}))
        current_tag = ",".join(sorted({str(item.get("current_tag", "") or "") for item in alignments if str(item.get("current_tag", "") or "")}))
        if missing_map_services:
            for service in missing_map_services:
                recommended_commands.append(f"add per-service branch/worktree mapping for {service}")
        summary = "implement branch preflight passed on per-service canonical branches"
        if blocked:
            summary = "implement branch preflight blocked: explicit version canonical branch/worktree mismatch"
        service_scope = {
            "status": "blocked" if unresolved_services or missing_map_services else "pass",
            "direct_delivery_services": services,
            "verified_roots": [str(item.get("repo_root", "") or "") for item in alignments],
            "unresolved_services": list(dict.fromkeys([*unresolved_services, *missing_map_services])),
        }
        return {
            "schema_version": "1.0",
            "status": "blocked" if blocked else "pass",
            "summary": summary,
            "blocked": blocked,
            "version": version,
            "expected_branch": "per-service",
            "current_branch": current_branch,
            "current_tag": current_tag,
            "branch_exists": all(git_branch_exists(Path(item["repo_root"]), str(item.get("expected_branch", "") or "")) for item in alignments) if alignments else False,
            "dirty_worktree": dirty_worktree,
            "require_clean_worktree_for_switch": require_clean_worktree_for_switch,
            "recommended_command": recommended_commands[0] if recommended_commands else "",
            "recommended_commands": list(dict.fromkeys(recommended_commands)),
            "direct_delivery_services": services,
            "service_scope": service_scope,
            "service_branch_map": branch_map,
            "service_worktree_map": worktree_map,
            "reason_codes": list(dict.fromkeys(reason_codes)),
            "git_alignment": {
                "mode": "workspace",
                "repo_detected": any_repo_detected,
                "target_branch": "per-service",
                "worktree_path": str(project_root),
                "workspace_repos": alignments,
                "blocked": blocked,
                "reason_codes": list(dict.fromkeys(reason_codes)),
            },
        }
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
            if repo_dirty and require_clean_worktree_for_switch and not alignment.get("branch_matches_target"):
                blocked = True
                alignment["reason_codes"] = list(
                    dict.fromkeys([*alignment.get("reason_codes", []), "implement_branch_switch_dirty_worktree"])
                )
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
        root_aliases = set(roots)
        for item in roots:
            name = Path(item).name.strip()
            if name:
                root_aliases.add(name)
        unresolved_services = [item for item in delivery_services if item not in root_aliases]
        if unresolved_services:
            blocked = True
            reason_codes.append("implement_direct_delivery_service_scope_unresolved")
        blocking_repos = [
            item
            for item in alignments
            if item.get("blocked") or (item.get("dirty_worktree") and not item.get("branch_matches_target"))
        ]
        recommended_commands: list[str] = []
        if blocked and target_branch:
            for item in blocking_repos:
                repo_label = str(item.get("relative_root", "") or "")
                if item.get("dirty_worktree") and require_clean_worktree_for_switch and not item.get("branch_matches_target"):
                    recommended_commands.append(
                        f"git -C {repo_label} stash push -u && git -C {repo_label} switch {target_branch}"
                    )
                elif repo_label:
                    recommended_commands.append(f"git -C {repo_label} switch {target_branch}")
            for item in unresolved_services:
                recommended_commands.append(
                    f"update git_workflow.service_directories to include {item} before implementation"
                )
        summary = f"implement branch preflight passed on workspace branch {target_branch}"
        if blocked:
            dirty_repos = [
                str(item.get("relative_root", "") or "")
                for item in blocking_repos
                if item.get("dirty_worktree") and not item.get("branch_matches_target")
            ]
            if unresolved_services:
                summary = (
                    "implement branch preflight blocked: direct delivery service scope unresolved for "
                    + ", ".join(unresolved_services)
                )
            elif dirty_repos:
                summary = (
                    f"implement branch preflight blocked: expected {target_branch}, dirty worktree blocks switch in "
                    + ", ".join(dirty_repos)
                )
            else:
                summary = f"implement branch preflight blocked: expected {target_branch}, workspace repos not aligned"
        service_scope = {
            "status": "blocked" if unresolved_services else "pass",
            "direct_delivery_services": delivery_services or list(roots),
            "verified_roots": list(roots),
            "unresolved_services": unresolved_services,
        }
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
            "recommended_command": recommended_commands[0] if recommended_commands else "",
            "recommended_commands": recommended_commands,
            "direct_delivery_services": service_scope["direct_delivery_services"],
            "service_scope": service_scope,
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
    if dirty_worktree and require_clean_worktree_for_switch and current_branch != expected_branch:
        alignment["reason_codes"] = list(dict.fromkeys([*alignment.get("reason_codes", []), "implement_branch_switch_dirty_worktree"]))
    unresolved_services = [item for item in delivery_services if item not in {"."}]
    if unresolved_services:
        alignment["reason_codes"] = list(
            dict.fromkeys([*alignment.get("reason_codes", []), "implement_direct_delivery_service_scope_unresolved"])
        )
    blocked = bool(alignment.get("blocked")) or bool(unresolved_services)
    if dirty_worktree and require_clean_worktree_for_switch and current_branch != expected_branch:
        blocked = True

    if not alignment.get("repo_detected"):
        summary = "implement branch preflight blocked: git repository not detected"
        recommended_commands: list[str] = []
    elif alignment.get("detached_head"):
        summary = "implement branch preflight blocked: detached HEAD is not allowed for implement"
        recommended_commands = [f"git switch {expected_branch}"] if expected_branch else []
    elif current_branch != expected_branch:
        if dirty_worktree and require_clean_worktree_for_switch:
            summary = (
                f"implement branch preflight blocked: expected {expected_branch}, dirty worktree blocks switch from "
                f"{current_branch or 'unknown'}"
            )
            switch_command = (
                f"git switch {expected_branch}"
                if branch_exists
                else f"git switch -c {expected_branch}"
            )
            recommended_commands = [f"git stash push -u && {switch_command}"]
        else:
            summary = f"implement branch preflight blocked: expected {expected_branch}, current {current_branch or 'unknown'}"
            recommended_commands = [
                f"git switch {expected_branch}"
                if branch_exists
                else f"git switch -c {expected_branch}"
            ]
    else:
        summary = f"implement branch preflight passed on {expected_branch}"
        recommended_commands = []

    return {
        "schema_version": "1.0",
        "status": "blocked" if blocked else "pass",
        "summary": summary,
        "blocked": blocked,
        "version": version,
        "expected_branch": expected_branch,
        "current_branch": current_branch,
        "current_tag": str(alignment.get("current_tag", "") or ""),
        "branch_exists": branch_exists,
        "dirty_worktree": dirty_worktree,
        "require_clean_worktree_for_switch": require_clean_worktree_for_switch,
        "recommended_command": recommended_commands[0] if recommended_commands else "",
        "recommended_commands": recommended_commands,
        "direct_delivery_services": delivery_services or ["."],
        "service_scope": {
            "status": "blocked" if unresolved_services else "pass",
            "direct_delivery_services": delivery_services or ["."],
            "verified_roots": ["."],
            "unresolved_services": unresolved_services,
        },
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


def ensure_expected_worktree_lane(
    project_root: Path,
    expected_branch: str,
    *,
    worktree_path: str,
    base_branch: str = "main",
) -> dict[str, Any]:
    target_path = Path(worktree_path).expanduser().resolve()
    root = project_root.expanduser().resolve()
    if not expected_branch:
        return {
            "status": "failed",
            "reason": "missing_expected_branch",
            "worktree_path": str(target_path),
        }
    if target_path == root:
        switch_payload = switch_to_expected_branch(root, expected_branch, create_if_missing=True)
        return {
            "status": "switched" if switch_payload.get("status") == "switched" else "failed",
            "expected_branch": expected_branch,
            "worktree_path": str(target_path),
            "switch_attempt": switch_payload,
        }
    if target_path.exists() and git_repo_exists(target_path):
        switch_payload = switch_to_expected_branch(target_path, expected_branch, create_if_missing=True)
        return {
            "status": "switched" if switch_payload.get("status") == "switched" else "failed",
            "expected_branch": expected_branch,
            "worktree_path": str(target_path),
            "switch_attempt": switch_payload,
        }
    commands = [
        ["git", "worktree", "add", str(target_path), expected_branch],
        ["git", "worktree", "add", "-b", expected_branch, str(target_path), base_branch],
    ]
    attempts: list[dict[str, Any]] = []
    for command in commands:
        try:
            result = subprocess.run(
                command,
                cwd=root,
                capture_output=True,
                text=True,
                timeout=20,
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
                "status": "created",
                "expected_branch": expected_branch,
                "worktree_path": str(target_path),
                "attempts": attempts,
            }
    return {
        "status": "failed",
        "expected_branch": expected_branch,
        "worktree_path": str(target_path),
        "attempts": attempts,
    }
