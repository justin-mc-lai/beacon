"""Goal implement admission hard gate (Scheme A / UD-GIA).

Before product-goal may dispatch implement (ralph) write paths:
  1. resolve version + feature (lake)
  2. call run_workspace_admit (reuse branch governance + pool + merge-main)
  3. if contract skips require: still force dedicated leaf worktree materialize
     (goal policy — closes main-write hole when require_workspace_admission=false)
  4. fail-closed: no soft fallback to truth_canonical implement

Does NOT auto-release or self-complete.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from beacon.utils.runtime import now_iso
from beacon.utils.story_state import feature_slug

SCHEMA = "goal-implement-admission.v1"
REASON_FEATURE_REQUIRED = "goal_implement_feature_required"
REASON_ADMIT_BLOCKED = "goal_implement_admission_blocked"
REASON_FORCE_WORKTREE_FAILED = "goal_implement_force_worktree_failed"
REASON_ENF_ADMISSION = "goal_implement_admission_required"  # UD-ENF-003
REASON_MERGE_CONFLICT = "merge_main_conflict"


def resolve_goal_implement_target(payload: dict[str, Any]) -> dict[str, str]:
    """Resolve version + feature for implement admission from goal payload."""
    version = str(payload.get("version") or "").strip() or "auto"
    feature = str(payload.get("feature") or "").strip()
    lakes = [str(x).strip() for x in (payload.get("lakes") or []) if str(x).strip()]

    if not feature and lakes:
        raw = lakes[0]
        if "::" in raw:
            ver, rest = raw.split("::", 1)
            if ver.strip():
                version = ver.strip()
            feature = rest.strip()
        else:
            feature = raw

    # multi_version tagged lakes may leave feature as version::slug in feature field
    if "::" in feature:
        ver, rest = feature.split("::", 1)
        if ver.strip():
            version = ver.strip()
        feature = rest.strip()

    slug = feature_slug(feature) if feature else ""
    return {"version": version, "feature": feature, "feature_slug": slug}


def ensure_goal_implement_admission(
    project_root: Path,
    payload: dict[str, Any],
    *,
    dry_run: bool = False,
) -> dict[str, Any]:
    """Hard gate before goal implement write path.

    Returns allow_implement True only when workspace lane is admitted (or goal-forced)
    and merge-main did not conflict.
    """
    from beacon.utils.workspace_admission import (
        _merge_main_into_feature_branch,
        artifact_path,
        load_admission_contract,
        pool_state_path,
        run_workspace_admit,
        write_admission_artifact,
        _load_pool_state,
        _write_pool_state,
        _lease_holder,
        SCHEMA_VERSION as ADMIT_SCHEMA,
    )
    from beacon.utils.git_alignment import ensure_expected_worktree_lane, git_output
    from beacon.utils.branch_ref_hierarchy import leaf_feature_branch

    root = Path(project_root).expanduser().resolve()
    target = resolve_goal_implement_target(payload)
    version = target["version"]
    feature = target["feature"]
    slug = target["feature_slug"]

    base: dict[str, Any] = {
        "schema": SCHEMA,
        "version": version,
        "feature": feature,
        "feature_slug": slug,
        "allow_implement": False,
        "status": "blocked",
        "blocked": True,
        "reason_code": "",
        "admission": {},
        "goal_forced_worktree": False,
        "generated_at": now_iso(),
    }

    if not slug or version in {"", "auto"} and not feature:
        # version auto is ok if feature present — resolve later; feature required
        pass
    if not slug:
        base["reason_code"] = REASON_FEATURE_REQUIRED
        base["user_facing"] = "goal implement 需要 feature/lake slug 才能 workspace admit。"
        base["recommended_command"] = "beacon goal run \"...\" --feature <slug> 或 lakes=[...]"
        return base

    # Prefer real version string; if still auto, leave admit to resolve via governance
    admit_version = version if version and version != "auto" else str(payload.get("version") or "v1.6.9")

    admit = run_workspace_admit(
        root,
        version=admit_version,
        feature=slug,
        dry_run=dry_run,
    )
    base["admission"] = admit
    base["version"] = admit_version

    if dry_run:
        base["status"] = "ok" if admit.get("status") != "blocked" else "blocked"
        base["blocked"] = admit.get("status") == "blocked" or bool(admit.get("blocked"))
        base["allow_implement"] = not base["blocked"]
        base["reason_code"] = str(admit.get("reason_code") or ("dry_run_ok" if base["allow_implement"] else REASON_ADMIT_BLOCKED))
        return base

    if admit.get("status") == "blocked" or admit.get("blocked"):
        base["reason_code"] = str(admit.get("reason_code") or REASON_ADMIT_BLOCKED)
        base["reason_codes"] = list(admit.get("reason_codes") or [base["reason_code"]])
        base["user_facing"] = str(admit.get("summary") or "workspace admit blocked")
        base["recommended_command"] = (
            f"beacon workspace admit --project-root {root} --version {admit_version} --feature {slug} --json"
        )
        return base

    # Contract optional (skipped): goal still forces leaf worktree + merge-main (UD-GIA)
    skipped = bool(admit.get("skipped"))
    contract = load_admission_contract(root, version=admit_version)
    require = bool(contract.get("require_workspace_admission"))
    worktree_mode = str(contract.get("worktree_mode") or "")

    if skipped or not require:
        forced = _force_goal_worktree_lane(
            root,
            version=admit_version,
            feature=slug,
            contract=contract,
            merge_fn=_merge_main_into_feature_branch,
            ensure_lane=ensure_expected_worktree_lane,
            git_output=git_output,
            leaf_feature_branch=leaf_feature_branch,
            write_admission_artifact=write_admission_artifact,
            artifact_path=artifact_path,
            admit_schema=ADMIT_SCHEMA,
            pool_state_path=pool_state_path,
            load_pool=_load_pool_state,
            write_pool=_write_pool_state,
            lease_holder=_lease_holder,
        )
        base["goal_forced_worktree"] = True
        base["admission"] = {**admit, **forced, "goal_forced_worktree": True}
        if forced.get("status") == "blocked" or forced.get("blocked"):
            base["reason_code"] = str(forced.get("reason_code") or REASON_FORCE_WORKTREE_FAILED)
            base["reason_codes"] = list(forced.get("reason_codes") or [base["reason_code"]])
            base["user_facing"] = str(forced.get("summary") or "goal force worktree failed")
            return base
        admit = base["admission"]
    else:
        # require path already materialized + merged inside run_workspace_admit
        if admit.get("status") != "pass":
            base["reason_code"] = str(admit.get("reason_code") or REASON_ADMIT_BLOCKED)
            return base

    # Align parallel_plan satellite paths to admit-resolved worktree (single truth)
    worktree_path = str(admit.get("worktree_path") or "").strip()
    branch = str(admit.get("branch") or "").strip()
    base.update(
        {
            "status": "pass",
            "blocked": False,
            "allow_implement": True,
            "reason_code": "goal_implement_admission_ok",
            "worktree_path": worktree_path,
            "branch": branch,
            "cwd": str(admit.get("cwd") or worktree_path),
            "merge_main": admit.get("merge_main") or {},
            "pool_entry": admit.get("pool_entry"),
            "worktree_mode": worktree_mode or admit.get("admission_contract", {}).get("worktree_mode"),
            "worktree_attempt": admit.get("worktree_attempt"),
            "user_facing": "implement admission pass; cwd must be worktree_path",
        }
    )
    return base


def _force_goal_worktree_lane(
    root: Path,
    *,
    version: str,
    feature: str,
    contract: dict[str, Any],
    merge_fn: Any,
    ensure_lane: Any,
    git_output: Any,
    leaf_feature_branch: Any,
    write_admission_artifact: Any,
    artifact_path: Any,
    admit_schema: str,
    pool_state_path: Any,
    load_pool: Any,
    write_pool: Any,
    lease_holder: Any,
) -> dict[str, Any]:
    """When version contract does not require admit, goal still materializes leaf lane."""
    pattern = str(contract.get("feature_branch_pattern") or "").strip() or f"beacon/{version}/<feature-slug>"
    feature_branch = leaf_feature_branch(version=version, feature=feature, pattern=pattern)
    base_branch = str(
        contract.get("previous_version_baseline_branch")
        or contract.get("canonical_branch")
        or "main"
    ).strip() or "main"
    # Prefer contract worktree_base; else .beacon/worktrees/<version>/<slug>
    from beacon.utils.workspace_admission import resolve_worktree_path

    # Temporarily treat as dedicated for path resolution
    forced_contract = {
        **contract,
        "version": version,
        "worktree_mode": "dedicated-worktree",
        "feature_branch_pattern": pattern,
        "worktree_base": str(contract.get("worktree_base") or f".beacon/worktrees/{version}"),
    }
    # If base is repo root (branch-only), do not use root as worktree — use versioned path
    wb = str(forced_contract.get("worktree_base") or "")
    if wb in {"", ".", str(root)} or Path(wb).resolve() == root:
        forced_contract["worktree_base"] = f".beacon/worktrees/{version}"
    worktree_path = resolve_worktree_path(root, forced_contract, feature=feature)

    attempt = ensure_lane(
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
    }
    if attempt.get("status") not in {"created", "switched"}:
        out["status"] = "blocked"
        out["blocked"] = True
        out["reason_code"] = REASON_FORCE_WORKTREE_FAILED
        out["reason_codes"] = ["workspace_admission_worktree_failed", REASON_FORCE_WORKTREE_FAILED]
        out["summary"] = "goal force worktree create/switch failed"
        return out

    lane_root = Path(str(attempt.get("worktree_path") or worktree_path)).resolve()
    merge_main = merge_fn(lane_root, base_branch=base_branch)
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
        "schema_version": admit_schema,
        "version": version,
        "feature_slug": feature_slug(feature),
        "project_root": str(root),
        "branch": current_branch,
        "worktree_path": str(lane_root),
        "base_branch": base_branch,
        "issued_at": now_iso(),
        "git_head": git_head,
        "status": "pass",
        "goal_forced_worktree": True,
    }
    write_admission_artifact(artifact_file, artifact_payload)

    # Register pool when mode is pooled; for dedicated still ok to skip pool
    mode = str(contract.get("worktree_mode") or "")
    if mode == "pooled":
        pool_path = pool_state_path(root, version=version)
        pool_state, pool_error = load_pool(pool_path)
        if pool_error:
            out["status"] = "blocked"
            out["blocked"] = True
            out["reason_code"] = "workspace_pool_state_corrupt"
            return out
        assert pool_state is not None
        holder = lease_holder()
        entry = {
            "state": "leased",
            "feature_slug": feature_slug(feature),
            "branch": current_branch,
            "worktree_path": str(lane_root),
            "lease_holder": holder,
            "leased_at": now_iso(),
            "released_at": "",
            "git_head": git_head,
            "goal_forced_worktree": True,
        }
        pool_state.setdefault("entries", {})[feature_slug(feature)] = entry
        write_pool(pool_path, pool_state)
        out["pool_entry"] = entry
        out["pool_state_path"] = str(pool_path)

    out.update(
        {
            "branch": current_branch,
            "worktree_path": str(lane_root),
            "cwd": str(lane_root),
            "git_head": git_head,
            "artifact": artifact_payload,
            "summary": "goal forced worktree admission issued",
            "status": "pass",
        }
    )
    return out


def apply_admission_to_goal_payload(payload: dict[str, Any], gate: dict[str, Any]) -> dict[str, Any]:
    """Mutate goal payload with implement_admission + aligned satellite worktree paths."""
    payload["implement_admission"] = gate
    wt = str(gate.get("worktree_path") or "").strip()
    slug = str(gate.get("feature_slug") or "").strip()
    if wt and slug:
        pp = payload.get("parallel_plan") if isinstance(payload.get("parallel_plan"), dict) else {}
        sats = pp.get("satellites") if isinstance(pp.get("satellites"), list) else []
        for s in sats:
            if not isinstance(s, dict):
                continue
            lake = feature_slug(str(s.get("lake") or ""))
            if lake == slug or str(s.get("lake") or "") == slug:
                s["worktree"] = wt
                s["admitted"] = bool(gate.get("allow_implement"))
                s["branch"] = gate.get("branch")
        if sats:
            pp["satellites"] = sats
            payload["parallel_plan"] = pp
    # mark implement stage
    for item in payload.get("stages") or []:
        if isinstance(item, dict) and item.get("stage") == "implement":
            item["implement_admission"] = {
                "allow_implement": gate.get("allow_implement"),
                "reason_code": gate.get("reason_code"),
                "worktree_path": gate.get("worktree_path"),
                "branch": gate.get("branch"),
            }
            if gate.get("allow_implement"):
                item["cwd"] = gate.get("cwd") or gate.get("worktree_path")
    return payload
