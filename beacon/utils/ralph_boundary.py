"""Ralph implement-only boundary contract (v1.6.7 P2).

Ralph is an implement sub-controller. It must not own truth, QA verdict,
or release verdict authority. Product Goal may delegate implement rounds.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from beacon.utils.runtime import now_iso
from beacon.utils.story_state import feature_slug

SCHEMA_VERSION = "1.0"
IMPLEMENT_DELEGATE_RALPH = "ralph"

FORBIDDEN_AUTHORITY_FIELDS = (
    "qa_verdict",
    "release_verdict",
    "final_verdict",
    "product_complete",
    "product_goal_complete",
    "gate_truth",
)

ALLOWED_HANDOFF_ROUTES = frozenset(
    {
        "implement",
        "qa",
        "review_quality",
        "verify",
        "test-case",
        "human_review",
        "repair",
        "release",  # only as *route suggestion* to release check, not verdict
        "handoff_execute",
    }
)

REASON_FORBIDDEN_AUTHORITY = "ralph_forbidden_authority_field"
REASON_INVALID_HANDOFF = "ralph_invalid_handoff_route"


def ralph_boundary_contract() -> dict[str, Any]:
    return {
        "schema_version": SCHEMA_VERSION,
        "scope": "implement_mode_ralph_only",
        "may_write_truth": False,
        "may_issue_qa_verdict": False,
        "may_issue_release_verdict": False,
        "may_mark_product_complete": False,
        "finalize_means": "implement_closure_route_only",
        "product_complete_authority": "product_goal_done_when_plus_evaluator",
        "allowed_handoff_routes": sorted(ALLOWED_HANDOFF_ROUTES),
        "forbidden_authority_fields": list(FORBIDDEN_AUTHORITY_FIELDS),
        "goal_delegate_field": "implement_delegate",
        "goal_delegate_value": IMPLEMENT_DELEGATE_RALPH,
    }


def sanitize_ralph_state(state: dict[str, Any] | None) -> dict[str, Any]:
    """Remove or neutralize forbidden authority fields from ralph state."""
    payload = dict(state or {})
    stripped: list[str] = []
    for key in FORBIDDEN_AUTHORITY_FIELDS:
        if key in payload:
            stripped.append(key)
            if key in {"product_complete", "product_goal_complete"}:
                payload[key] = False
            else:
                payload.pop(key, None)
    # Explicit non-authority markers
    payload["may_issue_qa_verdict"] = False
    payload["may_issue_release_verdict"] = False
    payload["may_mark_product_complete"] = False
    payload["ralph_finalize_is_product_complete"] = False
    payload["boundary"] = ralph_boundary_contract()
    if stripped:
        payload["stripped_authority_fields"] = stripped
    # Normalize handoff/next_action
    next_action = str(payload.get("next_action") or "").strip()
    if next_action and next_action not in ALLOWED_HANDOFF_ROUTES:
        payload["invalid_next_action"] = next_action
        payload["next_action"] = "human_review"
        payload["reason_code"] = REASON_INVALID_HANDOFF
    return payload


def enforce_ralph_state_file(project_root: Path, *, feature: str) -> dict[str, Any]:
    from beacon.utils.ralph_runtime import load_ralph_state, save_ralph_state

    state = load_ralph_state(project_root, feature=feature)
    if not state:
        return {"status": "empty", "feature": feature_slug(feature), "blocked": False}
    cleaned = sanitize_ralph_state(state)
    cleaned["updated_at"] = now_iso()
    # write cleaned without re-entering save_ralph_state sanitize loop issues
    save_ralph_state(project_root, feature=feature, payload=cleaned)
    return {
        "status": "pass",
        "blocked": False,
        "feature": feature_slug(feature),
        "stripped_authority_fields": cleaned.get("stripped_authority_fields") or [],
        "state": cleaned,
    }


def validate_handoff_route(route: str) -> dict[str, Any]:
    action = str(route or "").strip().lower()
    ok = action in ALLOWED_HANDOFF_ROUTES
    return {
        "route": action,
        "allowed": ok,
        "blocked": not ok,
        "status": "pass" if ok else "blocked",
        "reason_code": "" if ok else REASON_INVALID_HANDOFF,
        "allowed_set": sorted(ALLOWED_HANDOFF_ROUTES),
    }


def skill_boundary_text_ok(text: str) -> dict[str, Any]:
    lowered = str(text or "").lower()
    checks = {
        "mentions_implement_only": any(
            token in lowered
            for token in ("implement", "closure controller", "子控制器", "implement-only", "mode ralph", "mode=ralph")
        ),
        "forbids_qa_release_truth": any(
            token in lowered
            for token in (
                "never replaces qa",
                "不得替代",
                "不得写 truth",
                "does not replace qa",
                "never replaces",
                "不得发 qa",
                "不得作为 product goal",
                "≠ product complete",
                "not product complete",
                "frozen truth",
            )
        ),
        "has_boundary_section": "boundary" in lowered or "边界" in lowered,
    }
    ok = all(checks.values())
    return {"status": "pass" if ok else "blocked", "checks": checks, "blocked": not ok}
