"""Goal loop readiness score (LoopX ready-score distillation; CAP-5).

Checks whether a goal loop is safe to run repeatedly: frozen truth, workspace
admission, quota configured, and fresh evidence. Blocked checks are concrete,
not a vague "not ready".
"""

from __future__ import annotations

from typing import Any

READY_SCHEMA = "goal-ready-score.v1"


def goal_ready_score(state: dict[str, Any]) -> dict[str, Any]:
    checks = {
        "truth_frozen": bool(state.get("truth_frozen")),
        "workspace_admission": bool(state.get("workspace_admission")),
        "quota_configured": bool(
            state.get("quota_configured")
            or state.get("quota_config")
            or state.get("quota_enabled")
        ),
        "evidence_fresh": bool(state.get("evidence_fresh")),
    }
    blocked = [name for name, ok in checks.items() if not ok]
    return {
        "schema": READY_SCHEMA,
        "ready": not blocked,
        "blocked_checks": blocked,
        "checks": checks,
    }
