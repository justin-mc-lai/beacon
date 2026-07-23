"""Goal implement admission hard gate (Scheme A / UD-GIA).

v1.6.10+: delegates policy to shared ``ensure_implement_admission`` so goal,
direct, team, and ralph share one fail-closed pre-write invariant.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from beacon.utils.runtime import now_iso
from beacon.utils.story_state import feature_slug
from beacon.utils.goal_reason_codes import FREEZE_ACK_REQUIRED

SCHEMA = "goal-implement-admission.v1"
REASON_FEATURE_REQUIRED = "goal_implement_feature_required"
REASON_ADMIT_BLOCKED = "goal_implement_admission_blocked"
REASON_FORCE_WORKTREE_FAILED = "goal_implement_force_worktree_failed"
REASON_ENF_ADMISSION = "goal_implement_admission_required"  # UD-ENF-003
REASON_FREEZE_ACK = FREEZE_ACK_REQUIRED  # Decision A: fill ≠ self-sign
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
    """Hard gate before goal implement write path — shared implement admission."""
    from beacon.utils.implement_admission import ensure_goal_compatible_admission

    root = Path(project_root).expanduser().resolve()
    target = resolve_goal_implement_target(payload)
    if not target["feature_slug"]:
        return {
            "schema": SCHEMA,
            "version": target["version"],
            "feature": target["feature"],
            "feature_slug": "",
            "allow_implement": False,
            "status": "blocked",
            "blocked": True,
            "reason_code": REASON_FEATURE_REQUIRED,
            "admission": {},
            "goal_forced_worktree": False,
            "generated_at": now_iso(),
            "user_facing": "goal implement 需要 feature/lake slug 才能 workspace admit。",
            "recommended_command": "beacon goal run \"...\" --feature <slug> 或 lakes=[...]",
        }

    gate = ensure_goal_compatible_admission(root, payload, dry_run=dry_run)
    # Normalize legacy reason codes for existing goal tests/consumers
    reason = str(gate.get("reason_code") or "")
    if reason == "implement_admission_feature_required":
        gate["reason_code"] = REASON_FEATURE_REQUIRED
    elif reason in {"implement_admission_force_worktree_failed", "soft_skip_write_authorization_forbidden"}:
        gate["reason_code"] = REASON_FORCE_WORKTREE_FAILED
    elif reason == "implement_admission_blocked":
        gate["reason_code"] = REASON_ADMIT_BLOCKED
    elif reason == "freeze_ack_required":
        gate["reason_code"] = REASON_FREEZE_ACK
    gate["schema"] = SCHEMA
    return gate


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
                if gate.get("service_worktree_map"):
                    s["service_worktree_map"] = gate.get("service_worktree_map")
        if sats:
            pp["satellites"] = sats
            payload["parallel_plan"] = pp
    for item in payload.get("stages") or []:
        if isinstance(item, dict) and item.get("stage") == "implement":
            item["implement_admission"] = {
                "allow_implement": gate.get("allow_implement"),
                "reason_code": gate.get("reason_code"),
                "worktree_path": gate.get("worktree_path"),
                "branch": gate.get("branch"),
                "service_worktree_map": gate.get("service_worktree_map") or {},
            }
            if gate.get("allow_implement"):
                item["cwd"] = gate.get("cwd") or gate.get("worktree_path")
    return payload
