"""Stable reason_code taxonomy for goal hard gates (English snake_case).

Agents/UI may localize user_facing text; reason_code strings are API-stable.
"""

from __future__ import annotations

from typing import Final

# --- stage exit (tick cannot mark stage done) ---
STAGE_EXIT_OK: Final = "stage_exit_ok"
STAGE_EXIT_PLAN_INCOMPLETE: Final = "stage_exit_plan_incomplete"
STAGE_EXIT_TRUTH_NOT_FROZEN: Final = "stage_exit_truth_not_frozen"
STAGE_EXIT_TRUTH_MISSING: Final = "stage_exit_truth_package_missing"
STAGE_EXIT_DESIGN_INCOMPLETE: Final = "stage_exit_design_incomplete"
STAGE_EXIT_IMPLEMENT_BLOCKED: Final = "stage_exit_implement_blocked"
STAGE_EXIT_QA_EVIDENCE_MISSING: Final = "stage_exit_qa_evidence_missing"
STAGE_EXIT_RELEASE_HUMAN: Final = "release_requires_human_confirmation"
STAGE_EXIT_BLOCKED: Final = "stage_exit_blocked"

# --- implement admission ---
FREEZE_ACK_REQUIRED: Final = "freeze_ack_required"
GOAL_IMPLEMENT_FEATURE_REQUIRED: Final = "goal_implement_feature_required"
GOAL_IMPLEMENT_ADMISSION_BLOCKED: Final = "goal_implement_admission_blocked"
GOAL_IMPLEMENT_ADMISSION_OK: Final = "goal_implement_admission_ok"

# --- main write path ---
MAIN_IMPLEMENT_FORBIDDEN: Final = "main_implement_forbidden"
MAIN_DOCS_POLICY_FORBIDDEN: Final = "main_docs_policy_forbidden"
MAIN_IMPLEMENT_EXCEPTION_ALLOWED: Final = "main_implement_exception_allowed"

# resume_action values (not reason codes, listed for contract tests)
RESUME_NONE: Final = "none"
RESUME_LOAD_NEXT: Final = "load_next_skill"
RESUME_AWAIT_FREEZE: Final = "await_freeze_ack"
RESUME_AWAIT_RELEASE: Final = "await_human_release"

REASON_CATALOG: Final[dict[str, str]] = {
    STAGE_EXIT_OK: "Stage exit verifier passed",
    STAGE_EXIT_PLAN_INCOMPLETE: "Plan/journey incomplete; cannot leave plan",
    STAGE_EXIT_TRUTH_NOT_FROZEN: "Feature truth exists but status is not frozen",
    STAGE_EXIT_TRUTH_MISSING: "Feature truth package missing; fill then freeze",
    STAGE_EXIT_DESIGN_INCOMPLETE: "Design stage lacks verifiable design evidence",
    STAGE_EXIT_IMPLEMENT_BLOCKED: "Implement admission failed",
    STAGE_EXIT_QA_EVIDENCE_MISSING: "QA lacks scorecard/evidence artifact",
    STAGE_EXIT_RELEASE_HUMAN: "Release requires human confirmation",
    FREEZE_ACK_REQUIRED: "Freeze ack required before implement (fill ≠ self-sign)",
    MAIN_IMPLEMENT_FORBIDDEN: "Business path commit on main/master forbidden",
    MAIN_DOCS_POLICY_FORBIDDEN: "Docs path outside allowed main docs policy",
}


def is_known_reason(code: str) -> bool:
    return str(code or "") in REASON_CATALOG or str(code or "").startswith(
        ("stage_exit_", "goal_implement_", "main_", "freeze_", "release_")
    )
