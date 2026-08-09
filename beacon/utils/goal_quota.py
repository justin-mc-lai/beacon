"""Goal compute quota kernel (LoopX distillation; CAP-1 of beacon-goal-loopx-hybrid-v1612).

Borrowed semantics (interface alignment, not code): quota should-run decision
order, spend-once after validated writeback, and the two-boolean contract
("may ordinary delivery continue" vs "is there a bounded recovery action")
from LoopX quota / outcome-floor lessons.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

QUOTA_SCHEMA = "goal-quota.v1"


def normalize_quota_config(config: dict[str, Any] | None) -> dict[str, Any]:
    cfg = dict(config or {})
    compute = float(cfg.get("compute", 1.0))
    window_hours = int(cfg.get("window_hours", 24))
    slot_minutes = int(cfg.get("slot_minutes", 1))
    allowed = int(cfg.get("allowed_slots") or 0)
    if allowed <= 0:
        allowed = int(window_hours * 60 / max(slot_minutes, 1) * compute)
    return {
        "compute": compute,
        "window_hours": window_hours,
        "slot_minutes": slot_minutes,
        "allowed_slots": allowed,
    }


def spent_slots(state: dict[str, Any]) -> int:
    ledger = state.get("quota_ledger") or []
    return sum(int(entry.get("slots") or 0) for entry in ledger if isinstance(entry, dict))


def quota_should_run(
    state: dict[str, Any],
    *,
    config: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Decide whether an automatic goal turn may run (AC-001).

    Order: health -> operator gate -> evidence wait -> focus wait -> quota.
    Recovery actions are reported on a separate boolean; a skip never looks
    like a run and a recovery never looks like a quiet skip.
    """
    cfg = normalize_quota_config(config)
    gates = (
        ("health_blocked", "health_blocked"),
        ("operator_gate_open", "operator_gate_open"),
        ("evidence_wait", "evidence_wait"),
        ("focus_wait", "focus_wait"),
    )
    for key, reason in gates:
        if bool(state.get(key)):
            return {
                "schema": QUOTA_SCHEMA,
                "should_run": False,
                "decision": "skip",
                "state": reason,
                "reason_code": reason,
                "recovery_action": bool(state.get("recovery_action")),
                "recovery_kind": str(state.get("recovery_kind") or ""),
                "scheduler_hint": str(state.get("scheduler_hint") or ""),
                "spent_slots": spent_slots(state),
                "allowed_slots": cfg["allowed_slots"],
            }
    used = spent_slots(state)
    eligible = used < cfg["allowed_slots"]
    return {
        "schema": QUOTA_SCHEMA,
        "should_run": eligible,
        "decision": "run" if eligible else "quota_exhausted",
        "state": "quota_eligible" if eligible else "quota_exhausted",
        "reason_code": "" if eligible else "quota_exhausted",
        "recovery_action": False,
        "recovery_kind": "",
        "scheduler_hint": str(state.get("scheduler_hint") or ""),
        "spent_slots": used,
        "allowed_slots": cfg["allowed_slots"],
    }


def record_spend(
    state: dict[str, Any],
    *,
    slots: int = 1,
    writeback_validated: bool = False,
) -> dict[str, Any]:
    """Spend exactly once after a validated writeback; otherwise refuse (AC-001)."""
    if not writeback_validated:
        return {
            "schema": QUOTA_SCHEMA,
            "ok": False,
            "blocked": True,
            "reason_code": "spend_without_validated_writeback",
            "spent_slots": spent_slots(state),
        }
    ledger = list(state.get("quota_ledger") or [])
    ledger.append(
        {
            "slots": max(1, int(slots)),
            "at": datetime.now(timezone.utc).isoformat(),
        }
    )
    return {
        "schema": QUOTA_SCHEMA,
        "ok": True,
        "blocked": False,
        "reason_code": "",
        "spent_slots": sum(int(entry.get("slots") or 0) for entry in ledger),
        "ledger": ledger,
    }
