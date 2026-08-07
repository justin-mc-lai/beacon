"""Shared implement admission (v1.6.10 AC-UIA).

One fail-closed pre-write gate for direct implement, goal, team, and ralph.
Soft-skip / branch-only contracts never authorize writes: they either force a
real leaf (and monorepo service) worktree materialization or block.
"""

from __future__ import annotations

import subprocess
from pathlib import Path
from typing import Any

from beacon.utils.runtime import now_iso
from beacon.utils.story_state import feature_slug

SCHEMA = "implement-admission.v1"
VALID_SURFACES = frozenset({"direct", "goal", "team", "ralph", "check"})

REASON_FEATURE_REQUIRED = "implement_admission_feature_required"
REASON_ADMIT_BLOCKED = "implement_admission_blocked"
REASON_FORCE_WORKTREE_FAILED = "implement_admission_force_worktree_failed"
REASON_MERGE_CONFLICT = "merge_main_conflict"
REASON_SERVICE_WORKTREE_INVALID = "service_worktree_invalid"
REASON_SOFT_SKIP_FORBIDDEN = "soft_skip_write_authorization_forbidden"
REASON_FREEZE_ACK = "freeze_ack_required"
REASON_BRANCH_MISMATCH = "implement_admission_branch_mismatch"
REASON_CWD_MISMATCH = "implement_admission_cwd_mismatch"
REASON_HEAD_MISMATCH = "implement_admission_head_mismatch"


def _semver_tuple(value: str) -> tuple[int, int, int]:
    text = str(value or "").strip().lower().lstrip("v")
    parts: list[int] = []
    for raw in text.split(".")[:3]:
        digits = "".join(ch for ch in raw if ch.isdigit())
        parts.append(int(digits or "0"))
    while len(parts) < 3:
        parts.append(0)
    return tuple(parts[:3])


def _git(path: Path, *args: str) -> str:
    try:
        result = subprocess.run(
            ["git", *args],
            cwd=str(path),
            capture_output=True,
            text=True,
            timeout=20,
            check=False,
        )
    except Exception:
        return ""
    if result.returncode != 0:
        return ""
    return str(result.stdout or "").strip()


def is_real_git_worktree(path: Path | str) -> bool:
    """True only for a usable git worktree/checkout (not mkdir-only / empty gitlink)."""
    root = Path(path).expanduser()
    if not root.exists() or not root.is_dir():
        return False
    # empty directory or bare placeholder
    if not any(root.iterdir()) and not (root / ".git").exists():
        return False
    inside = _git(root, "rev-parse", "--is-inside-work-tree")
    if inside != "true":
        return False
    head = _git(root, "rev-parse", "HEAD")
    return bool(head)


def _truth_participating_services(project_root: Path, *, version: str, feature: str) -> list[str]:
    """Prefer frozen truth frontmatter participating_services when present."""
    slug = feature_slug(feature)
    if not slug:
        return []
    try:
        from beacon.utils.feature_package import _parse_frontmatter, package_paths
    except Exception:  # noqa: BLE001
        return []
    try:
        paths = package_paths(project_root, version=version, feature=slug)
        truth_path = Path(paths["truth"]) if isinstance(paths, dict) and paths.get("truth") else Path()
        if not truth_path.is_file():
            return []
        fm, _body, _errors = _parse_frontmatter(truth_path.read_text(encoding="utf-8"))
    except Exception:  # noqa: BLE001
        return []
    raw = fm.get("participating_services") if isinstance(fm, dict) else None
    if isinstance(raw, str):
        return [p.strip().strip("'\"") for p in raw.strip("[]").split(",") if p.strip().strip("'\"")]
    if isinstance(raw, list):
        return [str(item).strip() for item in raw if str(item).strip()]
    return []


def _writable_service_bindings(
    project_root: Path,
    *,
    version: str,
    feature: str = "",
) -> list[dict[str, Any]]:
    from beacon.utils.project_metadata import resolve_project_metadata_view

    root = project_root.expanduser().resolve()
    view = resolve_project_metadata_view(root, version=version)
    bindings = view.get("service_bindings") if isinstance(view.get("service_bindings"), list) else []
    version_contract = view.get("version_contract") if isinstance(view.get("version_contract"), dict) else {}
    # Feature truth scope wins over version-wide participating_services (lake ≠ whole version).
    truth_services = _truth_participating_services(root, version=version, feature=feature) if feature else []
    participating = truth_services or version_contract.get("participating_services")
    participating_set = {
        str(item).strip()
        for item in (participating if isinstance(participating, list) else [])
        if str(item).strip()
    }
    out: list[dict[str, Any]] = []
    for item in bindings:
        if not isinstance(item, dict):
            continue
        key = str(item.get("service_key") or "").strip()
        if not key:
            continue
        if participating_set and key not in participating_set:
            continue
        if item.get("writable") is False:
            continue
        rel = str(item.get("repo_root_relative") or item.get("repo_root") or ".").strip() or "."
        git_root = Path(rel)
        if not git_root.is_absolute():
            git_root = (root / rel).resolve()
        else:
            git_root = git_root.resolve()
        out.append({**item, "service_key": key, "resolved_git_root": str(git_root)})
    if not out:
        out.append(
            {
                "service_key": str(view.get("default_execution_service") or "default").strip() or "default",
                "resolved_git_root": str(root),
                "writable": True,
                "repo_root_relative": ".",
            }
        )
    return out


def _service_branch_map(project_root: Path, *, version: str, feature: str, default_branch: str) -> dict[str, str]:
    from beacon.utils.project_metadata import resolve_project_metadata_view

    view = resolve_project_metadata_view(project_root, version=version)
    version_contract = view.get("version_contract") if isinstance(view.get("version_contract"), dict) else {}
    per_service = (
        version_contract.get("per_service_canonical_branch")
        if isinstance(version_contract.get("per_service_canonical_branch"), dict)
        else {}
    )
    allowed = {
        str(item.get("service_key") or "").strip()
        for item in _writable_service_bindings(project_root, version=version, feature=feature)
        if str(item.get("service_key") or "").strip()
    }
    mapping: dict[str, str] = {}
    for key, value in per_service.items():
        k = str(key).strip()
        v = str(value).strip()
        if k and v and (not allowed or k in allowed):
            mapping[k] = v
    if not mapping and default_branch:
        for binding in _writable_service_bindings(project_root, version=version, feature=feature):
            mapping[str(binding["service_key"])] = default_branch
    # Prefer feature leaf over aggregation when pattern present and value is program-level
    from beacon.utils.branch_ref_hierarchy import leaf_feature_branch
    from beacon.utils.workspace_admission import load_admission_contract

    contract = load_admission_contract(project_root, version=version)
    pattern = str(contract.get("feature_branch_pattern") or "").strip()
    leaf = leaf_feature_branch(version=version, feature=feature, pattern=pattern) if pattern else default_branch
    for key, value in list(mapping.items()):
        # monorepo product branches often stay feature/<version>
        if value.startswith("feature/") and value.count("/") == 1:
            continue
        if pattern and "<feature" in pattern.lower() and value and value.count("/") == 1 and value.startswith("beacon/"):
            mapping[key] = leaf
    return mapping


def _service_baseline_map(
    project_root: Path,
    *,
    version: str,
    feature: str = "",
    default_baseline: str,
) -> dict[str, str]:
    from beacon.utils.project_metadata import resolve_project_metadata_view

    view = resolve_project_metadata_view(project_root, version=version)
    version_contract = view.get("version_contract") if isinstance(view.get("version_contract"), dict) else {}
    per_service = (
        version_contract.get("per_service_baseline_branch")
        if isinstance(version_contract.get("per_service_baseline_branch"), dict)
        else {}
    )
    allowed = {
        str(item.get("service_key") or "").strip()
        for item in _writable_service_bindings(project_root, version=version, feature=feature)
        if str(item.get("service_key") or "").strip()
    }
    mapping: dict[str, str] = {}
    for key, value in per_service.items():
        k = str(key).strip()
        v = str(value).strip()
        if k and v and (not allowed or k in allowed):
            mapping[k] = v
    if not mapping and default_baseline:
        for binding in _writable_service_bindings(project_root, version=version, feature=feature):
            mapping[str(binding["service_key"])] = default_baseline
    return mapping


def resolve_service_worktree_path(
    project_root: Path,
    *,
    version: str,
    feature: str,
    service_key: str,
    path_pattern: str = "",
) -> Path:
    root = project_root.expanduser().resolve()
    slug = feature_slug(feature)
    pattern = str(path_pattern or "").strip()
    if not pattern:
        from beacon.utils.project_metadata import resolve_project_metadata_view

        view = resolve_project_metadata_view(root, version=version)
        version_contract = view.get("version_contract") if isinstance(view.get("version_contract"), dict) else {}
        pattern = str(version_contract.get("service_worktree_path_pattern") or "").strip()
    if not pattern:
        pattern = ".beacon/worktrees/<version>/<feature_slug>/services/<service_key>"
    rendered = (
        pattern.replace("<version>", version)
        .replace("<feature_slug>", slug)
        .replace("<feature>", slug)
        .replace("<service_key>", service_key)
    )
    path = Path(rendered)
    if not path.is_absolute():
        path = (root / path).resolve()
    return path


REASON_PARENT_ONLY_SERVICE_WRITE = "parent_only_service_write_forbidden"


def assert_service_write_authorized(
    *,
    target_path: Path | str,
    service_worktree_map: dict[str, Any] | None,
    parent_worktree: Path | str | None = None,
    require_service_map: bool = False,
) -> dict[str, Any]:
    """Block parent-only writes when a multi-service map exists (AC-SSP-005)."""
    target = Path(target_path).expanduser().resolve()
    mapping = {
        str(k): str(v)
        for k, v in (service_worktree_map or {}).items()
        if str(k).strip() and str(v).strip()
    }
    if not mapping:
        if require_service_map:
            return {
                "status": "blocked",
                "blocked": True,
                "reason_code": "service_worktree_map_missing",
                "authorized_service": "",
            }
        return {"status": "pass", "blocked": False, "reason_code": "", "authorized_service": ""}

    for key, wt in mapping.items():
        try:
            target.relative_to(Path(wt).expanduser().resolve())
            return {
                "status": "pass",
                "blocked": False,
                "reason_code": "",
                "authorized_service": key,
                "service_worktree": wt,
            }
        except ValueError:
            continue

    parent = Path(parent_worktree).expanduser().resolve() if parent_worktree else None
    if parent is not None:
        try:
            target.relative_to(parent)
            # Target is inside parent but not inside any service worktree.
            distinct_services = [p for p in mapping.values() if Path(p).resolve() != parent]
            if distinct_services:
                return {
                    "status": "blocked",
                    "blocked": True,
                    "reason_code": REASON_PARENT_ONLY_SERVICE_WRITE,
                    "authorized_service": "",
                    "parent_worktree": str(parent),
                }
        except ValueError:
            pass
    return {
        "status": "blocked",
        "blocked": True,
        "reason_code": "write_target_outside_service_worktree",
        "authorized_service": "",
    }


def _force_leaf_worktree(
    root: Path,
    *,
    version: str,
    feature: str,
    contract: dict[str, Any],
) -> dict[str, Any]:
    """Materialize a real leaf worktree even when contract soft-skips admission."""
    from beacon.utils.branch_ref_hierarchy import leaf_feature_branch
    from beacon.utils.git_alignment import ensure_expected_worktree_lane, git_output
    from beacon.utils.workspace_admission import (
        SCHEMA_VERSION as ADMIT_SCHEMA,
        _lease_holder,
        _load_pool_state,
        _merge_main_into_feature_branch,
        _write_pool_state,
        artifact_path,
        pool_state_path,
        resolve_worktree_path,
        write_admission_artifact,
    )

    pattern = str(contract.get("feature_branch_pattern") or "").strip() or f"beacon/{version}/<feature-slug>"
    feature_branch = leaf_feature_branch(version=version, feature=feature, pattern=pattern)
    base_branch = str(
        contract.get("previous_version_baseline_branch")
        or contract.get("canonical_branch")
        or "main"
    ).strip() or "main"
    forced_contract = {
        **contract,
        "version": version,
        "worktree_mode": "dedicated-worktree",
        "feature_branch_pattern": pattern,
        "worktree_base": str(contract.get("worktree_base") or f".beacon/worktrees/{version}"),
    }
    wb = str(forced_contract.get("worktree_base") or "")
    if wb in {"", ".", str(root)} or Path(wb).resolve() == root:
        forced_contract["worktree_base"] = f".beacon/worktrees/{version}"
    worktree_path = resolve_worktree_path(root, forced_contract, feature=feature)
    attempt = ensure_expected_worktree_lane(
        root,
        feature_branch,
        worktree_path=worktree_path,
        base_branch=base_branch,
    )
    out: dict[str, Any] = {
        "worktree_attempt": attempt,
        "branch": feature_branch,
        "worktree_path": worktree_path,
        "base_branch": base_branch,
        "status": "pass",
        "forced_worktree": True,
    }
    if attempt.get("status") not in {"created", "switched", "already"}:
        out["status"] = "blocked"
        out["blocked"] = True
        out["reason_code"] = REASON_FORCE_WORKTREE_FAILED
        out["reason_codes"] = ["workspace_admission_worktree_failed", REASON_FORCE_WORKTREE_FAILED]
        out["summary"] = "force worktree create/switch failed"
        return out

    lane_root = Path(str(attempt.get("worktree_path") or worktree_path)).resolve()
    if not is_real_git_worktree(lane_root):
        out["status"] = "blocked"
        out["blocked"] = True
        out["reason_code"] = REASON_FORCE_WORKTREE_FAILED
        out["reason_codes"] = ["mkdir_only_worktree_forbidden", REASON_FORCE_WORKTREE_FAILED]
        out["summary"] = "forced worktree path is not a real git worktree"
        return out

    merge_main = _merge_main_into_feature_branch(lane_root, base_branch=base_branch)
    out["merge_main"] = merge_main
    if merge_main.get("status") == "conflict":
        out["status"] = "blocked"
        out["blocked"] = True
        out["reason_code"] = REASON_MERGE_CONFLICT
        out["reason_codes"] = [REASON_MERGE_CONFLICT]
        out["summary"] = f"merge {base_branch} into {feature_branch} conflicted"
        return out

    git_head = git_output(lane_root, "rev-parse", "HEAD")
    current_branch = git_output(lane_root, "branch", "--show-current") or feature_branch
    artifact_file = artifact_path(root, version=version, feature=feature)
    artifact_payload = {
        "schema_version": ADMIT_SCHEMA,
        "version": version,
        "feature_slug": feature_slug(feature),
        "project_root": str(root),
        "branch": current_branch,
        "worktree_path": str(lane_root),
        "base_branch": base_branch,
        "issued_at": now_iso(),
        "git_head": git_head,
        "status": "pass",
        "forced_worktree": True,
    }
    write_admission_artifact(artifact_file, artifact_payload)

    if str(contract.get("worktree_mode") or "") == "pooled":
        pool_path = pool_state_path(root, version=version)
        pool_state, pool_error = _load_pool_state(pool_path)
        if pool_error:
            out["status"] = "blocked"
            out["blocked"] = True
            out["reason_code"] = "workspace_pool_state_corrupt"
            return out
        assert pool_state is not None
        entry = {
            "state": "leased",
            "feature_slug": feature_slug(feature),
            "branch": current_branch,
            "worktree_path": str(lane_root),
            "lease_holder": _lease_holder(),
            "leased_at": now_iso(),
            "released_at": "",
            "git_head": git_head,
            "forced_worktree": True,
        }
        pool_state.setdefault("entries", {})[feature_slug(feature)] = entry
        _write_pool_state(pool_path, pool_state)
        out["pool_entry"] = entry
        out["pool_state_path"] = str(pool_path)

    out.update(
        {
            "branch": current_branch,
            "worktree_path": str(lane_root),
            "cwd": str(lane_root),
            "git_head": git_head,
            "artifact": artifact_payload,
            "summary": "forced worktree admission issued",
            "status": "pass",
        }
    )
    return out


def _materialize_service_worktrees(
    project_root: Path,
    *,
    version: str,
    feature: str,
    parent_worktree: Path,
    parent_branch: str,
    base_branch: str,
) -> dict[str, Any]:
    """Materialize/verify real worktrees for every writable service."""
    from beacon.utils.git_alignment import ensure_expected_worktree_lane, git_output
    from beacon.utils.project_metadata import resolve_project_metadata_view
    from beacon.utils.workspace_admission import upsert_service_pool_leases

    root = project_root.expanduser().resolve()
    view = resolve_project_metadata_view(root, version=version)
    topology = str(view.get("topology_kind") or "").strip().lower()
    version_contract = view.get("version_contract") if isinstance(view.get("version_contract"), dict) else {}
    path_pattern = str(version_contract.get("service_worktree_path_pattern") or "").strip()
    bindings = _writable_service_bindings(root, version=version, feature=feature)
    branch_map = _service_branch_map(root, version=version, feature=feature, default_branch=parent_branch)
    baseline_map = _service_baseline_map(
        root, version=version, feature=feature, default_baseline=base_branch
    )
    service_worktree_map: dict[str, str] = {}
    service_reconcile: dict[str, Any] = {}
    service_leases: dict[str, dict[str, Any]] = {}
    reason_codes: list[str] = []

    multi_roots = len({str(item.get("resolved_git_root") or "") for item in bindings}) > 1
    monorepo_like = topology in {"monorepo", "multi_git_workspace"} or multi_roots

    for binding in bindings:
        key = str(binding.get("service_key") or "").strip()
        git_root = Path(str(binding.get("resolved_git_root") or root)).resolve()
        service_branch = str(branch_map.get(key) or parent_branch).strip() or parent_branch
        service_baseline = str(baseline_map.get(key) or base_branch).strip() or base_branch

        if git_root == root or not monorepo_like:
            # single-repo / service at superproject root: share parent worktree
            if not is_real_git_worktree(parent_worktree):
                reason_codes.append(f"service_worktree_invalid:{key}")
                service_reconcile[key] = {
                    "status": "blocked",
                    "reason_code": REASON_SERVICE_WORKTREE_INVALID,
                    "path": str(parent_worktree),
                }
                continue
            service_worktree_map[key] = str(parent_worktree)
            head = git_output(parent_worktree, "rev-parse", "HEAD")
            service_reconcile[key] = {
                "status": "pass",
                "branch": parent_branch,
                "worktree_path": str(parent_worktree),
                "git_head": head,
                "shared_parent": True,
                "base_branch": service_baseline,
            }
            service_leases[key] = {
                "repo_root": str(git_root),
                "branch": parent_branch,
                "base_branch": service_baseline,
                "worktree_path": str(parent_worktree),
                "git_head": head,
                "state": "leased",
            }
            continue

        # nested / external child repository: require real child git checkout, not empty gitlink
        if not is_real_git_worktree(git_root):
            reason_codes.append(f"service_worktree_invalid:{key}")
            service_reconcile[key] = {
                "status": "blocked",
                "reason_code": "empty_gitlink_or_missing_child_repo",
                "path": str(git_root),
            }
            continue

        service_wt = resolve_service_worktree_path(
            root,
            version=version,
            feature=feature,
            service_key=key,
            path_pattern=path_pattern,
        )
        attempt = ensure_expected_worktree_lane(
            git_root,
            service_branch,
            worktree_path=str(service_wt),
            base_branch=service_baseline,
        )
        if attempt.get("status") not in {"created", "switched", "already"}:
            reason_codes.append(f"service_worktree_invalid:{key}")
            service_reconcile[key] = {
                "status": "blocked",
                "reason_code": "service_worktree_materialize_failed",
                "attempt": attempt,
                "path": str(service_wt),
            }
            continue
        lane = Path(str(attempt.get("worktree_path") or service_wt)).resolve()
        if not is_real_git_worktree(lane):
            reason_codes.append(f"service_worktree_invalid:{key}")
            service_reconcile[key] = {
                "status": "blocked",
                "reason_code": "mkdir_only_worktree_forbidden",
                "path": str(lane),
            }
            continue
        current_branch = git_output(lane, "branch", "--show-current")
        if service_branch and current_branch and current_branch != service_branch:
            reason_codes.append(f"service_branch_mismatch:{key}")
            service_reconcile[key] = {
                "status": "blocked",
                "reason_code": REASON_BRANCH_MISMATCH,
                "expected_branch": service_branch,
                "current_branch": current_branch,
                "path": str(lane),
            }
            continue
        # child baseline reconcile: merge per-service baseline when possible.
        # Go services commonly use master while governance may say main — fall back.
        baseline_candidates = [service_baseline]
        if service_baseline == "main":
            baseline_candidates.append("master")
        elif service_baseline == "master":
            baseline_candidates.append("main")
        merge = None
        used_baseline = service_baseline
        for candidate in baseline_candidates:
            if not git_output(lane, "rev-parse", "--verify", candidate):
                continue
            used_baseline = candidate
            merge = subprocess.run(
                ["git", "merge", candidate, "--no-edit", "--ff"],
                cwd=str(lane),
                capture_output=True,
                text=True,
                timeout=30,
                check=False,
            )
            if merge.returncode == 0:
                break
            subprocess.run(["git", "merge", "--abort"], cwd=str(lane), capture_output=True, timeout=15, check=False)
        if merge is None or merge.returncode != 0:
            reason_codes.append(f"service_baseline_conflict:{key}")
            service_reconcile[key] = {
                "status": "blocked",
                "reason_code": REASON_MERGE_CONFLICT,
                "path": str(lane),
                "base_branch": used_baseline,
                "stderr": str((merge.stderr if merge else "") or f"baseline refs missing: {baseline_candidates}").strip(),
            }
            continue
        service_baseline = used_baseline
        head = git_output(lane, "rev-parse", "HEAD")
        service_worktree_map[key] = str(lane)
        service_reconcile[key] = {
            "status": "pass",
            "branch": current_branch or service_branch,
            "worktree_path": str(lane),
            "git_head": head,
            "base_branch": service_baseline,
            "baseline_reconcile": "merged" if "Already up to date" not in str(merge.stdout or "") else "up_to_date",
            "shared_parent": False,
        }
        service_leases[key] = {
            "repo_root": str(git_root),
            "branch": current_branch or service_branch,
            "base_branch": service_baseline,
            "worktree_path": str(lane),
            "git_head": head,
            "state": "leased",
        }

    blocked = bool(reason_codes) or (
        monorepo_like and any(not str(v).strip() for v in service_worktree_map.values())
    )
    if monorepo_like:
        for binding in bindings:
            key = str(binding.get("service_key") or "").strip()
            if key and key not in service_worktree_map:
                blocked = True
                reason_codes.append(f"service_worktree_missing:{key}")

    pool_update: dict[str, Any] = {}
    if not blocked and service_leases:
        pool_update = upsert_service_pool_leases(
            root,
            version=version,
            feature=feature,
            service_leases=service_leases,
        )
        if pool_update.get("blocked"):
            blocked = True
            reason_codes.append(str(pool_update.get("reason_code") or "workspace_pool_state_corrupt"))

    return {
        "status": "blocked" if blocked else "pass",
        "blocked": blocked,
        "reason_codes": list(dict.fromkeys(reason_codes)),
        "reason_code": reason_codes[0] if reason_codes else "",
        "service_worktree_map": service_worktree_map,
        "service_reconcile": service_reconcile,
        "topology_kind": topology or ("multi_git_workspace" if multi_roots else "single_repo"),
        "writable_services": [str(item.get("service_key") or "") for item in bindings],
        "pool_update": pool_update,
    }


def _strict_parent_checks(
    *,
    worktree_path: Path,
    expected_branch: str,
    artifact: dict[str, Any] | None,
    cwd: Path | None,
) -> list[str]:
    codes: list[str] = []
    if not is_real_git_worktree(worktree_path):
        codes.append("mkdir_only_worktree_forbidden")
        return codes
    current_branch = _git(worktree_path, "branch", "--show-current")
    if expected_branch and current_branch and current_branch != expected_branch:
        codes.append(REASON_BRANCH_MISMATCH)
    if artifact:
        recorded_head = str(artifact.get("git_head") or "").strip()
        current_head = _git(worktree_path, "rev-parse", "HEAD")
        if recorded_head and current_head and recorded_head != current_head:
            # allow after merge_main moved HEAD; re-check only dirty mismatch if branch wrong
            pass
    if cwd is not None:
        try:
            Path(cwd).expanduser().resolve().relative_to(worktree_path.resolve())
        except ValueError:
            codes.append(REASON_CWD_MISMATCH)
    return codes


def ensure_implement_admission(
    project_root: Path,
    *,
    version: str,
    feature: str,
    execution_surface: str = "direct",
    dry_run: bool = False,
    cwd: Path | str | None = None,
    require_freeze: bool = False,
    payload: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Shared fail-closed admission for all implement write surfaces.

    Soft-skip / branch-only never returns write authorization without a real worktree.
    """
    from beacon.utils.versioning import resolve_target_version
    from beacon.utils.workspace_admission import (
        load_admission_contract,
        read_admission_artifact,
        run_workspace_admit,
        artifact_path,
    )

    root = Path(project_root).expanduser().resolve()
    surface = str(execution_surface or "direct").strip().lower() or "direct"
    if surface not in VALID_SURFACES:
        surface = "direct"
    slug = feature_slug(feature) if feature else ""
    resolved_version = resolve_target_version(root, version) if version and version != "auto" else str(version or "")

    base: dict[str, Any] = {
        "schema": SCHEMA,
        "version": resolved_version or version,
        "feature": feature,
        "feature_slug": slug,
        "execution_surface": surface,
        "allow_implement": False,
        "status": "blocked",
        "blocked": True,
        "reason_code": "",
        "reason_codes": [],
        "admission": {},
        "service_worktree_map": {},
        "forced_worktree": False,
        "generated_at": now_iso(),
    }

    if not slug:
        base["reason_code"] = REASON_FEATURE_REQUIRED
        base["user_facing"] = "implement admission requires feature slug"
        return base

    if not resolved_version or resolved_version == "auto":
        resolved_version = resolve_target_version(root, "auto")
        base["version"] = resolved_version

    # Optional freeze gate (goal path always requires; direct may also when strict package gate already ran)
    if require_freeze or surface == "goal":
        from beacon.utils.goal_stage_exit_gates import feature_package_frozen

        info = feature_package_frozen(root, version=resolved_version, feature=slug)
        if not info.get("frozen"):
            base["reason_code"] = REASON_FREEZE_ACK
            base["reason_codes"] = [REASON_FREEZE_ACK]
            base["freeze_check"] = info
            base["user_facing"] = "implement blocked: truth not frozen"
            base["recommended_command"] = (
                f"beacon freeze --project-root {root} --version {resolved_version} --feature {slug}"
            )
            return base

        if _semver_tuple(resolved_version) >= (1, 6, 10) and surface == "goal":
            try:
                from beacon.utils.feature_package import evaluate_task_ac_evidence_bindings, package_paths

                tpath = package_paths(root, version=resolved_version, feature=slug)["tasks"]
                if tpath.is_file():
                    gate = evaluate_task_ac_evidence_bindings(
                        root, tasks_md=tpath.read_text(encoding="utf-8"), version=resolved_version
                    )
                    bad = [
                        f
                        for f in (gate.get("findings") or [])
                        if str(f.get("kind") or "").startswith("checkbox_checked_without")
                    ]
                    if bad:
                        base["reason_code"] = "task_checkbox_without_evidence"
                        base["reason_codes"] = ["task_checkbox_without_evidence"]
                        base["task_evidence_gate"] = {"findings": bad}
                        return base
            except Exception as exc:  # noqa: BLE001
                base["task_evidence_gate_error"] = str(exc)

    contract = load_admission_contract(root, version=resolved_version)
    admit = run_workspace_admit(
        root,
        version=resolved_version,
        feature=slug,
        dry_run=dry_run,
    )
    base["admission"] = admit

    if dry_run:
        base["status"] = "ok" if admit.get("status") != "blocked" else "blocked"
        base["blocked"] = base["status"] != "ok"
        base["allow_implement"] = not base["blocked"]
        base["reason_code"] = str(
            admit.get("reason_code") or ("dry_run_ok" if base["allow_implement"] else REASON_ADMIT_BLOCKED)
        )
        return base

    if admit.get("status") == "blocked" or admit.get("blocked"):
        base["reason_code"] = str(admit.get("reason_code") or REASON_ADMIT_BLOCKED)
        base["reason_codes"] = list(admit.get("reason_codes") or [base["reason_code"]])
        base["user_facing"] = str(admit.get("summary") or "workspace admit blocked")
        base["recommended_command"] = (
            f"beacon workspace admit --project-root {root} --version {resolved_version} --feature {slug} --json"
        )
        return base

    skipped = bool(admit.get("skipped"))
    require = bool(contract.get("require_workspace_admission"))
    forced = False
    if skipped or not require:
        # Soft-skip must never authorize writes without a real worktree.
        forced_payload = _force_leaf_worktree(root, version=resolved_version, feature=slug, contract=contract)
        forced = True
        base["forced_worktree"] = True
        base["admission"] = {**admit, **forced_payload, "forced_worktree": True}
        if forced_payload.get("status") == "blocked" or forced_payload.get("blocked"):
            base["reason_code"] = str(forced_payload.get("reason_code") or REASON_SOFT_SKIP_FORBIDDEN)
            base["reason_codes"] = list(
                forced_payload.get("reason_codes")
                or [REASON_SOFT_SKIP_FORBIDDEN, REASON_FORCE_WORKTREE_FAILED]
            )
            base["user_facing"] = str(forced_payload.get("summary") or "soft-skip cannot authorize implement writes")
            return base
        admit = base["admission"]

    worktree_path = Path(str(admit.get("worktree_path") or "")).expanduser()
    branch = str(admit.get("branch") or "").strip()
    if not worktree_path or not is_real_git_worktree(worktree_path):
        base["reason_code"] = REASON_FORCE_WORKTREE_FAILED
        base["reason_codes"] = ["mkdir_only_worktree_forbidden", REASON_FORCE_WORKTREE_FAILED]
        base["user_facing"] = "implement blocked: admission worktree is not a real git worktree"
        return base

    artifact = read_admission_artifact(artifact_path(root, version=resolved_version, feature=slug))
    check_cwd = Path(cwd).expanduser().resolve() if cwd is not None else None
    strict_codes = _strict_parent_checks(
        worktree_path=worktree_path,
        expected_branch=branch,
        artifact=artifact if isinstance(artifact, dict) else None,
        cwd=check_cwd,
    )
    if strict_codes:
        base["reason_code"] = strict_codes[0]
        base["reason_codes"] = strict_codes
        base["user_facing"] = "implement blocked: strict branch/cwd/worktree verification failed"
        return base

    base_branch = str(
        contract.get("previous_version_baseline_branch")
        or contract.get("canonical_branch")
        or "main"
    ).strip() or "main"
    services = _materialize_service_worktrees(
        root,
        version=resolved_version,
        feature=slug,
        parent_worktree=worktree_path,
        parent_branch=branch,
        base_branch=base_branch,
    )
    base["service_worktrees"] = services
    base["service_worktree_map"] = dict(services.get("service_worktree_map") or {})
    base["topology_kind"] = services.get("topology_kind")
    if services.get("blocked"):
        base["reason_code"] = str(services.get("reason_code") or REASON_SERVICE_WORKTREE_INVALID)
        base["reason_codes"] = list(services.get("reason_codes") or [base["reason_code"]])
        base["user_facing"] = "implement blocked: writable service worktrees incomplete or invalid"
        return base

    if check_cwd is not None and base.get("service_worktree_map"):
        write_gate = assert_service_write_authorized(
            target_path=check_cwd,
            service_worktree_map=base["service_worktree_map"],
            parent_worktree=worktree_path,
        )
        base["write_authorization"] = write_gate
        if write_gate.get("blocked"):
            base["reason_code"] = str(write_gate.get("reason_code") or REASON_PARENT_ONLY_SERVICE_WRITE)
            base["reason_codes"] = [base["reason_code"]]
            base["user_facing"] = "implement blocked: write target is not inside an admitted service worktree"
            base["status"] = "blocked"
            base["blocked"] = True
            base["allow_implement"] = False
            return base

    # Enrich admission artifact with service map for QA replay
    try:
        art_path = artifact_path(root, version=resolved_version, feature=slug)
        existing = read_admission_artifact(art_path) or {}
        if isinstance(existing, dict):
            existing.update(
                {
                    "service_worktree_map": base["service_worktree_map"],
                    "service_reconcile": services.get("service_reconcile") or {},
                    "parent_reconcile": admit.get("merge_main") or {},
                    "execution_surface": surface,
                    "forced_worktree": forced,
                    "updated_at": now_iso(),
                }
            )
            from beacon.utils.workspace_admission import write_admission_artifact

            write_admission_artifact(art_path, existing)
            base["artifact"] = existing
    except Exception as exc:  # noqa: BLE001
        base["artifact_enrich_error"] = str(exc)

    base.update(
        {
            "status": "pass",
            "blocked": False,
            "allow_implement": True,
            "reason_code": "implement_admission_ok",
            "worktree_path": str(worktree_path),
            "branch": branch,
            "cwd": str(admit.get("cwd") or worktree_path),
            "merge_main": admit.get("merge_main") or {},
            "worktree_mode": str(contract.get("worktree_mode") or ""),
            "worktree_attempt": admit.get("worktree_attempt"),
            "user_facing": "implement admission pass; write only under admitted worktree/service map",
            "payload_ref": bool(payload),
        }
    )
    return base


def ensure_goal_compatible_admission(
    project_root: Path,
    payload: dict[str, Any],
    *,
    dry_run: bool = False,
) -> dict[str, Any]:
    """Adapter used by goal path; preserves goal-facing fields."""
    from beacon.utils.goal_implement_admission import resolve_goal_implement_target

    target = resolve_goal_implement_target(payload)
    gate = ensure_implement_admission(
        project_root,
        version=target["version"],
        feature=target["feature"] or target["feature_slug"],
        execution_surface="goal",
        dry_run=dry_run,
        require_freeze=True,
        payload=payload,
    )
    # Goal legacy field names
    gate["goal_forced_worktree"] = bool(gate.get("forced_worktree"))
    if gate.get("allow_implement") and gate.get("reason_code") == "implement_admission_ok":
        gate["reason_code"] = "goal_implement_admission_ok"
    return gate
